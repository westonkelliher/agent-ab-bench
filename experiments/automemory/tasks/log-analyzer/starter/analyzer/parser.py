from datetime import datetime

LEVELS = ("DEBUG", "INFO", "WARN", "ERROR")


class LogRecord:
    def __init__(self, ts: datetime, level: str, message: str):
        self.ts = ts
        self.level = level
        self.message = message

    def __repr__(self):
        return f"LogRecord({self.ts.isoformat()}, {self.level}, {self.message!r})"


def parse_line(line: str):
    """Parse a single log line. Return a LogRecord or None if malformed."""
    line = line.rstrip("\n")
    if not line.strip():
        return None
    # BUG: whitespace split without maxsplit drops the rest of the message
    # beyond the third token.
    parts = line.split()
    if len(parts) < 3:
        return None
    ts_str, level, message = parts[0], parts[1], parts[2]
    if level not in LEVELS:
        return None
    try:
        ts = datetime.strptime(ts_str, "%Y-%m-%dT%H:%M:%S")
    except ValueError:
        return None
    return LogRecord(ts, level, message)


def parse_file(path: str):
    records = []
    with open(path) as f:
        for line in f:
            rec = parse_line(line)
            if rec is not None:
                records.append(rec)
    return records
