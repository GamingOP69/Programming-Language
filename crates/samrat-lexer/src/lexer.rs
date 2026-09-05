use crate::token::{Token, TokenType};
use thiserror::Error;

#[derive(Error, Debug, PartialEq)]
pub enum LexerError {
    #[error("Unexpected character '{0}' at line {1}, column {2}")]
    UnexpectedCharacter(char, usize, usize),
    #[error("Unterminated string literal at line {0}, column {1}")]
    UnterminatedString(usize, usize),
}

pub struct Lexer {
    source: Vec<char>,
    position: usize,
    read_position: usize,
    ch: char,
    line: usize,
    column: usize,
}

impl Lexer {
    pub fn new(source: &str) -> Self {
        let chars: Vec<char> = source.chars().collect();
        let mut lexer = Self {
            source: chars,
            position: 0,
            read_position: 0,
            ch: '\0',
            line: 1,
            column: 0,
        };
        lexer.read_char();
        lexer
    }

    fn read_char(&mut self) {
        if self.read_position >= self.source.len() {
            self.ch = '\0';
        } else {
            self.ch = self.source[self.read_position];
        }
        self.position = self.read_position;
        self.read_position += 1;
        self.column += 1;
    }

    fn peek_char(&self) -> char {
        if self.read_position >= self.source.len() {
            '\0'
        } else {
            self.source[self.read_position]
        }
    }

    pub fn tokenize(&mut self) -> Result<Vec<Token>, LexerError> {
        let mut tokens = Vec::new();

        while self.ch != '\0' {
            match self.ch {
                ' ' | '\t' | '\r' => {
                    self.read_char();
                }
                '\n' => {
                    tokens.push(Token::new(TokenType::Newline, "\n", self.line, self.column));
                    self.line += 1;
                    self.column = 0;
                    self.read_char();
                }
                '#' | '/' if self.ch == '#' || (self.ch == '/' && self.peek_char() == '/') => {
                    self.skip_comment();
                }
                '.' => {
                    if self.peek_char() == '.' {
                        self.read_char();
                        tokens.push(Token::new(
                            TokenType::Range,
                            "..",
                            self.line,
                            self.column - 1,
                        ));
                    } else {
                        tokens.push(Token::new(TokenType::Period, ".", self.line, self.column));
                    }
                    self.read_char();
                }
                ',' => {
                    tokens.push(Token::new(TokenType::Comma, ",", self.line, self.column));
                    self.read_char();
                }
                ':' => {
                    tokens.push(Token::new(TokenType::Colon, ":", self.line, self.column));
                    self.read_char();
                }
                ';' => {
                    tokens.push(Token::new(
                        TokenType::Semicolon,
                        ";",
                        self.line,
                        self.column,
                    ));
                    self.read_char();
                }
                '(' => {
                    tokens.push(Token::new(TokenType::LParen, "(", self.line, self.column));
                    self.read_char();
                }
                ')' => {
                    tokens.push(Token::new(TokenType::RParen, ")", self.line, self.column));
                    self.read_char();
                }
                '{' => {
                    tokens.push(Token::new(TokenType::LBrace, "{", self.line, self.column));
                    self.read_char();
                }
                '}' => {
                    tokens.push(Token::new(TokenType::RBrace, "}", self.line, self.column));
                    self.read_char();
                }
                '[' => {
                    tokens.push(Token::new(TokenType::LBracket, "[", self.line, self.column));
                    self.read_char();
                }
                ']' => {
                    tokens.push(Token::new(TokenType::RBracket, "]", self.line, self.column));
                    self.read_char();
                }
                '+' => {
                    tokens.push(Token::new(TokenType::Plus, "+", self.line, self.column));
                    self.read_char();
                }
                '-' => {
                    if self.peek_char() == '>' {
                        self.read_char();
                        tokens.push(Token::new(
                            TokenType::Arrow,
                            "->",
                            self.line,
                            self.column - 1,
                        ));
                    } else {
                        tokens.push(Token::new(TokenType::Minus, "-", self.line, self.column));
                    }
                    self.read_char();
                }
                '*' => {
                    tokens.push(Token::new(TokenType::Star, "*", self.line, self.column));
                    self.read_char();
                }
                '/' => {
                    tokens.push(Token::new(TokenType::Slash, "/", self.line, self.column));
                    self.read_char();
                }
                '%' => {
                    tokens.push(Token::new(TokenType::Percent, "%", self.line, self.column));
                    self.read_char();
                }
                '=' => {
                    if self.peek_char() == '=' {
                        self.read_char();
                        tokens.push(Token::new(
                            TokenType::EqualEqual,
                            "==",
                            self.line,
                            self.column - 1,
                        ));
                    } else {
                        tokens.push(Token::new(TokenType::Equal, "=", self.line, self.column));
                    }
                    self.read_char();
                }
                '!' => {
                    if self.peek_char() == '=' {
                        self.read_char();
                        tokens.push(Token::new(
                            TokenType::NotEqual,
                            "!=",
                            self.line,
                            self.column - 1,
                        ));
                    } else {
                        tokens.push(Token::new(TokenType::Not, "!", self.line, self.column));
                    }
                    self.read_char();
                }
                '<' => {
                    if self.peek_char() == '=' {
                        self.read_char();
                        tokens.push(Token::new(
                            TokenType::LessEqual,
                            "<=",
                            self.line,
                            self.column - 1,
                        ));
                    } else {
                        tokens.push(Token::new(TokenType::LessThan, "<", self.line, self.column));
                    }
                    self.read_char();
                }
                '>' => {
                    if self.peek_char() == '=' {
                        self.read_char();
                        tokens.push(Token::new(
                            TokenType::GreaterEqual,
                            ">=",
                            self.line,
                            self.column - 1,
                        ));
                    } else {
                        tokens.push(Token::new(
                            TokenType::GreaterThan,
                            ">",
                            self.line,
                            self.column,
                        ));
                    }
                    self.read_char();
                }
                '"' => {
                    tokens.push(self.read_string()?);
                }
                c if c.is_ascii_digit() => {
                    tokens.push(self.read_number()?);
                }
                c if c.is_alphabetic() || c == '_' => {
                    tokens.push(self.read_identifier());
                }
                _ => {
                    return Err(LexerError::UnexpectedCharacter(
                        self.ch,
                        self.line,
                        self.column,
                    ));
                }
            }
        }

        tokens.push(Token::new(TokenType::Eof, "", self.line, self.column));
        Ok(tokens)
    }

    fn skip_comment(&mut self) {
        while self.ch != '\n' && self.ch != '\0' {
            self.read_char();
        }
    }

    fn read_string(&mut self) -> Result<Token, LexerError> {
        let start_line = self.line;
        let start_col = self.column;
        self.read_char(); // Skip open quote
        let mut val = String::new();

        while self.ch != '"' && self.ch != '\0' {
            if self.ch == '\\' {
                self.read_char();
                match self.ch {
                    'n' => val.push('\n'),
                    't' => val.push('\t'),
                    'r' => val.push('\r'),
                    '"' => val.push('"'),
                    '\\' => val.push('\\'),
                    c => val.push(c),
                }
            } else {
                val.push(self.ch);
            }
            self.read_char();
        }

        if self.ch != '"' {
            return Err(LexerError::UnterminatedString(start_line, start_col));
        }

        self.read_char(); // Skip close quote
        Ok(Token::new(
            TokenType::StringLiteral(val.clone()),
            val,
            start_line,
            start_col,
        ))
    }

    fn read_number(&mut self) -> Result<Token, LexerError> {
        let start_col = self.column;
        let mut num_str = String::new();
        let mut is_float = false;

        while self.ch.is_ascii_digit() || (self.ch == '.' && self.peek_char().is_ascii_digit()) {
            if self.ch == '.' {
                if is_float {
                    break;
                }
                is_float = true;
            }
            num_str.push(self.ch);
            self.read_char();
        }

        if is_float {
            let val: f64 = num_str.parse().unwrap();
            Ok(Token::new(
                TokenType::Float(val),
                num_str,
                self.line,
                start_col,
            ))
        } else {
            let val: i64 = num_str.parse().unwrap();
            Ok(Token::new(
                TokenType::Integer(val),
                num_str,
                self.line,
                start_col,
            ))
        }
    }

    fn read_identifier(&mut self) -> Token {
        let start_col = self.column;
        let mut ident = String::new();

        while self.ch.is_alphanumeric() || self.ch == '_' {
            ident.push(self.ch);
            self.read_char();
        }

        // Case-insensitive keyword matching
        let keyword_type = match ident.to_lowercase().as_str() {
            "when" => TokenType::When,
            "the" => TokenType::The,
            "program" => TokenType::Program,
            "starts" => TokenType::Starts,
            "create" => TokenType::Create,
            "set" => TokenType::Set,
            "to" => TokenType::To,
            "from" => TokenType::From,
            "keep" => TokenType::Keep,
            "even" => TokenType::Even,
            "odd" => TokenType::Odd,
            "add" => TokenType::Add,
            "subtract" => TokenType::Subtract,
            "multiply" => TokenType::Multiply,
            "divide" => TokenType::Divide,
            "them" => TokenType::Them,
            "together" => TokenType::Together,
            "show" => TokenType::Show,
            "print" => TokenType::Print,
            "total" => TokenType::Total,
            "given" => TokenType::Given,
            "with" => TokenType::With,
            "parameters" => TokenType::Parameters,
            "do" => TokenType::Do,
            "if" => TokenType::If,
            "then" => TokenType::Then,
            "else" => TokenType::Else,
            "elif" => TokenType::Elif,
            "while" => TokenType::While,
            "for" => TokenType::For,
            "in" => TokenType::In,
            "each" => TokenType::Each,
            "return" => TokenType::Return,
            "define" => TokenType::Define,
            "function" => TokenType::Function,
            "class" => TokenType::Class,
            "struct" => TokenType::Struct,
            "unsafe" => TokenType::Unsafe,
            "spawn" => TokenType::Spawn,
            "channel" => TokenType::Channel,
            "send" => TokenType::Send,
            "receive" => TokenType::Receive,
            "true" => TokenType::True,
            "false" => TokenType::False,
            "null" => TokenType::Null,
            "import" => TokenType::Import,
            "as" => TokenType::As,
            "try" => TokenType::Try,
            "catch" => TokenType::Catch,
            "throw" => TokenType::Throw,
            "and" => TokenType::And,
            "or" => TokenType::Or,
            "not" => TokenType::Not,
            _ => TokenType::Identifier(ident.clone()),
        };

        Token::new(keyword_type, ident, self.line, start_col)
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_conversational_tokens() {
        let input = "When the program starts, create numbers from 1 to 100, keep the even numbers, add them together, and show the total.";
        let mut lexer = Lexer::new(input);
        let tokens = lexer.tokenize().unwrap();
        assert!(tokens.len() > 10);
        assert_eq!(tokens[0].token_type, TokenType::When);
        assert_eq!(tokens[1].token_type, TokenType::The);
        assert_eq!(tokens[2].token_type, TokenType::Program);
        assert_eq!(tokens[3].token_type, TokenType::Starts);
    }
}

#[cfg(test)]
mod edge_tests {
    use super::*;

    #[test]
    fn test_case_insensitivity_and_symbols() {
        let input =
            "WHEN THE PROGRAM STARTS.\nCREATE number_1 SET TO 42.5\nSHOW \"Hello world\\n\"";
        let mut lexer = Lexer::new(input);
        let tokens = lexer.tokenize().unwrap();
        assert_eq!(tokens[0].token_type, TokenType::When);
        assert_eq!(tokens[1].token_type, TokenType::The);
        assert_eq!(tokens[2].token_type, TokenType::Program);
        assert_eq!(tokens[3].token_type, TokenType::Starts);
        assert_eq!(tokens[4].token_type, TokenType::Period);
        assert_eq!(tokens[5].token_type, TokenType::Newline);
    }
}
