use samrat_ir::ir::IrModule;
use thiserror::Error;

#[derive(Error, Debug)]
pub enum CodegenError {
    #[error("Cranelift codegen error: {0}")]
    CraneliftError(String),
}

pub trait Backend {
    fn compile(&mut self, module: &IrModule) -> Result<Vec<u8>, CodegenError>;
}
