#!/usr/bin/env python3

import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
INDEX_PATH = ROOT / "docs/agent-docs-index.json"
SCHEMA_PATH = ROOT / "docs/schemas/agent-docs-index.schema.json"

REQUIRED_ENTRY_KEYS = {
    "id",
    "topic",
    "intent",
    "entry_doc",
    "related_docs",
    "commands",
    "last_verified_version",
    "scope",
}

REQUIRED_DOC_METADATA = {
    "intent",
    "audience",
    "prereqs",
    "inputs",
    "outputs",
    "related_docs",
    "last_verified_version",
}

KEY_DOCS = [
    ROOT / "docs/index.md",
    ROOT / "docs/admin/installation/install-k0rdent.md",
    ROOT / "docs/admin/installation/verify-install.md",
    ROOT / "docs/quickstarts/quickstart-1-mgmt-node-and-cluster.md",
    ROOT / "docs/troubleshooting/index.md",
    ROOT / "docs/api-specification/index.md",
]


def fail(msg: str) -> None:
    print(f"ERROR: {msg}")


def parse_frontmatter_keys(path: Path) -> set[str]:
    text = path.read_text(encoding="utf-8")
    lines = text.splitlines()
    if not lines or lines[0].strip() != "---":
        return set()

    keys = set()
    for line in lines[1:]:
        if line.strip() == "---":
            break
        if not line.strip() or line.lstrip().startswith("-"):
            continue
        if ":" in line:
            key = line.split(":", 1)[0].strip()
            if key:
                keys.add(key)
    return keys


def main() -> int:
    errors = 0

    if not SCHEMA_PATH.exists():
        fail(f"Missing schema file: {SCHEMA_PATH}")
        errors += 1

    if not INDEX_PATH.exists():
        fail(f"Missing index file: {INDEX_PATH}")
        return 1

    data = json.loads(INDEX_PATH.read_text(encoding="utf-8"))

    for field in ["version", "generated_at", "entries"]:
        if field not in data:
            fail(f"agent-docs-index missing top-level field '{field}'")
            errors += 1

    entries = data.get("entries", [])
    if not isinstance(entries, list) or not entries:
        fail("agent-docs-index entries must be a non-empty array")
        errors += 1
        entries = []

    for i, entry in enumerate(entries):
        missing = REQUIRED_ENTRY_KEYS - set(entry.keys())
        if missing:
            fail(f"entry[{i}] missing keys: {sorted(missing)}")
            errors += 1
            continue

        if entry.get("scope") != "core":
            fail(
                f"entry[{i}] has invalid scope '{entry.get('scope')}', expected 'core'"
            )
            errors += 1

        for key in ["id", "topic", "intent", "entry_doc"]:
            if not isinstance(entry.get(key), str) or not entry[key].strip():
                fail(f"entry[{i}] key '{key}' must be a non-empty string")
                errors += 1

        aliases = entry.get("aliases", [])
        if aliases is not None:
            if not isinstance(aliases, list):
                fail(f"entry[{i}] key 'aliases' must be an array when present")
                errors += 1
            else:
                for alias in aliases:
                    if not isinstance(alias, str) or not alias.strip():
                        fail(f"entry[{i}] aliases contains an invalid value")
                        errors += 1

        entry_doc = ROOT / entry["entry_doc"]
        if not entry_doc.exists():
            fail(f"entry[{i}] entry_doc does not exist: {entry['entry_doc']}")
            errors += 1

        for rel in entry.get("related_docs", []):
            if not isinstance(rel, str):
                fail(f"entry[{i}] related_docs contains non-string value")
                errors += 1
                continue
            rel_path = ROOT / rel
            if not rel_path.exists():
                fail(f"entry[{i}] related_doc does not exist: {rel}")
                errors += 1

        for cmd in entry.get("commands", []):
            if not isinstance(cmd, str):
                fail(f"entry[{i}] commands contains non-string value")
                errors += 1

        flattened = " ".join(
            [
                entry.get("id", ""),
                entry.get("topic", ""),
                entry.get("intent", ""),
                entry.get("entry_doc", ""),
                " ".join(entry.get("related_docs", [])),
            ]
        ).lower()
        if "kof" in flattened:
            fail(f"entry[{i}] contains excluded component reference 'kof'")
            errors += 1

    for doc in KEY_DOCS:
        if not doc.exists():
            fail(f"Missing required key doc for metadata check: {doc}")
            errors += 1
            continue
        keys = parse_frontmatter_keys(doc)
        missing = REQUIRED_DOC_METADATA - keys
        if missing:
            fail(f"{doc.relative_to(ROOT)} missing metadata keys: {sorted(missing)}")
            errors += 1

    if errors:
        print(f"docs-agent-check failed with {errors} error(s)")
        return 1

    print("docs-agent-check passed")
    return 0


if __name__ == "__main__":
    sys.exit(main())
