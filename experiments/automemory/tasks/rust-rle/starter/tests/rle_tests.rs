use rle::{decode, encode};

#[test]
fn encode_empty() {
    assert_eq!(encode(""), "");
}

#[test]
fn encode_single() {
    assert_eq!(encode("a"), "a");
}

#[test]
fn encode_no_repeats() {
    assert_eq!(encode("abcde"), "abcde");
}

#[test]
fn encode_simple_run() {
    assert_eq!(encode("aaabbc"), "3a2bc");
}

#[test]
fn encode_long_run() {
    let s: String = std::iter::repeat('x').take(12).collect();
    assert_eq!(encode(&s), "12x");
}

#[test]
fn encode_with_spaces() {
    assert_eq!(encode("aa  bb"), "2a2 2b");
}

#[test]
fn decode_empty() {
    assert_eq!(decode("").unwrap(), "");
}

#[test]
fn decode_no_counts() {
    assert_eq!(decode("abcde").unwrap(), "abcde");
}

#[test]
fn decode_simple() {
    assert_eq!(decode("3a2bc").unwrap(), "aaabbc");
}

#[test]
fn decode_multidigit() {
    assert_eq!(decode("12x").unwrap(), "xxxxxxxxxxxx");
}

#[test]
fn decode_trailing_digits_is_error() {
    assert!(decode("3a4").is_err());
}

#[test]
fn decode_zero_count_is_error() {
    assert!(decode("0a").is_err());
}

#[test]
fn roundtrip() {
    let cases = ["", "a", "abc", "aaabbc", "wwwwwwoooood", "hello  world"];
    for c in cases {
        assert_eq!(decode(&encode(c)).unwrap(), c, "roundtrip failed for {:?}", c);
    }
}
