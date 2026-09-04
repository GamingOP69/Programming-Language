use samrat_parser::ast::*;
use crate::ir::*;

pub struct IrBuilder {
    temp_counter: usize,
    label_counter: usize,
}

impl IrBuilder {
    pub fn new() -> Self {
        Self {
            temp_counter: 0,
            label_counter: 0,
        }
    }

    fn new_temp(&mut self) -> String {
        self.temp_counter += 1;
        format!("t{}", self.temp_counter)
    }

    fn new_label(&mut self, prefix: &str) -> String {
        self.label_counter += 1;
        format!("{}_{}", prefix, self.label_counter)
    }

    pub fn build_module(&mut self, program: &Program) -> IrModule {
        let mut main_instructions = Vec::new();

        for stmt in &program.statements {
            self.build_statement(stmt, &mut main_instructions);
        }

        let main_fn = IrFunction {
            name: "main".to_string(),
            params: vec![],
            return_type: IrType::I64,
            instructions: main_instructions,
        };

        IrModule {
            functions: vec![main_fn],
        }
    }

    fn build_statement(&mut self, stmt: &Statement, instrs: &mut Vec<IrInstruction>) {
        match stmt {
            Statement::Entrypoint(body) => {
                for s in body {
                    self.build_statement(s, instrs);
                }
            }
            Statement::CreateRangePipeline { variable: _, start, end, filter_even, sum, show_total: _ } => {
                let start_val = match start {
                    Expression::Integer(i) => *i,
                    _ => 1,
                };
                let end_val = match end {
                    Expression::Integer(i) => *i,
                    _ => 100,
                };
                let res_var = self.new_temp();
                instrs.push(IrInstruction::CreateRangePipeline {
                    start: start_val,
                    end: end_val,
                    filter_even: *filter_even,
                    sum: *sum,
                    dest: res_var.clone(),
                });
                instrs.push(IrInstruction::Print { value: IrValue::Variable(res_var) });
            }
            Statement::VariableDeclaration { name, value, .. } => {
                instrs.push(IrInstruction::Alloca { dest: name.clone(), ty: IrType::I64 });
                let val = self.build_expression(value, instrs);
                instrs.push(IrInstruction::Store { src: val, dest: name.clone() });
            }
            Statement::Print(expr) => {
                let val = self.build_expression(expr, instrs);
                instrs.push(IrInstruction::Print { value: val });
            }
            Statement::If { condition, then_branch, else_branch } => {
                let cond_val = self.build_expression(condition, instrs);
                let then_lbl = self.new_label("then");
                let else_lbl = self.new_label("else");
                let merge_lbl = self.new_label("merge");

                instrs.push(IrInstruction::JumpIf {
                    condition: cond_val,
                    then_target: then_lbl.clone(),
                    else_target: if else_branch.is_some() { else_lbl.clone() } else { merge_lbl.clone() },
                });

                instrs.push(IrInstruction::Label { name: then_lbl });
                for s in then_branch {
                    self.build_statement(s, instrs);
                }
                instrs.push(IrInstruction::Jump { target: merge_lbl.clone() });

                if let Some(else_stmts) = else_branch {
                    instrs.push(IrInstruction::Label { name: else_lbl });
                    for s in else_stmts {
                        self.build_statement(s, instrs);
                    }
                    instrs.push(IrInstruction::Jump { target: merge_lbl.clone() });
                }

                instrs.push(IrInstruction::Label { name: merge_lbl });
            }
            Statement::Return(Some(expr)) => {
                let val = self.build_expression(expr, instrs);
                instrs.push(IrInstruction::Return { value: Some(val) });
            }
            Statement::Return(None) => {
                instrs.push(IrInstruction::Return { value: None });
            }
            _ => {}
        }
    }

    fn build_expression(&mut self, expr: &Expression, instrs: &mut Vec<IrInstruction>) -> IrValue {
        match expr {
            Expression::Integer(i) => IrValue::ConstantInt(*i),
            Expression::Float(f) => IrValue::ConstantFloat(*f),
            Expression::Boolean(b) => IrValue::ConstantBool(*b),
            Expression::Variable(name) => {
                let temp = self.new_temp();
                instrs.push(IrInstruction::Load { dest: temp.clone(), src: name.clone() });
                IrValue::Variable(temp)
            }
            Expression::BinaryOp { left, op, right } => {
                let l = self.build_expression(left, instrs);
                let r = self.build_expression(right, instrs);
                let temp = self.new_temp();
                match op {
                    BinaryOperator::Add => instrs.push(IrInstruction::Add { dest: temp.clone(), left: l, right: r }),
                    BinaryOperator::Subtract => instrs.push(IrInstruction::Sub { dest: temp.clone(), left: l, right: r }),
                    BinaryOperator::Multiply => instrs.push(IrInstruction::Mul { dest: temp.clone(), left: l, right: r }),
                    BinaryOperator::Divide => instrs.push(IrInstruction::Div { dest: temp.clone(), left: l, right: r }),
                    BinaryOperator::Modulo => instrs.push(IrInstruction::Mod { dest: temp.clone(), left: l, right: r }),
                    BinaryOperator::Equal => instrs.push(IrInstruction::CmpEq { dest: temp.clone(), left: l, right: r }),
                    BinaryOperator::NotEqual => instrs.push(IrInstruction::CmpNe { dest: temp.clone(), left: l, right: r }),
                    BinaryOperator::LessThan => instrs.push(IrInstruction::CmpLt { dest: temp.clone(), left: l, right: r }),
                    BinaryOperator::GreaterThan => instrs.push(IrInstruction::CmpGt { dest: temp.clone(), left: l, right: r }),
                    _ => {}
                }
                IrValue::Variable(temp)
            }
            _ => IrValue::ConstantInt(0),
        }
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    use samrat_lexer::Lexer;
    use samrat_parser::Parser;

    #[test]
    fn test_ir_build() {
        let input = "When the program starts, create numbers from 1 to 100, keep the even numbers, add them together, and show the total.";
        let mut lexer = Lexer::new(input);
        let tokens = lexer.tokenize().unwrap();
        let mut parser = Parser::new(tokens);
        let ast = parser.parse().unwrap();

        let mut builder = IrBuilder::new();
        let ir = builder.build_module(&ast);
        assert_eq!(ir.functions.len(), 1);
        assert!(!ir.functions[0].instructions.is_empty());
    }
}
