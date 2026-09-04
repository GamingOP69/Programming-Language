use crate::backend::{Backend, CodegenError};
use samrat_ir::ir::{IrModule, IrInstruction, IrValue};
use cranelift_codegen::ir::{AbiParam, InstBuilder, types};
use cranelift_codegen::settings::{self, Flags};
use cranelift_frontend::{FunctionBuilder, FunctionBuilderContext};
use cranelift_module::{Module, Linkage};
use cranelift_object::{ObjectBuilder, ObjectModule};
use target_lexicon::Triple;
use std::collections::HashMap;

pub struct NativeCodegenBackend {
    target_triple: Triple,
}

impl NativeCodegenBackend {
    pub fn new() -> Self {
        Self {
            target_triple: Triple::host(),
        }
    }
}

impl Backend for NativeCodegenBackend {
    fn compile(&mut self, ir_module: &IrModule) -> Result<Vec<u8>, CodegenError> {
        let flag_builder = settings::builder();
        let flags = Flags::new(flag_builder);
        let isa = cranelift_codegen::isa::lookup(self.target_triple.clone())
            .map_err(|e| CodegenError::CraneliftError(e.to_string()))?
            .finish(flags)
            .map_err(|e| CodegenError::CraneliftError(e.to_string()))?;

        let builder = ObjectBuilder::new(isa, "samrat_app", cranelift_module::default_libcall_names())
            .map_err(|e| CodegenError::CraneliftError(e.to_string()))?;
        let mut module = ObjectModule::new(builder);

        for func in &ir_module.functions {
            let mut sig = module.make_signature();
            sig.returns.push(AbiParam::new(types::I64));

            let func_id = module.declare_function(&func.name, Linkage::Export, &sig)
                .map_err(|e| CodegenError::CraneliftError(e.to_string()))?;

            let mut ctx = module.make_context();
            ctx.func.signature = sig;

            let mut builder_ctx = FunctionBuilderContext::new();
            let mut builder = FunctionBuilder::new(&mut ctx.func, &mut builder_ctx);

            let entry_block = builder.create_block();
            builder.append_block_params_for_function_params(entry_block);
            builder.switch_to_block(entry_block);

            let mut var_map: HashMap<String, cranelift_codegen::ir::Value> = HashMap::new();
            let mut last_val = builder.ins().iconst(types::I64, 0);

            for inst in &func.instructions {
                match inst {
                    IrInstruction::CreateRangePipeline { start, end, filter_even, sum, dest } => {
                        let mut total: i64 = 0;
                        for n in *start..=*end {
                            if !*filter_even || n % 2 == 0 {
                                if *sum {
                                    total += n;
                                }
                            }
                        }
                        let val = builder.ins().iconst(types::I64, total);
                        var_map.insert(dest.clone(), val);
                        last_val = val;
                    }
                    IrInstruction::Print { value } => {
                        let val = match value {
                            IrValue::ConstantInt(i) => builder.ins().iconst(types::I64, *i),
                            IrValue::Variable(v) => *var_map.get(v).unwrap_or(&builder.ins().iconst(types::I64, 0)),
                            _ => builder.ins().iconst(types::I64, 0),
                        };
                        last_val = val;
                    }
                    IrInstruction::Return { value } => {
                        let ret_val = match value {
                            Some(IrValue::ConstantInt(i)) => builder.ins().iconst(types::I64, *i),
                            Some(IrValue::Variable(v)) => *var_map.get(v).unwrap_or(&builder.ins().iconst(types::I64, 0)),
                            _ => builder.ins().iconst(types::I64, 0),
                        };
                        last_val = ret_val;
                    }
                    _ => {}
                }
            }

            builder.ins().return_(&[last_val]);
            builder.seal_block(entry_block);
            builder.finalize();

            module.define_function(func_id, &mut ctx)
                .map_err(|e| CodegenError::CraneliftError(e.to_string()))?;
            module.clear_context(&mut ctx);
        }

        let product = module.finish();
        let bytes = product.emit().map_err(|e| CodegenError::CraneliftError(e.to_string()))?;
        Ok(bytes)
    }
}
