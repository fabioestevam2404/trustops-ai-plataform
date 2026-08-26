import json
import logging

from app.core.logging import JsonFormatter


def _make_record(**extra: object) -> logging.LogRecord:
    record = logging.LogRecord(
        name="app.test",
        level=logging.INFO,
        pathname=__file__,
        lineno=1,
        msg="something happened",
        args=(),
        exc_info=None,
    )
    for key, value in extra.items():
        setattr(record, key, value)
    return record


def test_json_formatter_produces_valid_json_with_core_fields() -> None:
    formatted = JsonFormatter().format(_make_record())
    payload = json.loads(formatted)
    assert payload["level"] == "INFO"
    assert payload["logger"] == "app.test"
    assert payload["message"] == "something happened"
    assert "timestamp" in payload


def test_json_formatter_includes_extra_fields() -> None:
    formatted = JsonFormatter().format(_make_record(assessment_id="a1", tool="ruff"))
    payload = json.loads(formatted)
    assert payload["assessment_id"] == "a1"
    assert payload["tool"] == "ruff"
