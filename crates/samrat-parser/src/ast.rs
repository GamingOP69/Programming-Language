#[derive(Debug, Clone, PartialEq)]
pub enum Expression {
    Integer(i64),
    Float(f64),
    StringLiteral(String),
    Boolean(bool),
    Null,
    Variable(String),
    BinaryOp {
        left: Box<Expression>,
        op: BinaryOperator,
        right: Box<Expression>,
    },
    UnaryOp {
        op: UnaryOperator,
        expr: Box<Expression>,
    },
    FunctionCall {
        callee: String,
        arguments: Vec<Expression>,
    },
    Range {
        start: Box<Expression>,
        end: Box<Expression>,
    },
    ArrayLiteral(Vec<Expression>),
}

#[derive(Debug, Clone, PartialEq)]
pub enum BinaryOperator {
    Add,
    Subtract,
    Multiply,
    Divide,
    Modulo,
    Equal,
    NotEqual,
    LessThan,
    GreaterThan,
    LessEqual,
    GreaterEqual,
    And,
    Or,
}

#[derive(Debug, Clone, PartialEq)]
pub enum UnaryOperator {
    Negate,
    Not,
}

#[derive(Debug, Clone, PartialEq)]
pub enum Statement {
    Entrypoint(Vec<Statement>),
    CreateRangePipeline {
        variable: String,
        start: Expression,
        end: Expression,
        filter_even: bool,
        sum: bool,
        show_total: bool,
    },
    VariableDeclaration {
        name: String,
        value: Expression,
        type_annotation: Option<String>,
    },
    Assignment {
        target: String,
        value: Expression,
    },
    Print(Expression),
    If {
        condition: Expression,
        then_branch: Vec<Statement>,
        else_branch: Option<Vec<Statement>>,
    },
    While {
        condition: Expression,
        body: Vec<Statement>,
    },
    For {
        variable: String,
        iterable: Expression,
        body: Vec<Statement>,
    },
    FunctionDeclaration {
        name: String,
        parameters: Vec<String>,
        body: Vec<Statement>,
        return_type: Option<String>,
    },
    Return(Option<Expression>),
    Expression(Expression),
}

#[derive(Debug, Clone, PartialEq)]
pub struct Program {
    pub statements: Vec<Statement>,
}
