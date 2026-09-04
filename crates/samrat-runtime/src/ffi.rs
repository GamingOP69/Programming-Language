pub unsafe fn raw_pointer_read<T: Copy>(ptr: *const T) -> T {
    *ptr
}

pub unsafe fn raw_pointer_write<T>(ptr: *mut T, val: T) {
    *ptr = val;
}
