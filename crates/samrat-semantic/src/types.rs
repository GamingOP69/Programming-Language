#[derive(Debug, Clone, PartialEq, Eq)]
pub enum Type {
    Int,
    Float,
    String,
    Bool,
    Null,
    Array(Box<Type>),
    Pointer(Box<Type>),
    Function {
        params: Vec<Type>,
        return_type: Box<Type>,
    },
    Void,
    Unknown,
}

impl std::fmt::Display for Type {
    fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
        match self {
            Type::Int => write!(f, "Integer"),
            Type::Float => write!(f, "Float"),
            Type::String => write!(f, "String"),
            Type::Bool => write!(f, "Boolean"),
            Type::Null => write!(f, "Null"),
            Type::Array(inner) => write!(f, "Array[{}]", inner),
            Type::Pointer(inner) => write!(f, "Pointer[{}]", inner),
            Type::Function { params, return_type } => {
                let params_str: Vec<String> = params.iter().map(|p| p.to_string()).collect();
                write!(f, "fn({}) -> {}", params_str.join(", "), return_type)
            }
            Type::Void => write!(f, "Void"),
            Type::Unknown => write!(f, "Unknown"),
        }
    }
}
