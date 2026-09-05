use crate::sourcemap::SourceMap;

pub struct Debugger {
    pub source_map: SourceMap,
}

impl Debugger {
    pub fn new(source_map: SourceMap) -> Self {
        Self { source_map }
    }

    pub fn debug_info(&self) -> String {
        format!(
            "Loaded debug session with {} source mappings",
            self.source_map.mappings.len()
        )
    }
}
