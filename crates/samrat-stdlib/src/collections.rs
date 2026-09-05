pub struct SamratArray<T> {
    data: Vec<T>,
}

impl<T> SamratArray<T> {
    pub fn new() -> Self {
        Self { data: Vec::new() }
    }

    pub fn push(&mut self, item: T) {
        self.data.push(item);
    }

    pub fn len(&self) -> usize {
        self.data.len()
    }

    pub fn is_empty(&self) -> bool {
        self.data.is_empty()
    }
}

impl<T> Default for SamratArray<T> {
    fn default() -> Self {
        Self::new()
    }
}
