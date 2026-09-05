pub fn sum_range(start: i64, end: i64, filter_even: bool) -> i64 {
    let mut sum = 0;
    for i in start..=end {
        if !filter_even || i % 2 == 0 {
            sum += i;
        }
    }
    sum
}
