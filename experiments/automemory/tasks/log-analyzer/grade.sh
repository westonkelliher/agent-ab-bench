#!/usr/bin/env bash
set -e
test -f main.py
test -f analyzer/parser.py
test -f analyzer/cli.py

python3 tests/test_parser.py
python3 tests/test_stats.py

# No --since: count everything in sample.log
out=$(python3 main.py sample.log)
expected=$'DEBUG 2\nINFO 3\nWARN 1\nERROR 1'
[ "$out" = "$expected" ] || { echo "no-since:"; echo "$out"; echo "---"; echo "$expected"; exit 1; }

# --since at 12:00:00 -> includes records >= 12:00:00
out=$(python3 main.py sample.log --since 2024-06-01T12:00:00)
expected=$'DEBUG 1\nINFO 2\nWARN 0\nERROR 1'
[ "$out" = "$expected" ] || { echo "since-12:"; echo "$out"; echo "---"; echo "$expected"; exit 1; }

# --since in the future -> all zero
out=$(python3 main.py sample.log --since 2030-01-01T00:00:00)
expected=$'DEBUG 0\nINFO 0\nWARN 0\nERROR 0'
[ "$out" = "$expected" ] || { echo "since-future:"; echo "$out"; exit 1; }

echo ok
