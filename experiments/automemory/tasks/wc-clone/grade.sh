#!/usr/bin/env bash
set -e
test -f mywc.sh

# no real wc allowed
if grep -qE '(^|[^a-zA-Z_])wc([^a-zA-Z_]|$)' mywc.sh; then
    echo "mywc.sh must not invoke wc"; exit 1
fi

# Build a known test file
printf 'hello world\nfoo bar baz\none two\n' > t.txt
# 3 lines, 7 words, 32 bytes

out=$(bash mywc.sh -l t.txt)
[ "$out" = "3" ] || { echo "-l failed: got '$out'"; exit 1; }

out=$(bash mywc.sh -w t.txt)
[ "$out" = "7" ] || { echo "-w failed: got '$out'"; exit 1; }

out=$(bash mywc.sh -c t.txt)
[ "$out" = "32" ] || { echo "-c failed: got '$out'"; exit 1; }

out=$(bash mywc.sh -l -w t.txt)
[ "$out" = "3 7" ] || { echo "-l -w failed: got '$out'"; exit 1; }

out=$(bash mywc.sh -w -l t.txt)
[ "$out" = "3 7" ] || { echo "-w -l order failed: got '$out'"; exit 1; }

out=$(bash mywc.sh -lwc t.txt)
[ "$out" = "3 7 32" ] || { echo "-lwc combined failed: got '$out'"; exit 1; }

out=$(bash mywc.sh t.txt)
[ "$out" = "3 7 32" ] || { echo "no flags failed: got '$out'"; exit 1; }

# missing file
if bash mywc.sh -l nope.txt 2>err.txt; then
    echo "expected failure on missing file"; exit 1
fi
grep -q "no such file" err.txt || { echo "missing stderr message"; exit 1; }

echo ok
