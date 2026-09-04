pub struct SourceLocation {
    pub file: String,
    pub line: usize,
    pub column: usize,
}

pub struct SourceMap {
    pub mappings: Vec<(usize, SourceLocation)>,
}

impl SourceMap {
    pub fn new() -> Self {
        Self { mappings: Vec::new() }
    }

    pub fn add_mapping(&mut self, instruction_offset: usize, loc: SourceLocation) {
        self.mappings.push((instruction_offset, loc));
    }
}
