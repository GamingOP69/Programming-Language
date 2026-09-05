/// # Safety
///
/// The caller must guarantee that `ptr` is valid for reads and properly aligned.
pub unsafe fn raw_pointer_read<T: Copy>(ptr: *const T) -> T {
    *ptr
}

/// # Safety
///
/// The caller must guarantee that `ptr` is valid for writes and properly aligned.
pub unsafe fn raw_pointer_write<T>(ptr: *mut T, val: T) {
    *ptr = val;
}
