Implement a minimal INI file parser in Python.

Create a file `ini_parser.py` in the current directory exposing a single function:

```python
def parse_ini(text: str) -> dict:
    ...
```

Rules:
- Input is the text of an INI file. Output is a dict mapping section name (str) to a dict of key->value (both str).
- Sections are introduced by a line `[section-name]`. Keys before any section header belong to section `""` (empty string).
- Key/value lines look like `key = value` or `key=value`. Whitespace around `key` and `value` is stripped.
- Lines that are empty or whose first non-whitespace character is `;` or `#` are comments and must be ignored.
- Values may contain `=` characters; only the first `=` separates key from value.
- If a section header appears more than once, later keys merge into the same section dict (later keys overwrite earlier ones with the same name).
- Do not use the `configparser` module.

The file must be importable as `from ini_parser import parse_ini`.
