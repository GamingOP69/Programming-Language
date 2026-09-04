#[derive(Debug, Clone, PartialEq)]
pub enum IrType {
    I64,
    F64,
    Bool,
    Ptr,
    Void,
}

#[derive(Debug, Clone, PartialEq)]
pub enum IrValue {
    ConstantInt(i64),
    ConstantFloat(f64),
    ConstantBool(bool),
    Variable(String),
}

#[derive(Debug, Clone, PartialEq)]
pub enum IrInstruction {
    Alloca { dest: String, ty: IrType },
    Load { dest: String, src: String },
    Store { src: IrValue, dest: String },
    Add { dest: String, left: IrValue, right: IrValue },
    Sub { dest: String, left: IrValue, right: IrValue },
    Mul { dest: String, left: IrValue, right: IrValue },
    Div { dest: String, left: IrValue, right: IrValue },
    Mod { dest: String, left: IrValue, right: IrValue },
    CmpEq { dest: String, left: IrValue, right: IrValue },
    CmpNe { dest: String, left: IrValue, right: IrValue },
    CmpLt { dest: String, left: IrValue, right: IrValue },
    CmpGt { dest: String, left: IrValue, right: IrValue },
    CreateRangePipeline {
        start: i64,
        end: i64,
        filter_even: bool,
        sum: bool,
        dest: String,
    },
    Call { dest: Option<String>, name: String, args: Vec<IrValue> },
    Print { value: IrValue },
    Return { value: Option<IrValue> },
    Jump { target: String },
    JumpIf { condition: IrValue, then_target: String, else_target: String },
    Label { name: String },
}

#[derive(Debug, Clone, PartialEq)]
pub struct IrFunction {
    pub name: String,
    pub params: Vec<(String, IrType)>,
    pub return_type: IrType,
    pub instructions: Vec<IrInstruction>,
}

#[derive(Debug, Clone, PartialEq)]
pub struct IrModule {
    pub functions: Vec<IrFunction>,
}
