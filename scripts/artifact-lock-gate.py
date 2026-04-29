#!/usr/bin/env python3

import argparse
import re
import sys
from pathlib import Path


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate artifact lock strict gate checks")
    parser.add_argument("lock_path", help="Path to artifact-lock.yaml")
    parser.add_argument(
        "--allow-registry",
        action="append",
        default=[],
        help="Allowed registry hostname (repeatable)",
    )
    args = parser.parse_args()

    lock_file = Path(args.lock_path)
    if not lock_file.is_file():
        print(f"ERROR: missing lock file: {lock_file}")
        return 2

    text = lock_file.read_text(encoding="utf-8")
    lines = text.splitlines()

    placeholders = [ln for ln in lines if "REPLACE_WITH_REAL" in ln]
    refs = []
    digests = []
    for line in lines:
        ref_match = re.search(r"\bref:\s*(\S+)", line)
        if ref_match:
            refs.append(ref_match.group(1).strip())
        digest_match = re.search(r"\bdigest:\s*(\S+)", line)
        if digest_match:
            digests.append(digest_match.group(1).strip())

    allowed = set(args.allow_registry)
    disallowed_refs = []
    for ref in refs:
        raw = ref[6:] if ref.startswith("oci://") else ref
        host = raw.split("/", 1)[0]
        if allowed and host not in allowed:
            disallowed_refs.append((ref, host))

    invalid_digests = [d for d in digests if not re.match(r"^sha256:[0-9a-fA-F]{64}$", d)]

    print(f"lock_path={lock_file}")
    print(f"placeholder_matches={len(placeholders)}")
    print(f"refs_total={len(refs)}")
    print(f"digests_total={len(digests)}")
    print(f"invalid_digest_format={len(invalid_digests)}")
    print(f"disallowed_refs={len(disallowed_refs)}")

    if placeholders:
        print("\nPlaceholder entries:")
        for line in placeholders:
            print(f"- {line.strip()}")

    if invalid_digests:
        print("\nInvalid digest format entries:")
        for digest in invalid_digests:
            print(f"- {digest}")

    if disallowed_refs:
        print("\nDisallowed registry refs:")
        for ref, host in disallowed_refs:
            print(f"- {ref} (host={host})")

    failed = bool(placeholders or invalid_digests or disallowed_refs)
    print(f"\nstrict_gate={'fail' if failed else 'pass'}")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
