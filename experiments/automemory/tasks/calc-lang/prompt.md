Implement a tiny stack-based calculator language.

Create a script `calc.py` in the current directory. It reads a program from a file given as its first argument:

```
python3 calc.py program.calc
```

The program is a sequence of lines. Each line is one command. Blank lines and lines whose first non-whitespace character is `#` are comments and must be ignored. Whitespace around tokens should be tolerated.

The interpreter has:
- an integer stack (initially empty),
- a dict of named variables (initially empty).

Commands:

1. `PUSH <int>` — push an integer literal (may be negative) onto the stack.
2. `POP` — pop and discard the top of the stack.
3. `ADD` — pop two values `b` then `a`, push `a + b`.
4. `SUB` — pop two values `b` then `a`, push `a - b`.
5. `MUL` — pop two values `b` then `a`, push `a * b`.
6. `STORE <name>` — pop the top of the stack and store it in variable `<name>`.
7. `LOAD <name>` — push the value of variable `<name>` onto the stack.
8. `PRINT` — pop the top of the stack and print it on its own line to stdout.
9. `DUP` — duplicate the top of the stack.

Error behavior:
- If a command tries to pop from an empty stack, print `error: stack underflow` to stderr and exit with status 1.
- If `LOAD` references an unknown variable, print `error: unknown variable <name>` to stderr and exit 1.
- If a command name is unrecognized, print `error: unknown command <name>` to stderr and exit 1.

On successful completion (end of program), exit 0. Final stack/variable state does not need to be printed.
