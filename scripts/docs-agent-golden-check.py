#!/usr/bin/env python3

import json
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
INDEX_PATH = ROOT / "docs/agent-docs-index.json"
GOLDEN_PATH = ROOT / "docs/golden-queries.json"
ROUTER_PATH = ROOT / "scripts/docs-agent-route.py"


def fail(msg: str) -> None:
    print(f"ERROR: {msg}")


def run_route(query: str, topic: str | None) -> tuple[dict, str]:
    cmd = ["python3", str(ROUTER_PATH), "--intent", query, "--limit", "3"]
    if topic:
        cmd.extend(["--topic", topic])
    cp = subprocess.run(cmd, cwd=ROOT, text=True, capture_output=True)
    if cp.returncode != 0:
        raise RuntimeError(cp.stderr.strip() or cp.stdout.strip() or "route command failed")
    return json.loads(cp.stdout), cp.stdout


def main() -> int:
    errors = 0

    if not INDEX_PATH.exists():
        fail(f"Missing agent index: {INDEX_PATH}")
        return 1
    if not GOLDEN_PATH.exists():
        fail(f"Missing golden queries: {GOLDEN_PATH}")
        return 1
    if not ROUTER_PATH.exists():
        fail(f"Missing route helper: {ROUTER_PATH}")
        return 1

    index = json.loads(INDEX_PATH.read_text(encoding="utf-8"))
    valid_ids = {e.get("id") for e in index.get("entries", [])}

    golden = json.loads(GOLDEN_PATH.read_text(encoding="utf-8"))
    cases = golden.get("cases", [])
    if not isinstance(cases, list) or not cases:
        fail("golden-queries.json must contain a non-empty 'cases' array")
        return 1

    passed = 0
    failed_rows = []

    for i, case in enumerate(cases, start=1):
        query = case.get("query")
        expected = case.get("expected_top")
        mode = case.get("mode", "strict")
        topic = case.get("topic", "")
        allowed = case.get("allowed_alternatives", [])

        if not query or not expected:
            errors += 1
            failed_rows.append((i, query, "case-metadata", "missing query/expected_top"))
            continue
        if expected not in valid_ids:
            errors += 1
            failed_rows.append((i, query, "case-metadata", f"expected_top '{expected}' not in index"))
            continue
        for alt in allowed:
            if alt not in valid_ids:
                errors += 1
                failed_rows.append((i, query, "case-metadata", f"alternative '{alt}' not in index"))
                continue

        try:
            result, _ = run_route(query, topic)
        except Exception as exc:  # noqa: BLE001
            errors += 1
            failed_rows.append((i, query, "route-exec", str(exc)))
            continue

        match = result.get("match", {})
        matched_id = match.get("id")
        if not matched_id:
            errors += 1
            failed_rows.append((i, query, "route-result", "no matched route id"))
            continue

        flattened = " ".join(
            [
                str(match.get("id", "")),
                str(match.get("topic", "")),
                str(match.get("intent", "")),
                str(match.get("entry_doc", "")),
            ]
        ).lower()
        if "kof" in flattened:
            errors += 1
            failed_rows.append((i, query, matched_id, "matched excluded 'kof' route"))
            continue

        if match.get("scope") != "core":
            errors += 1
            failed_rows.append((i, query, matched_id, "matched non-core scope route"))
            continue

        accepted = {expected} | set(allowed)
        if mode == "strict":
            if matched_id != expected:
                errors += 1
                failed_rows.append(
                    (i, query, matched_id, f"strict mismatch, expected '{expected}'")
                )
                continue
        else:
            if matched_id not in accepted:
                errors += 1
                failed_rows.append(
                    (i, query, matched_id, f"lenient mismatch, expected one of {sorted(accepted)}")
                )
                continue

        passed += 1

    total = len(cases)
    print(f"docs-agent-golden-check: passed {passed}/{total}")
    if failed_rows:
        print("Failures:")
        for row in failed_rows:
            print(f"- case#{row[0]} query='{row[1]}' matched='{row[2]}' reason={row[3]}")
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
