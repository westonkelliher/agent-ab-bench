The current directory contains a Rust crate `rle` with a failing test suite. Your job is to implement the two public functions in `src/lib.rs`:

```rust
pub fn encode(input: &str) -> String;
pub fn decode(input: &str) -> Result<String, String>;
```

Rules for encoding:
- A run of length 1 is emitted as just the character (no count). Example: `"abc"` -> `"abc"`.
- A run of length >= 2 is emitted as the count followed by the character. Example: `"aaabbc"` -> `"3a2bc"`.
- The input may contain any ASCII letters or spaces. You may assume no digits appear in the input to `encode`.
- Empty string encodes to empty string.

Rules for decoding:
- Inverse of encode. Multi-digit counts are allowed (e.g. `"12a"` -> `"aaaaaaaaaaaa"`).
- A digit sequence must be followed by a non-digit character. If the input ends in digits or is otherwise malformed (e.g. a count of zero), return `Err(...)` with any non-empty error message.
- Empty string decodes to empty string (Ok).

Run `cargo test` to verify — the existing tests in `tests/rle_tests.rs` define the exact expected behavior. Do not modify the tests. You may only edit `src/lib.rs`.
