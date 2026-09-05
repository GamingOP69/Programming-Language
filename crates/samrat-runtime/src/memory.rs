use std::alloc::{alloc, dealloc, Layout};

pub struct MemoryManager;

impl MemoryManager {
    /// # Safety
    ///
    /// The caller must ensure that `size` and `align` define a valid layout.
    pub unsafe fn allocate(size: usize, align: usize) -> *mut u8 {
        let layout = Layout::from_size_align_unchecked(size, align);
        alloc(layout)
    }

    /// # Safety
    ///
    /// The caller must ensure `ptr` was allocated with the same `size` and `align`.
    pub unsafe fn deallocate(ptr: *mut u8, size: usize, align: usize) {
        let layout = Layout::from_size_align_unchecked(size, align);
        dealloc(ptr, layout);
    }
}

pub struct RefCounted<T> {
    ptr: *mut T,
    ref_count: *mut usize,
}

impl<T> RefCounted<T> {
    pub fn new(val: T) -> Self {
        let ptr = Box::into_raw(Box::new(val));
        let ref_count = Box::into_raw(Box::new(1));
        Self { ptr, ref_count }
    }

    pub fn clone_ref(&self) -> Self {
        unsafe {
            *self.ref_count += 1;
        }
        Self {
            ptr: self.ptr,
            ref_count: self.ref_count,
        }
    }
}

impl<T> Drop for RefCounted<T> {
    fn drop(&mut self) {
        unsafe {
            *self.ref_count -= 1;
            if *self.ref_count == 0 {
                let _ = Box::from_raw(self.ptr);
                let _ = Box::from_raw(self.ref_count);
            }
        }
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_ref_counter() {
        let rc = RefCounted::new(42);
        let rc2 = rc.clone_ref();
        assert_eq!(unsafe { *rc.ref_count }, 2);
        drop(rc2);
        assert_eq!(unsafe { *rc.ref_count }, 1);
    }
}
