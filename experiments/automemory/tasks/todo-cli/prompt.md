Build a small todo list CLI in Python.

Create a script `todo.py` in the current directory. It must be invokable as `python3 todo.py <subcommand> [args]` and persist state in a file `todo.json` in the current directory (create if missing).

Subcommands:

1. `add <text...>`: add a new task. `<text...>` may contain multiple arguments (join with single spaces). Assign an integer id that is 1 more than the maximum existing id (or 1 if empty). New tasks are `open`. Print `added <id>` on success.

2. `list [--all]`: by default, print only `open` tasks. With `--all`, print open and done tasks. Output format: one task per line, `<id>\t<status>\t<text>` where status is literally `open` or `done`. Tasks must be printed in ascending id order. No header. If there are zero tasks to print, print nothing.

3. `done <id>`: mark the task with that id as `done`. If the id does not exist, print `no such task: <id>` to stderr and exit 1. On success print `done <id>`.

4. `rm <id>`: remove the task with that id entirely. Same error behavior as `done`. On success print `removed <id>`.

5. Unknown subcommands or missing required args: print a usage message to stderr and exit 2.

The `todo.json` file format is up to you, but it must round-trip across invocations. Ids of removed tasks must NOT be reused.
