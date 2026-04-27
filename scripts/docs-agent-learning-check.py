#!/usr/bin/env python3

import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent

FAILURE_LOG_PATH = ROOT / "docs/agent-learning/failure-log.jsonl"
TRIAGE_PATH = ROOT / "docs/agent-learning/triage-queue.json"
PROPOSALS_PATH = ROOT / "docs/agent-learning/proposals.json"

SCHEMA_FILES = [
    ROOT / "docs/agent-learning/schemas/failure-log-entry.schema.json",
    ROOT / "docs/agent-learning/schemas/triage-queue.schema.json",
    ROOT / "docs/agent-learning/schemas/proposals.schema.json",
]

REQUIRED_FAILURE_KEYS = {
    "event_id",
    "timestamp",
    "source",
    "query",
    "matched_route",
    "confidence",
    "acceptable",
    "expected_routes",
    "scope_violation",
    "run_id",
}


def err(msg: str) -> None:
    print(f"ERROR: {msg}")


def load_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def check_schema_files() -> int:
    errors = 0
    for path in SCHEMA_FILES:
        if not path.exists():
            err(f"missing schema file: {path}")
            errors += 1
            continue
        try:
            payload = load_json(path)
        except Exception as exc:  # noqa: BLE001
            err(f"failed to parse schema {path}: {exc}")
            errors += 1
            continue
        if "$schema" not in payload or "title" not in payload:
            err(f"schema missing required metadata fields: {path}")
            errors += 1
    return errors


def check_failure_log() -> int:
    if not FAILURE_LOG_PATH.exists():
        err(f"missing failure log file: {FAILURE_LOG_PATH}")
        return 1

    errors = 0
    lines = FAILURE_LOG_PATH.read_text(encoding="utf-8").splitlines()
    if not lines:
        err("failure-log.jsonl is empty")
        return 1

    for i, line in enumerate(lines, start=1):
        if not line.strip():
            continue
        try:
            obj = json.loads(line)
        except Exception as exc:  # noqa: BLE001
            err(f"failure-log line {i} invalid JSON: {exc}")
            errors += 1
            continue

        missing = REQUIRED_FAILURE_KEYS - set(obj.keys())
        if missing:
            err(f"failure-log line {i} missing keys: {sorted(missing)}")
            errors += 1

        if obj.get("source") not in {"shadow", "golden", "runtime"}:
            err(f"failure-log line {i} has invalid source: {obj.get('source')}")
            errors += 1

    return errors


def check_triage() -> int:
    if not TRIAGE_PATH.exists():
        err(f"missing triage queue file: {TRIAGE_PATH}")
        return 1

    errors = 0
    data = load_json(TRIAGE_PATH)
    if not isinstance(data, dict):
        err("triage-queue.json must be an object")
        return 1

    if "version" not in data or "items" not in data:
        err("triage-queue.json missing required fields: version/items")
        errors += 1
    if not isinstance(data.get("items", []), list):
        err("triage-queue.json items must be an array")
        errors += 1

    return errors


def check_proposals() -> int:
    if not PROPOSALS_PATH.exists():
        err(f"missing proposals file: {PROPOSALS_PATH}")
        return 1

    errors = 0
    data = load_json(PROPOSALS_PATH)
    if not isinstance(data, dict):
        err("proposals.json must be an object")
        return 1

    if "version" not in data or "proposals" not in data:
        err("proposals.json missing required fields: version/proposals")
        errors += 1
    if not isinstance(data.get("proposals", []), list):
        err("proposals.json proposals must be an array")
        errors += 1

    return errors


def main() -> int:
    errors = 0
    errors += check_schema_files()
    errors += check_failure_log()
    errors += check_triage()
    errors += check_proposals()

    if errors:
        print(f"docs-agent-learning-check failed with {errors} error(s)")
        return 1

    print("docs-agent-learning-check passed")
    return 0


if __name__ == "__main__":
    sys.exit(main())
