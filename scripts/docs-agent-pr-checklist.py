#!/usr/bin/env python3

import json
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
PROPOSALS = ROOT / "docs/agent-learning/proposals.json"
OUTPUT = ROOT / "docs/agent-learning/pr-checklist.md"


def main() -> int:
    if not PROPOSALS.exists():
        print(f"ERROR: missing proposals file: {PROPOSALS}")
        return 1

    payload = json.loads(PROPOSALS.read_text(encoding="utf-8"))
    proposals = payload.get("proposals", [])

    pending = [
        p
        for p in proposals
        if p.get("status") == "approved" and not p.get("applied", {}).get("applied_in_commit")
    ]

    grouped = defaultdict(list)
    for p in pending:
        grouped[p.get("type", "unknown")].append(p)

    now = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    lines = []
    lines.append(f"# PR Checklist from Approved Proposals ({now})")
    lines.append("")
    lines.append(f"Approved pending proposals: {len(pending)}")
    lines.append("")

    sections = [
        ("add_alias", "Alias additions"),
        ("adjust_route_scoring", "Scoring adjustments"),
        ("doc_update", "Doc updates"),
        ("test_update", "Test updates"),
    ]

    for key, title in sections:
        lines.append(f"## {title}")
        items = grouped.get(key, [])
        if not items:
            lines.append("- (none)")
            lines.append("")
            continue

        for p in sorted(items, key=lambda x: x.get("score", 0), reverse=True):
            pid = p.get("proposal_id", "unknown")
            target = p.get("target", {}).get("id", "unknown")
            rationale = p.get("rationale", "")
            lines.append(f"- [ ] {pid} `{key}` -> `{target}` - {rationale}")
        lines.append("")

    lines.append("## Validation")
    lines.append("")
    lines.append("- [ ] make docs-check")
    lines.append("- [ ] make docs-shadow-report")
    lines.append("- [ ] make docs-build")
    lines.append("")

    OUTPUT.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"Wrote checklist: {OUTPUT.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
