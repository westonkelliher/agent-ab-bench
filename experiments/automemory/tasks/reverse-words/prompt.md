Write a bash script `revwords.sh` in the current directory. It reads lines from stdin and prints, for each input line, one output line with that line's words in reverse order (words separated by single spaces). Each output line must be terminated by a newline. Preserve line order. Empty input lines become empty output lines (still terminated by a newline). Make the script executable.

Example: given stdin `hello world foo\nthe quick brown fox\n`, the output must be exactly `foo world hello\nfox brown quick the\n`.
