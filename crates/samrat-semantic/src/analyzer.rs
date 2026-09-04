use samrat_parser::ast::*;
use crate::symbol::{Symbol, SymbolTable};
use crate::types::Type;
use thiserror::Error;

#[derive(Error, Debug, PartialEq)]
pub enum SemanticError {
    #[error("Undefined symbol '{0}'")]
    UndefinedSymbol(String),
    #[error("Redeclared symbol '{0}'")]
    RedeclaredSymbol(String),
    #[error("Type mismatch: expected {0}, found {1}")]
    TypeMismatch(String, String),
}

pub struct SemanticAnalyzer {
    symbols: SymbolTable,
}

impl SemanticAnalyzer {
    pub fn new() -> Self {
        let mut symbols = SymbolTable::new();
        // Built-in functions
        symbols.insert(Symbol {
            name: "print".to_string(),
            ty: Type::Function {
                params: vec![Type::Unknown],
                return_type: Box::new(Type::Void),
            },
            is_mutable: false,
        });
        Self { symbols }
    }

    pub fn analyze(&mut self, program: &Program) -> Result<(), SemanticError> {
        for stmt in &program.statements {
            self.analyze_statement(stmt)?;
        }
        Ok(())
    }

    fn analyze_statement(&mut self, stmt: &Statement) -> Result<(), SemanticError> {
        match stmt {
            Statement::Entrypoint(body) => {
                self.symbols.enter_scope();
                for s in body {
                    self.analyze_statement(s)?;
                }
                self.symbols.exit_scope();
            }
            Statement::CreateRangePipeline { variable, start, end, .. } => {
                let start_ty = self.infer_expression(start)?;
                let end_ty = self.infer_expression(end)?;
                if start_ty != Type::Int || end_ty != Type::Int {
                    return Err(SemanticError::TypeMismatch("Integer".to_string(), format!("{} and {}", start_ty, end_ty)));
                }
                self.symbols.insert(Symbol {
                    name: variable.clone(),
                    ty: Type::Int,
                    is_mutable: false,
                });
            }
            Statement::VariableDeclaration { name, value, .. } => {
                let val_ty = self.infer_expression(value)?;
                if !self.symbols.insert(Symbol {
                    name: name.clone(),
                    ty: val_ty,
                    is_mutable: true,
                }) {
                    return Err(SemanticError::RedeclaredSymbol(name.clone()));
                }
            }
            Statement::Assignment { target, value } => {
                let sym_ty = self.symbols.lookup(target)
                    .ok_or_else(|| SemanticError::UndefinedSymbol(target.clone()))?.ty.clone();
                let val_ty = self.infer_expression(value)?;
                if sym_ty != Type::Unknown && val_ty != Type::Unknown && sym_ty != val_ty {
                    return Err(SemanticError::TypeMismatch(sym_ty.to_string(), val_ty.to_string()));
                }
            }
            Statement::Print(expr) => {
                self.infer_expression(expr)?;
            }
            Statement::If { condition, then_branch, else_branch } => {
                let cond_ty = self.infer_expression(condition)?;
                if cond_ty != Type::Bool && cond_ty != Type::Unknown {
                    return Err(SemanticError::TypeMismatch("Boolean".to_string(), cond_ty.to_string()));
                }
                self.symbols.enter_scope();
                for s in then_branch {
                    self.analyze_statement(s)?;
                }
                self.symbols.exit_scope();

                if let Some(else_stmts) = else_branch {
                    self.symbols.enter_scope();
                    for s in else_stmts {
                        self.analyze_statement(s)?;
                    }
                    self.symbols.exit_scope();
                }
            }
            Statement::While { condition, body } => {
                let cond_ty = self.infer_expression(condition)?;
                if cond_ty != Type::Bool && cond_ty != Type::Unknown {
                    return Err(SemanticError::TypeMismatch("Boolean".to_string(), cond_ty.to_string()));
                }
                self.symbols.enter_scope();
                for s in body {
                    self.analyze_statement(s)?;
                }
                self.symbols.exit_scope();
            }
            Statement::For { variable, iterable, body } => {
                let _iter_ty = self.infer_expression(iterable)?;
                self.symbols.enter_scope();
                self.symbols.insert(Symbol {
                    name: variable.clone(),
                    ty: Type::Int,
                    is_mutable: false,
                });
                for s in body {
                    self.analyze_statement(s)?;
                }
                self.symbols.exit_scope();
            }
            Statement::FunctionDeclaration { name, parameters, body, .. } => {
                self.symbols.insert(Symbol {
                    name: name.clone(),
                    ty: Type::Function {
                        params: vec![Type::Unknown; parameters.len()],
                        return_type: Box::new(Type::Unknown),
                    },
                    is_mutable: false,
                });
                self.symbols.enter_scope();
                for p in parameters {
                    self.symbols.insert(Symbol {
                        name: p.clone(),
                        ty: Type::Unknown,
                        is_mutable: true,
                    });
                }
                for s in body {
                    self.analyze_statement(s)?;
                }
                self.symbols.exit_scope();
            }
            Statement::Return(Some(expr)) => {
                self.infer_expression(expr)?;
            }
            Statement::Return(None) => {}
            Statement::Expression(expr) => {
                self.infer_expression(expr)?;
            }
        }
        Ok(())
    }

    fn infer_expression(&mut self, expr: &Expression) -> Result<Type, SemanticError> {
        match expr {
            Expression::Integer(_) => Ok(Type::Int),
            Expression::Float(_) => Ok(Type::Float),
            Expression::StringLiteral(_) => Ok(Type::String),
            Expression::Boolean(_) => Ok(Type::Bool),
            Expression::Null => Ok(Type::Null),
            Expression::Variable(name) => {
                let sym = self.symbols.lookup(name)
                    .ok_or_else(|| SemanticError::UndefinedSymbol(name.clone()))?;
                Ok(sym.ty.clone())
            }
            Expression::BinaryOp { left, op, right } => {
                let l_ty = self.infer_expression(left)?;
                let r_ty = self.infer_expression(right)?;
                match op {
                    BinaryOperator::Add | BinaryOperator::Subtract | BinaryOperator::Multiply | BinaryOperator::Divide | BinaryOperator::Modulo => {
                        if l_ty == Type::Float || r_ty == Type::Float {
                            Ok(Type::Float)
                        } else {
                            Ok(Type::Int)
                        }
                    }
                    BinaryOperator::Equal | BinaryOperator::NotEqual | BinaryOperator::LessThan | BinaryOperator::GreaterThan | BinaryOperator::LessEqual | BinaryOperator::GreaterEqual => {
                        Ok(Type::Bool)
                    }
                    BinaryOperator::And | BinaryOperator::Or => Ok(Type::Bool),
                }
            }
            Expression::UnaryOp { op, expr } => {
                let ty = self.infer_expression(expr)?;
                match op {
                    UnaryOperator::Negate => Ok(ty),
                    UnaryOperator::Not => Ok(Type::Bool),
                }
            }
            Expression::FunctionCall { callee, arguments } => {
                for arg in arguments {
                    self.infer_expression(arg)?;
                }
                let sym = self.symbols.lookup(callee)
                    .ok_or_else(|| SemanticError::UndefinedSymbol(callee.clone()))?;
                if let Type::Function { return_type, .. } = &sym.ty {
                    Ok(*return_type.clone())
                } else {
                    Ok(Type::Unknown)
                }
            }
            Expression::Range { start, end } => {
                self.infer_expression(start)?;
                self.infer_expression(end)?;
                Ok(Type::Array(Box::new(Type::Int)))
            }
            Expression::ArrayLiteral(elems) => {
                if let Some(first) = elems.first() {
                    let elem_ty = self.infer_expression(first)?;
                    Ok(Type::Array(Box::new(elem_ty)))
                } else {
                    Ok(Type::Array(Box::new(Type::Unknown)))
                }
            }
        }
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    use samrat_lexer::Lexer;
    use samrat_parser::Parser;

    #[test]
    fn test_semantic_analysis_valid_sentence() {
        let input = "When the program starts, create numbers from 1 to 100, keep the even numbers, add them together, and show the total.";
        let mut lexer = Lexer::new(input);
        let tokens = lexer.tokenize().unwrap();
        let mut parser = Parser::new(tokens);
        let ast = parser.parse().unwrap();

        let mut analyzer = SemanticAnalyzer::new();
        assert!(analyzer.analyze(&ast).is_ok());
    }
}
