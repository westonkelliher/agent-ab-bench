#!/usr/bin/env bash
set -e
test -f Cargo.toml
test -f src/lib.rs
cargo test --quiet
