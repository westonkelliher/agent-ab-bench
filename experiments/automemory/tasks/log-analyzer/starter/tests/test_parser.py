"""Plain-Python tests. Run with: python3 tests/test_parser.py"""
import os
import sys
import tempfile
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from analyzer.parser import parse_line, parse_file


def test_parse_simple():
    r = parse_line("2024-06-01T12:34:56 INFO hello")
    assert r is not None
    assert r.ts == datetime(2024, 6, 1, 12, 34, 56)
    assert r.level == "INFO"
    assert r.message == "hello"


def test_parse_multiword_message():
    r = parse_line("2024-06-01T12:34:56 ERROR connection refused by peer")
    assert r is not None
    assert r.level == "ERROR"
    assert r.message == "connection refused by peer", repr(r.message)


def test_parse_bad_level():
    assert parse_line("2024-06-01T12:34:56 TRACE nope") is None


def test_parse_bad_timestamp():
    assert parse_line("not-a-ts INFO msg") is None


def test_parse_blank():
    assert parse_line("") is None
    assert parse_line("   ") is None


def test_parse_file():
    with tempfile.TemporaryDirectory() as td:
        p = os.path.join(td, "x.log")
        with open(p, "w") as f:
            f.write(
                "2024-06-01T10:00:00 INFO starting up\n"
                "2024-06-01T10:00:01 DEBUG loading config file\n"
                "2024-06-01T10:00:02 WARN disk space low\n"
                "bogus line\n"
                "2024-06-01T10:00:03 ERROR failed to open socket\n"
            )
        recs = parse_file(p)
        assert len(recs) == 4, len(recs)
        assert recs[0].message == "starting up", repr(recs[0].message)
        assert recs[1].message == "loading config file", repr(recs[1].message)
        assert recs[2].message == "disk space low"
        assert recs[3].message == "failed to open socket"


def main():
    tests = [v for k, v in globals().items() if k.startswith("test_") and callable(v)]
    failed = 0
    for t in tests:
        try:
            t()
            print(f"PASS {t.__name__}")
        except Exception as e:
            failed += 1
            print(f"FAIL {t.__name__}: {e}")
    if failed:
        sys.exit(1)
    print(f"ok ({len(tests)} tests)")


if __name__ == "__main__":
    main()
