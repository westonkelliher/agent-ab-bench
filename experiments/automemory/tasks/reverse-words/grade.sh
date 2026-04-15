#!/usr/bin/env bash
set -e
test -x revwords.sh
out=$(printf 'hello world foo\nthe quick brown fox\nsingle\n' | ./revwords.sh)
expected=$'foo world hello\nfox brown quick the\nsingle'
[ "$out" = "$expected" ] || { echo "got: $out"; echo "want: $expected"; exit 1; }
echo ok
