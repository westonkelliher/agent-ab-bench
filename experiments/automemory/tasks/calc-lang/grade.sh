#!/usr/bin/env bash
set -e
test -f calc.py

cat > p1.calc <<'EOF'
# simple arithmetic
PUSH 3
PUSH 4
ADD
PRINT
EOF
out=$(python3 calc.py p1.calc)
[ "$out" = "7" ] || { echo "p1: $out"; exit 1; }

cat > p2.calc <<'EOF'
PUSH 10
PUSH 3
SUB
PRINT
PUSH 6
PUSH 7
MUL
PRINT
EOF
out=$(python3 calc.py p2.calc)
expected=$'7\n42'
[ "$out" = "$expected" ] || { echo "p2: $out"; exit 1; }

cat > p3.calc <<'EOF'
# variables
PUSH 5
STORE x
PUSH 10
STORE y
LOAD x
LOAD y
ADD
PRINT
LOAD x
DUP
MUL
PRINT
EOF
out=$(python3 calc.py p3.calc)
expected=$'15\n25'
[ "$out" = "$expected" ] || { echo "p3: $out"; exit 1; }

cat > p4.calc <<'EOF'

   # leading blank and indented comment
PUSH  1
   PUSH 2
ADD
   PRINT
POP
EOF
out=$(python3 calc.py p4.calc 2>&1)
[ "$out" = "3" ] || { echo "p4: $out"; exit 1; }

# underflow
cat > p5.calc <<'EOF'
POP
EOF
if python3 calc.py p5.calc 2>err.txt; then echo "expected fail"; exit 1; fi
grep -q "stack underflow" err.txt || { echo "underflow msg missing"; exit 1; }

# unknown var
cat > p6.calc <<'EOF'
LOAD z
EOF
if python3 calc.py p6.calc 2>err.txt; then echo "expected fail"; exit 1; fi
grep -q "unknown variable" err.txt || { echo "unknown var msg missing"; exit 1; }

# unknown command
cat > p7.calc <<'EOF'
FOO
EOF
if python3 calc.py p7.calc 2>err.txt; then echo "expected fail"; exit 1; fi
grep -q "unknown command" err.txt || { echo "unknown cmd msg missing"; exit 1; }

# negative literal
cat > p8.calc <<'EOF'
PUSH -5
PUSH 3
ADD
PRINT
EOF
out=$(python3 calc.py p8.calc)
[ "$out" = "-2" ] || { echo "p8: $out"; exit 1; }

echo ok
