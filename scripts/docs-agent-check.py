#!/usr/bin/env python3

import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
INDEX_PATH = ROOT / "docs/agent-docs-index.json"
SCHEMA_PATH = ROOT / "docs/schemas/agent-docs-index.schema.json"
METADATA_REQUIRED_PATH = ROOT / "docs/metadata-required.json"

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


def parse_frontmatter_fields(path: Path) -> dict[str, str]:
    text = path.read_text(encoding="utf-8")
    lines = text.splitlines()
    if not lines or lines[0].strip() != "---":
        return {}

    fields: dict[str, str] = {}
    for line in lines[1:]:
        if line.strip() == "---":
            break
        if not line.strip() or line.lstrip().startswith("-"):
            continue
        if ":" in line:
            key, val = line.split(":", 1)
            key = key.strip()
            if key:
                fields[key] = val.strip()
    return fields


def related_docs_are_repo_relative(value: str) -> bool:
    docs = [v.strip() for v in value.split(",") if v.strip()]
    if not docs:
        return False
    return all(d.startswith("docs/") for d in docs)


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
        fields = parse_frontmatter_fields(doc)
        keys = set(fields.keys())
        missing = REQUIRED_DOC_METADATA - keys
        if missing:
            fail(f"{doc.relative_to(ROOT)} missing metadata keys: {sorted(missing)}")
            errors += 1

    if METADATA_REQUIRED_PATH.exists():
        required_payload = json.loads(METADATA_REQUIRED_PATH.read_text(encoding="utf-8"))
        required_keys = required_payload.get("required_keys", [])
        required_files = required_payload.get("files", [])

        if not isinstance(required_keys, list) or not all(
            isinstance(k, str) for k in required_keys
        ):
            fail("docs/metadata-required.json required_keys must be an array of strings")
            errors += 1
            required_keys = []

        if not isinstance(required_files, list) or not all(
            isinstance(f, str) for f in required_files
        ):
            fail("docs/metadata-required.json files must be an array of strings")
            errors += 1
            required_files = []

        required_key_set = set(required_keys)

        for rel_path in required_files:
            abs_path = ROOT / rel_path
            if not abs_path.exists():
                fail(f"metadata-required file does not exist: {rel_path}")
                errors += 1
                continue

            fields = parse_frontmatter_fields(abs_path)
            if not fields:
                fail(f"{rel_path} is missing frontmatter")
                errors += 1
                continue

            missing = required_key_set - set(fields.keys())
            if missing:
                fail(f"{rel_path} missing metadata-required keys: {sorted(missing)}")
                errors += 1

            related_docs = fields.get("related_docs", "")
            if not related_docs_are_repo_relative(related_docs):
                fail(f"{rel_path} has non-compliant related_docs; use docs/... paths")
                errors += 1

    if errors:
        print(f"docs-agent-check failed with {errors} error(s)")
        return 1

    print("docs-agent-check passed")
    return 0


if __name__ == "__main__":
    sys.exit(main())
