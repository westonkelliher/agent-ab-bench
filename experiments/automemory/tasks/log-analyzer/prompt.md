The current directory contains a small Python log-analyzer project with the following layout:

```
analyzer/
  __init__.py
  parser.py     # parses log lines into records
  stats.py      # computes per-level counts
  cli.py        # command-line entry point
main.py         # thin wrapper: python3 main.py <logfile> [--since YYYY-MM-DDTHH:MM:SS]
tests/
  test_parser.py
  test_stats.py
sample.log
```

Run `python3 tests/test_parser.py` and `python3 tests/test_stats.py` first to see the current state. (Plain-Python tests — no pytest required.) You must make TWO changes:

1. **Fix a bug in `analyzer/parser.py`.** The parser is supposed to accept log lines of the form:

   ```
   2024-06-01T12:34:56 LEVEL message text here
   ```

   where `LEVEL` is one of `DEBUG`, `INFO`, `WARN`, `ERROR`. The current parser has a bug that makes it drop or misparse some valid lines. The existing tests in `tests/test_parser.py` describe the expected behavior.

2. **Add a `--since` filter** to the CLI (`analyzer/cli.py` and wired through `main.py`). When `--since YYYY-MM-DDTHH:MM:SS` is passed, only records with a timestamp strictly greater than or equal to that value should be counted and printed. Without `--since`, all records are included (current behavior).

The CLI output format (do not change it other than to honor the filter) is one line per level in the fixed order `DEBUG INFO WARN ERROR`, like:

```
DEBUG 2
INFO 5
WARN 1
ERROR 0
```

All existing tests must still pass (`python3 tests/test_parser.py` and `python3 tests/test_stats.py`), and the new behavior must work when invoked as `python3 main.py sample.log --since 2024-06-01T12:00:00`.
