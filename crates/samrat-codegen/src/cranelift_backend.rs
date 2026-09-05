use crate::backend::{Backend, CodegenError};
use cranelift_codegen::ir::{types, AbiParam, InstBuilder};
use cranelift_codegen::settings::{self, Flags};
use cranelift_frontend::{FunctionBuilder, FunctionBuilderContext, Variable};
use cranelift_module::{Linkage, Module};
use cranelift_object::{ObjectBuilder, ObjectModule};
use samrat_ir::ir::{IrInstruction, IrModule, IrValue};
use std::collections::HashMap;
use target_lexicon::Triple;

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

impl Default for NativeCodegenBackend {
    fn default() -> Self {
        Self::new()
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

        let builder =
            ObjectBuilder::new(isa, "samrat_app", cranelift_module::default_libcall_names())
                .map_err(|e| CodegenError::CraneliftError(e.to_string()))?;
        let mut module = ObjectModule::new(builder);

        for func in &ir_module.functions {
            let mut sig = module.make_signature();
            for _ in &func.params {
                sig.params.push(AbiParam::new(types::I64));
            }
            sig.returns.push(AbiParam::new(types::I64));

            let func_id = module
                .declare_function(&func.name, Linkage::Export, &sig)
                .map_err(|e| CodegenError::CraneliftError(e.to_string()))?;

            let mut ctx = module.make_context();
            ctx.func.signature = sig;

            let mut builder_ctx = FunctionBuilderContext::new();
            let mut builder = FunctionBuilder::new(&mut ctx.func, &mut builder_ctx);

            let entry_block = builder.create_block();
            builder.append_block_params_for_function_params(entry_block);
            builder.switch_to_block(entry_block);

            let mut var_map: HashMap<String, Variable> = HashMap::new();
            let mut var_counter = 0u32;
            let mut block_map: HashMap<String, cranelift_codegen::ir::Block> = HashMap::new();

            // Bind function parameters to variables
            for (idx, (param_name, _)) in func.params.iter().enumerate() {
                let var = Variable::from_u32(var_counter);
                var_counter += 1;
                builder.declare_var(var, types::I64);
                let param_val = builder.block_params(entry_block)[idx];
                builder.def_var(var, param_val);
                var_map.insert(param_name.clone(), var);
            }

            let mut last_val = builder.ins().iconst(types::I64, 0);

            for inst in &func.instructions {
                match inst {
                    IrInstruction::Alloca { dest, .. } => {
                        let var = Variable::from_u32(var_counter);
                        var_counter += 1;
                        builder.declare_var(var, types::I64);
                        let zero = builder.ins().iconst(types::I64, 0);
                        builder.def_var(var, zero);
                        var_map.insert(dest.clone(), var);
                    }
                    IrInstruction::Store { src, dest } => {
                        let val = match src {
                            IrValue::ConstantInt(i) => builder.ins().iconst(types::I64, *i),
                            IrValue::ConstantFloat(f) => builder.ins().f64const(*f),
                            IrValue::ConstantBool(b) => {
                                builder.ins().iconst(types::I64, if *b { 1 } else { 0 })
                            }
                            IrValue::Variable(v) => {
                                if let Some(&var) = var_map.get(v) {
                                    builder.use_var(var)
                                } else {
                                    builder.ins().iconst(types::I64, 0)
                                }
                            }
                        };
                        let var = if let Some(&v) = var_map.get(dest) {
                            v
                        } else {
                            let v = Variable::from_u32(var_counter);
                            var_counter += 1;
                            builder.declare_var(v, types::I64);
                            var_map.insert(dest.clone(), v);
                            v
                        };
                        builder.def_var(var, val);
                        last_val = val;
                    }
                    IrInstruction::Load { dest, src } => {
                        let val = if let Some(&var) = var_map.get(src) {
                            builder.use_var(var)
                        } else {
                            builder.ins().iconst(types::I64, 0)
                        };
                        let dest_var = if let Some(&v) = var_map.get(dest) {
                            v
                        } else {
                            let v = Variable::from_u32(var_counter);
                            var_counter += 1;
                            builder.declare_var(v, types::I64);
                            var_map.insert(dest.clone(), v);
                            v
                        };
                        builder.def_var(dest_var, val);
                        last_val = val;
                    }
                    IrInstruction::Add { dest, left, right } => {
                        let l = resolve_val(&mut builder, left, &var_map);
                        let r = resolve_val(&mut builder, right, &var_map);
                        let res = builder.ins().iadd(l, r);
                        assign_var(&mut builder, dest, res, &mut var_map, &mut var_counter);
                        last_val = res;
                    }
                    IrInstruction::Sub { dest, left, right } => {
                        let l = resolve_val(&mut builder, left, &var_map);
                        let r = resolve_val(&mut builder, right, &var_map);
                        let res = builder.ins().isub(l, r);
                        assign_var(&mut builder, dest, res, &mut var_map, &mut var_counter);
                        last_val = res;
                    }
                    IrInstruction::Mul { dest, left, right } => {
                        let l = resolve_val(&mut builder, left, &var_map);
                        let r = resolve_val(&mut builder, right, &var_map);
                        let res = builder.ins().imul(l, r);
                        assign_var(&mut builder, dest, res, &mut var_map, &mut var_counter);
                        last_val = res;
                    }
                    IrInstruction::Div { dest, left, right } => {
                        let l = resolve_val(&mut builder, left, &var_map);
                        let r = resolve_val(&mut builder, right, &var_map);
                        let res = builder.ins().sdiv(l, r);
                        assign_var(&mut builder, dest, res, &mut var_map, &mut var_counter);
                        last_val = res;
                    }
                    IrInstruction::Mod { dest, left, right } => {
                        let l = resolve_val(&mut builder, left, &var_map);
                        let r = resolve_val(&mut builder, right, &var_map);
                        let res = builder.ins().srem(l, r);
                        assign_var(&mut builder, dest, res, &mut var_map, &mut var_counter);
                        last_val = res;
                    }
                    IrInstruction::CmpEq { dest, left, right } => {
                        let l = resolve_val(&mut builder, left, &var_map);
                        let r = resolve_val(&mut builder, right, &var_map);
                        let res = builder.ins().icmp(
                            cranelift_codegen::ir::condcodes::IntCC::Equal,
                            l,
                            r,
                        );
                        let ext = builder.ins().uextend(types::I64, res);
                        assign_var(&mut builder, dest, ext, &mut var_map, &mut var_counter);
                        last_val = ext;
                    }
                    IrInstruction::CmpNe { dest, left, right } => {
                        let l = resolve_val(&mut builder, left, &var_map);
                        let r = resolve_val(&mut builder, right, &var_map);
                        let res = builder.ins().icmp(
                            cranelift_codegen::ir::condcodes::IntCC::NotEqual,
                            l,
                            r,
                        );
                        let ext = builder.ins().uextend(types::I64, res);
                        assign_var(&mut builder, dest, ext, &mut var_map, &mut var_counter);
                        last_val = ext;
                    }
                    IrInstruction::CmpLt { dest, left, right } => {
                        let l = resolve_val(&mut builder, left, &var_map);
                        let r = resolve_val(&mut builder, right, &var_map);
                        let res = builder.ins().icmp(
                            cranelift_codegen::ir::condcodes::IntCC::SignedLessThan,
                            l,
                            r,
                        );
                        let ext = builder.ins().uextend(types::I64, res);
                        assign_var(&mut builder, dest, ext, &mut var_map, &mut var_counter);
                        last_val = ext;
                    }
                    IrInstruction::CmpGt { dest, left, right } => {
                        let l = resolve_val(&mut builder, left, &var_map);
                        let r = resolve_val(&mut builder, right, &var_map);
                        let res = builder.ins().icmp(
                            cranelift_codegen::ir::condcodes::IntCC::SignedGreaterThan,
                            l,
                            r,
                        );
                        let ext = builder.ins().uextend(types::I64, res);
                        assign_var(&mut builder, dest, ext, &mut var_map, &mut var_counter);
                        last_val = ext;
                    }
                    IrInstruction::CreateRangePipeline {
                        start,
                        end,
                        filter_even,
                        sum,
                        dest,
                    } => {
                        let mut total: i64 = 0;
                        for n in *start..=*end {
                            if (!*filter_even || n % 2 == 0) && *sum {
                                total += n;
                            }
                        }
                        let val = builder.ins().iconst(types::I64, total);
                        assign_var(&mut builder, dest, val, &mut var_map, &mut var_counter);
                        last_val = val;
                    }
                    IrInstruction::Print { value } => {
                        let val = resolve_val(&mut builder, value, &var_map);
                        last_val = val;
                    }
                    IrInstruction::Return { value } => {
                        let ret_val = match value {
                            Some(v) => resolve_val(&mut builder, v, &var_map),
                            None => builder.ins().iconst(types::I64, 0),
                        };
                        builder.ins().return_(&[ret_val]);
                        last_val = ret_val;
                    }
                    IrInstruction::Label { name } => {
                        let block = *block_map
                            .entry(name.clone())
                            .or_insert_with(|| builder.create_block());
                        if !builder.is_unreachable() {
                            builder.ins().jump(block, &[]);
                        }
                        builder.switch_to_block(block);
                    }
                    IrInstruction::Jump { target } => {
                        let block = *block_map
                            .entry(target.clone())
                            .or_insert_with(|| builder.create_block());
                        builder.ins().jump(block, &[]);
                    }
                    IrInstruction::JumpIf {
                        condition,
                        then_target,
                        else_target,
                    } => {
                        let cond = resolve_val(&mut builder, condition, &var_map);
                        let then_block = *block_map
                            .entry(then_target.clone())
                            .or_insert_with(|| builder.create_block());
                        let else_block = *block_map
                            .entry(else_target.clone())
                            .or_insert_with(|| builder.create_block());
                        builder.ins().brif(cond, then_block, &[], else_block, &[]);
                    }
                    IrInstruction::Call { dest, args, .. } => {
                        let _arg_vals: Vec<_> = args
                            .iter()
                            .map(|a| resolve_val(&mut builder, a, &var_map))
                            .collect();
                        let dummy_ret = builder.ins().iconst(types::I64, 0);
                        if let Some(d) = dest {
                            assign_var(&mut builder, d, dummy_ret, &mut var_map, &mut var_counter);
                        }
                        last_val = dummy_ret;
                    }
                }
            }

            if !builder.is_unreachable() {
                builder.ins().return_(&[last_val]);
            }
            builder.seal_all_blocks();
            builder.finalize();

            module
                .define_function(func_id, &mut ctx)
                .map_err(|e| CodegenError::CraneliftError(e.to_string()))?;
            module.clear_context(&mut ctx);
        }

        let product = module.finish();
        let bytes = product
            .emit()
            .map_err(|e| CodegenError::CraneliftError(e.to_string()))?;
        Ok(bytes)
    }
}

fn resolve_val(
    builder: &mut FunctionBuilder,
    val: &IrValue,
    var_map: &HashMap<String, Variable>,
) -> cranelift_codegen::ir::Value {
    match val {
        IrValue::ConstantInt(i) => builder.ins().iconst(types::I64, *i),
        IrValue::ConstantFloat(f) => builder.ins().f64const(*f),
        IrValue::ConstantBool(b) => builder.ins().iconst(types::I64, if *b { 1 } else { 0 }),
        IrValue::Variable(v) => {
            if let Some(&var) = var_map.get(v) {
                builder.use_var(var)
            } else {
                builder.ins().iconst(types::I64, 0)
            }
        }
    }
}

fn assign_var(
    builder: &mut FunctionBuilder,
    name: &str,
    val: cranelift_codegen::ir::Value,
    var_map: &mut HashMap<String, Variable>,
    var_counter: &mut u32,
) {
    let var = if let Some(&v) = var_map.get(name) {
        v
    } else {
        let v = Variable::from_u32(*var_counter);
        *var_counter += 1;
        builder.declare_var(v, types::I64);
        var_map.insert(name.to_string(), v);
        v
    };
    builder.def_var(var, val);
}
