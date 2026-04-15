Write a Python script `flatten.py` in the current directory that reads `input.json` and writes `flat.json`.

`input.json` contains a JSON object (possibly nested). Your job is to produce `flat.json` — a flat JSON object whose keys use dot notation to represent the nesting path.

Rules:
- Nested objects: concatenate keys with `.`. Example `{"a": {"b": 1}}` -> `{"a.b": 1}`.
- Arrays: use the integer index in the key path. Example `{"a": [10, 20]}` -> `{"a.0": 10, "a.1": 20}`.
- Leaves are anything that is not a dict or list: string, number, bool, null.
- Empty dicts and empty lists should be preserved as leaf values (i.e., `{"a": {}}` -> `{"a": {}}` and `{"a": []}` -> `{"a": []}`).
- The top-level input is always a JSON object.
- Invoke as `python3 flatten.py` with no arguments. It must read `input.json` and write `flat.json` in the current directory.

Then run it so `flat.json` exists.
