use crate::ast::*;
use samrat_lexer::{Token, TokenType};
use thiserror::Error;

#[derive(Error, Debug, PartialEq)]
pub enum ParserError {
    #[error("Unexpected token '{0}' at line {1}, column {2}")]
    UnexpectedToken(String, usize, usize),
    #[error("Expected token '{0}', found '{1}' at line {2}, column {3}")]
    ExpectedToken(String, String, usize, usize),
    #[error("Unexpected end of input")]
    UnexpectedEof,
}

pub struct Parser {
    tokens: Vec<Token>,
    current: usize,
}

impl Parser {
    pub fn new(tokens: Vec<Token>) -> Self {
        Self { tokens, current: 0 }
    }

    fn peek(&self) -> &Token {
        if self.current < self.tokens.len() {
            &self.tokens[self.current]
        } else {
            self.tokens.last().unwrap()
        }
    }

    fn previous(&self) -> &Token {
        &self.tokens[self.current - 1]
    }

    fn is_at_end(&self) -> bool {
        self.peek().token_type == TokenType::Eof
    }

    fn advance(&mut self) -> &Token {
        if !self.is_at_end() {
            self.current += 1;
        }
        self.previous()
    }

    fn check(&self, token_type: &TokenType) -> bool {
        if self.is_at_end() {
            return false;
        }
        &self.peek().token_type == token_type
    }

    fn match_token(&mut self, token_types: &[TokenType]) -> bool {
        for t in token_types {
            if self.check(t) {
                self.advance();
                return true;
            }
        }
        false
    }

    fn consume(&mut self, token_type: &TokenType, message: &str) -> Result<&Token, ParserError> {
        if self.check(token_type) {
            Ok(self.advance())
        } else {
            let tok = self.peek();
            Err(ParserError::ExpectedToken(
                message.to_string(),
                tok.lexeme.clone(),
                tok.line,
                tok.column,
            ))
        }
    }

    fn skip_separators(&mut self) {
        while self.match_token(&[
            TokenType::Newline,
            TokenType::Period,
            TokenType::Comma,
            TokenType::Semicolon,
        ]) {}
    }

    pub fn parse(&mut self) -> Result<Program, ParserError> {
        let mut statements = Vec::new();
        self.skip_separators();

        while !self.is_at_end() {
            let stmt = self.parse_statement()?;
            statements.push(stmt);
            self.skip_separators();
        }

        Ok(Program { statements })
    }

    fn parse_statement(&mut self) -> Result<Statement, ParserError> {
        self.skip_separators();

        if self.check(&TokenType::When) {
            self.parse_entrypoint_or_pipeline()
        } else if self.match_token(&[TokenType::Create]) {
            self.parse_create_statement()
        } else if self.match_token(&[TokenType::Show, TokenType::Print]) {
            let expr = self.parse_expression()?;
            Ok(Statement::Print(expr))
        } else if self.match_token(&[TokenType::If]) {
            self.parse_if_statement()
        } else if self.match_token(&[TokenType::While]) {
            self.parse_while_statement()
        } else if self.match_token(&[TokenType::For]) {
            self.parse_for_statement()
        } else if self.match_token(&[TokenType::Define]) {
            self.parse_function_statement()
        } else if self.match_token(&[TokenType::Return]) {
            if self.check(&TokenType::Newline)
                || self.check(&TokenType::Period)
                || self.check(&TokenType::Semicolon)
            {
                Ok(Statement::Return(None))
            } else {
                let expr = self.parse_expression()?;
                Ok(Statement::Return(Some(expr)))
            }
        } else {
            let expr = self.parse_expression()?;
            Ok(Statement::Expression(expr))
        }
    }

    fn parse_entrypoint_or_pipeline(&mut self) -> Result<Statement, ParserError> {
        self.consume(&TokenType::When, "when")?;
        self.consume(&TokenType::The, "the")?;
        self.consume(&TokenType::Program, "program")?;
        self.consume(&TokenType::Starts, "starts")?;

        if self.match_token(&[TokenType::Comma, TokenType::Colon]) {
            self.skip_separators();
        }

        // Check if conversational range pipeline construct follows
        if self.check(&TokenType::Create) {
            self.advance(); // consume Create
            if self.match_keyword_or_ident("numbers") || self.match_keyword_or_ident("number") {
                let var_name = "numbers".to_string();
                self.consume(&TokenType::From, "from")?;
                let start = self.parse_expression()?;
                self.consume(&TokenType::To, "to")?;
                let end = self.parse_expression()?;

                let mut filter_even = false;
                let mut sum = false;
                let mut show_total = false;

                if self.match_token(&[TokenType::Comma]) {
                    self.skip_separators();
                }

                if self.match_token(&[TokenType::Keep]) {
                    self.consume(&TokenType::The, "the")?;
                    if self.match_token(&[TokenType::Even]) {
                        filter_even = true;
                    }
                    if self.match_keyword_or_ident("numbers") {
                        // skip optional 'numbers' keyword
                    }
                }

                if self.match_token(&[TokenType::Comma]) {
                    self.skip_separators();
                }

                if self.match_keyword_or_ident("and") {
                    // skip optional 'and'
                }

                if self.match_token(&[TokenType::Add])
                    && self.match_token(&[TokenType::Them])
                    && self.match_token(&[TokenType::Together])
                {
                    sum = true;
                }

                if self.match_token(&[TokenType::Comma]) {
                    self.skip_separators();
                }

                if self.match_keyword_or_ident("and") {
                    // skip optional 'and'
                }

                if self.match_token(&[TokenType::Show, TokenType::Print]) {
                    self.consume(&TokenType::The, "the")?;
                    if self.match_token(&[TokenType::Total]) {
                        show_total = true;
                    }
                }

                return Ok(Statement::CreateRangePipeline {
                    variable: var_name,
                    start,
                    end,
                    filter_even,
                    sum,
                    show_total,
                });
            }
        }

        // Standard entrypoint block containing statements
        let mut inner_statements = Vec::new();
        while !self.is_at_end() && !self.check(&TokenType::RBrace) {
            inner_statements.push(self.parse_statement()?);
            self.skip_separators();
        }

        Ok(Statement::Entrypoint(inner_statements))
    }

    fn match_keyword_or_ident(&mut self, expected: &str) -> bool {
        if expected.eq_ignore_ascii_case("and") && self.check(&TokenType::And) {
            self.advance();
            return true;
        }
        if expected.eq_ignore_ascii_case("or") && self.check(&TokenType::Or) {
            self.advance();
            return true;
        }
        if let TokenType::Identifier(id) = &self.peek().token_type {
            if id.eq_ignore_ascii_case(expected) {
                self.advance();
                return true;
            }
        }
        false
    }

    fn parse_create_statement(&mut self) -> Result<Statement, ParserError> {
        let mut _type_annotation = None;
        if self.match_keyword_or_ident("variable")
            || self.match_keyword_or_ident("a")
            || self.match_keyword_or_ident("number")
        {
            // Optional descriptive words
        }

        let name_tok = self.advance();
        let var_name = match &name_tok.token_type {
            TokenType::Identifier(id) => id.clone(),
            _ => name_tok.lexeme.clone(),
        };

        let mut val = Expression::Null;
        if self.match_token(&[TokenType::Set, TokenType::To, TokenType::Equal]) {
            val = self.parse_expression()?;
        }

        Ok(Statement::VariableDeclaration {
            name: var_name,
            value: val,
            type_annotation: _type_annotation,
        })
    }

    fn parse_if_statement(&mut self) -> Result<Statement, ParserError> {
        let cond = self.parse_expression()?;
        if self.match_token(&[TokenType::Then]) {
            self.skip_separators();
        }

        let mut then_branch = Vec::new();
        if self.match_token(&[TokenType::LBrace]) {
            while !self.check(&TokenType::RBrace) && !self.is_at_end() {
                then_branch.push(self.parse_statement()?);
                self.skip_separators();
            }
            self.consume(&TokenType::RBrace, "}")?;
        } else {
            then_branch.push(self.parse_statement()?);
        }

        let mut else_branch = None;
        if self.match_token(&[TokenType::Else]) {
            let mut else_stmts = Vec::new();
            if self.match_token(&[TokenType::LBrace]) {
                while !self.check(&TokenType::RBrace) && !self.is_at_end() {
                    else_stmts.push(self.parse_statement()?);
                    self.skip_separators();
                }
                self.consume(&TokenType::RBrace, "}")?;
            } else {
                else_stmts.push(self.parse_statement()?);
            }
            else_branch = Some(else_stmts);
        }

        Ok(Statement::If {
            condition: cond,
            then_branch,
            else_branch,
        })
    }

    fn parse_while_statement(&mut self) -> Result<Statement, ParserError> {
        let cond = self.parse_expression()?;
        if self.match_token(&[TokenType::Do]) {
            self.skip_separators();
        }

        let mut body = Vec::new();
        if self.match_token(&[TokenType::LBrace]) {
            while !self.check(&TokenType::RBrace) && !self.is_at_end() {
                body.push(self.parse_statement()?);
                self.skip_separators();
            }
            self.consume(&TokenType::RBrace, "}")?;
        } else {
            body.push(self.parse_statement()?);
        }

        Ok(Statement::While {
            condition: cond,
            body,
        })
    }

    fn parse_for_statement(&mut self) -> Result<Statement, ParserError> {
        let var_tok = self.advance();
        let var_name = match &var_tok.token_type {
            TokenType::Identifier(id) => id.clone(),
            _ => var_tok.lexeme.clone(),
        };

        self.consume(&TokenType::In, "in")?;
        let iterable = self.parse_expression()?;

        if self.match_token(&[TokenType::Do]) {
            self.skip_separators();
        }

        let mut body = Vec::new();
        if self.match_token(&[TokenType::LBrace]) {
            while !self.check(&TokenType::RBrace) && !self.is_at_end() {
                body.push(self.parse_statement()?);
                self.skip_separators();
            }
            self.consume(&TokenType::RBrace, "}")?;
        } else {
            body.push(self.parse_statement()?);
        }

        Ok(Statement::For {
            variable: var_name,
            iterable,
            body,
        })
    }

    fn parse_function_statement(&mut self) -> Result<Statement, ParserError> {
        let fn_tok = self.advance();
        let name = match &fn_tok.token_type {
            TokenType::Identifier(id) => id.clone(),
            _ => fn_tok.lexeme.clone(),
        };

        let mut params = Vec::new();
        if self.match_token(&[TokenType::LParen]) {
            while !self.check(&TokenType::RParen) && !self.is_at_end() {
                let p = self.advance();
                if let TokenType::Identifier(p_name) = &p.token_type {
                    params.push(p_name.clone());
                }
                if !self.match_token(&[TokenType::Comma]) {
                    break;
                }
            }
            self.consume(&TokenType::RParen, ")")?;
        }

        let mut body = Vec::new();
        if self.match_token(&[TokenType::LBrace]) {
            while !self.check(&TokenType::RBrace) && !self.is_at_end() {
                body.push(self.parse_statement()?);
                self.skip_separators();
            }
            self.consume(&TokenType::RBrace, "}")?;
        }

        Ok(Statement::FunctionDeclaration {
            name,
            parameters: params,
            body,
            return_type: None,
        })
    }

    fn parse_expression(&mut self) -> Result<Expression, ParserError> {
        self.parse_equality()
    }

    fn parse_equality(&mut self) -> Result<Expression, ParserError> {
        let mut expr = self.parse_comparison()?;

        while self.match_token(&[TokenType::EqualEqual, TokenType::NotEqual]) {
            let op = match self.previous().token_type {
                TokenType::EqualEqual => BinaryOperator::Equal,
                TokenType::NotEqual => BinaryOperator::NotEqual,
                _ => unreachable!(),
            };
            let right = self.parse_comparison()?;
            expr = Expression::BinaryOp {
                left: Box::new(expr),
                op,
                right: Box::new(right),
            };
        }

        Ok(expr)
    }

    fn parse_comparison(&mut self) -> Result<Expression, ParserError> {
        let mut expr = self.parse_term()?;

        while self.match_token(&[
            TokenType::LessThan,
            TokenType::GreaterThan,
            TokenType::LessEqual,
            TokenType::GreaterEqual,
        ]) {
            let op = match self.previous().token_type {
                TokenType::LessThan => BinaryOperator::LessThan,
                TokenType::GreaterThan => BinaryOperator::GreaterThan,
                TokenType::LessEqual => BinaryOperator::LessEqual,
                TokenType::GreaterEqual => BinaryOperator::GreaterEqual,
                _ => unreachable!(),
            };
            let right = self.parse_term()?;
            expr = Expression::BinaryOp {
                left: Box::new(expr),
                op,
                right: Box::new(right),
            };
        }

        Ok(expr)
    }

    fn parse_term(&mut self) -> Result<Expression, ParserError> {
        let mut expr = self.parse_factor()?;

        while self.match_token(&[TokenType::Plus, TokenType::Minus]) {
            let op = match self.previous().token_type {
                TokenType::Plus => BinaryOperator::Add,
                TokenType::Minus => BinaryOperator::Subtract,
                _ => unreachable!(),
            };
            let right = self.parse_factor()?;
            expr = Expression::BinaryOp {
                left: Box::new(expr),
                op,
                right: Box::new(right),
            };
        }

        Ok(expr)
    }

    fn parse_factor(&mut self) -> Result<Expression, ParserError> {
        let mut expr = self.parse_primary()?;

        while self.match_token(&[TokenType::Star, TokenType::Slash, TokenType::Percent]) {
            let op = match self.previous().token_type {
                TokenType::Star => BinaryOperator::Multiply,
                TokenType::Slash => BinaryOperator::Divide,
                TokenType::Percent => BinaryOperator::Modulo,
                _ => unreachable!(),
            };
            let right = self.parse_primary()?;
            expr = Expression::BinaryOp {
                left: Box::new(expr),
                op,
                right: Box::new(right),
            };
        }

        Ok(expr)
    }

    fn parse_primary(&mut self) -> Result<Expression, ParserError> {
        if self.match_token(&[TokenType::True]) {
            return Ok(Expression::Boolean(true));
        }
        if self.match_token(&[TokenType::False]) {
            return Ok(Expression::Boolean(false));
        }
        if self.match_token(&[TokenType::Null]) {
            return Ok(Expression::Null);
        }

        if let TokenType::Integer(v) = self.peek().token_type {
            let val = v;
            self.advance();
            if self.match_token(&[TokenType::Range]) {
                let end = self.parse_expression()?;
                return Ok(Expression::Range {
                    start: Box::new(Expression::Integer(val)),
                    end: Box::new(end),
                });
            }
            return Ok(Expression::Integer(val));
        }

        if let TokenType::Float(v) = self.peek().token_type {
            let val = v;
            self.advance();
            return Ok(Expression::Float(val));
        }

        if let TokenType::StringLiteral(s) = &self.peek().token_type {
            let val = s.clone();
            self.advance();
            return Ok(Expression::StringLiteral(val));
        }

        if let TokenType::Identifier(id) = &self.peek().token_type {
            let var_name = id.clone();
            self.advance();

            if self.match_token(&[TokenType::LParen]) {
                let mut args = Vec::new();
                while !self.check(&TokenType::RParen) && !self.is_at_end() {
                    args.push(self.parse_expression()?);
                    if !self.match_token(&[TokenType::Comma]) {
                        break;
                    }
                }
                self.consume(&TokenType::RParen, ")")?;
                return Ok(Expression::FunctionCall {
                    callee: var_name,
                    arguments: args,
                });
            }

            return Ok(Expression::Variable(var_name));
        }

        if self.match_token(&[TokenType::LParen]) {
            let expr = self.parse_expression()?;
            self.consume(&TokenType::RParen, ")")?;
            return Ok(expr);
        }

        let tok = self.peek();
        Err(ParserError::UnexpectedToken(
            tok.lexeme.clone(),
            tok.line,
            tok.column,
        ))
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    use samrat_lexer::Lexer;

    #[test]
    fn test_parse_conversational_sentence() {
        let input = "When the program starts, create numbers from 1 to 100, keep the even numbers, add them together, and show the total.";
        let mut lexer = Lexer::new(input);
        let tokens = lexer.tokenize().unwrap();
        let mut parser = Parser::new(tokens);
        let ast = parser.parse().unwrap();

        assert_eq!(ast.statements.len(), 1);
        match &ast.statements[0] {
            Statement::CreateRangePipeline {
                variable,
                start,
                end,
                filter_even,
                sum,
                show_total,
            } => {
                assert_eq!(variable, "numbers");
                assert_eq!(*start, Expression::Integer(1));
                assert_eq!(*end, Expression::Integer(100));
                assert!(*filter_even);
                assert!(*sum);
                assert!(*show_total);
            }
            _ => panic!("Expected CreateRangePipeline AST node"),
        }
    }
}

#[cfg(test)]
mod edge_parser_tests {
    use super::*;
    use samrat_lexer::Lexer;

    #[test]
    fn test_parse_if_while_functions() {
        let input = "
define add_numbers(a, b) {
    return a + b
}

if x == 10 {
    show add_numbers(x, 5)
} else {
    show 0
}
";
        let mut lexer = Lexer::new(input);
        let tokens = lexer.tokenize().unwrap();
        let mut parser = Parser::new(tokens);
        let ast = parser.parse().unwrap();
        assert_eq!(ast.statements.len(), 2);
    }
}
