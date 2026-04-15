#!/usr/bin/env bash
set -e
test -f todo.py
rm -f todo.json

run() { python3 todo.py "$@"; }

out=$(run add buy milk); [ "$out" = "added 1" ] || { echo "add1: $out"; exit 1; }
out=$(run add write report); [ "$out" = "added 2" ] || { echo "add2: $out"; exit 1; }
out=$(run add "walk the dog"); [ "$out" = "added 3" ] || { echo "add3: $out"; exit 1; }

# list open
out=$(run list)
expected=$'1\topen\tbuy milk\n2\topen\twrite report\n3\topen\twalk the dog'
[ "$out" = "$expected" ] || { echo "list failed:"; echo "$out"; echo "---"; echo "$expected"; exit 1; }

# mark done
out=$(run done 2); [ "$out" = "done 2" ] || { echo "done: $out"; exit 1; }

# list open hides done
out=$(run list)
expected=$'1\topen\tbuy milk\n3\topen\twalk the dog'
[ "$out" = "$expected" ] || { echo "list-after-done: $out"; exit 1; }

# list --all shows all in id order
out=$(run list --all)
expected=$'1\topen\tbuy milk\n2\tdone\twrite report\n3\topen\twalk the dog'
[ "$out" = "$expected" ] || { echo "list-all: $out"; exit 1; }

# remove
out=$(run rm 1); [ "$out" = "removed 1" ] || { echo "rm: $out"; exit 1; }

# id not reused: next add should be 4
out=$(run add new task); [ "$out" = "added 4" ] || { echo "id reuse: $out"; exit 1; }

# error cases
if run done 999 2>err.txt; then echo "expected done fail"; exit 1; fi
grep -q "no such task" err.txt || { echo "done error msg missing"; exit 1; }

if run rm 999 2>err.txt; then echo "expected rm fail"; exit 1; fi
grep -q "no such task" err.txt || { echo "rm error msg missing"; exit 1; }

# unknown subcommand exits 2
set +e
run bogus 2>/dev/null
rc=$?
set -e
[ "$rc" = "2" ] || { echo "unknown subcmd rc=$rc"; exit 1; }

# persistence: fresh process sees state
out=$(run list --all)
expected=$'2\tdone\twrite report\n3\topen\twalk the dog\n4\topen\tnew task'
[ "$out" = "$expected" ] || { echo "persist: $out"; exit 1; }

echo ok
