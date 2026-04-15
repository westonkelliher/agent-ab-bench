Write a bash script `mywc.sh` in the current directory that mimics a subset of `wc`.

Requirements:
- Usage: `bash mywc.sh [-l] [-w] [-c] FILE`
- Exactly one file argument (the last argument). Flags may appear in any order and may be combined like `-lw`.
- `-l` prints line count, `-w` prints word count (whitespace-separated), `-c` prints byte count.
- If multiple flags are given, print their counts in the order `lines words bytes` (always that order, regardless of flag order), separated by single spaces, followed by a newline.
- If no flags are given, behave as if `-l -w -c` was passed.
- Output must be ONLY the numbers and a trailing newline — no filename, no leading whitespace.
- If the file does not exist, print `mywc.sh: FILE: no such file` to stderr and exit with status 1.
- You may NOT invoke the real `wc` command. Use bash builtins or other tools (awk, etc.).

The file `sample.txt` is provided in the current directory for your own testing.
