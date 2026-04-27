#!/usr/bin/env python3

import argparse
import json
import subprocess
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
INDEX_PATH = ROOT / "docs/agent-docs-index.json"


def route_query(query: str, topic: str, limit: int = 3) -> dict:
    cmd = [
        "python3",
        str(ROOT / "scripts/docs-agent-route.py"),
        "--intent",
        query,
        "--limit",
        str(limit),
    ]
    if topic:
        cmd.extend(["--topic", topic])
    cp = subprocess.run(cmd, cwd=ROOT, text=True, capture_output=True)
    if cp.returncode != 0:
        raise RuntimeError(cp.stderr.strip() or cp.stdout.strip() or "route command failed")
    return json.loads(cp.stdout)


def get_commit_sha() -> str:
    cp = subprocess.run(
        ["git", "rev-parse", "--short", "HEAD"], cwd=ROOT, text=True, capture_output=True
    )
    if cp.returncode != 0:
        return "unknown"
    return cp.stdout.strip()


def fail(msg: str) -> int:
    print(f"ERROR: {msg}")
    return 1


def validate_shadow_input(payload: dict) -> list[str]:
    errs = []
    if not isinstance(payload, dict):
        return ["input must be a JSON object"]
    if "version" not in payload:
        errs.append("missing top-level field: version")
    if "cases" not in payload:
        errs.append("missing top-level field: cases")
        return errs
    if not isinstance(payload["cases"], list) or not payload["cases"]:
        errs.append("cases must be a non-empty array")
        return errs

    for i, case in enumerate(payload["cases"], start=1):
        if not isinstance(case, dict):
            errs.append(f"case {i}: must be an object")
            continue
        for key in ["query", "expected_area", "acceptable_routes", "priority"]:
            if key not in case:
                errs.append(f"case {i}: missing field '{key}'")
        if "query" in case and not isinstance(case["query"], str):
            errs.append(f"case {i}: query must be string")
        if "expected_area" in case and not isinstance(case["expected_area"], str):
            errs.append(f"case {i}: expected_area must be string")
        if "acceptable_routes" in case:
            ar = case["acceptable_routes"]
            if not isinstance(ar, list) or not ar:
                errs.append(f"case {i}: acceptable_routes must be non-empty array")
            elif any(not isinstance(x, str) for x in ar):
                errs.append(f"case {i}: acceptable_routes must contain strings")
    return errs


def validate_report_shape(report: dict) -> list[str]:
    required_top = {
        "version",
        "generated_at",
        "commit_sha",
        "input_file",
        "summary",
        "category_stats",
        "cases",
        "failures",
        "low_confidence",
    }
    errs = []
    missing = required_top - set(report.keys())
    if missing:
        errs.append(f"report missing fields: {sorted(missing)}")
    return errs


def main() -> int:
    parser = argparse.ArgumentParser(description="Generate report-only shadow routing results")
    parser.add_argument("--input", default="docs/shadow-queries.json")
    parser.add_argument("--output", default="")
    parser.add_argument("--json-output", default="")
    parser.add_argument("--low-confidence-threshold", type=float, default=4.5)
    args = parser.parse_args()

    input_path = ROOT / args.input
    if not input_path.exists():
        return fail(f"missing input file: {input_path}")

    if not INDEX_PATH.exists():
        return fail(f"missing route index: {INDEX_PATH}")

    now = datetime.now(timezone.utc)
    date_tag = now.strftime("%Y-%m-%d")
    output_path = ROOT / (args.output or f"docs/reports/agent-shadow-report-{date_tag}.md")
    json_output_path = ROOT / (
        args.json_output or f"docs/reports/agent-shadow-report-{date_tag}.json"
    )

    output_path.parent.mkdir(parents=True, exist_ok=True)
    json_output_path.parent.mkdir(parents=True, exist_ok=True)

    shadow_data = json.loads(input_path.read_text(encoding="utf-8"))
    input_errors = validate_shadow_input(shadow_data)
    if input_errors:
        return fail("; ".join(input_errors))

    index = json.loads(INDEX_PATH.read_text(encoding="utf-8"))
    valid_route_ids = {e.get("id") for e in index.get("entries", [])}

    case_results = []
    failures = []
    low_confidence = []
    out_of_scope_matches = 0
    missing_route_ids = 0

    area_counts = defaultdict(int)
    area_acceptable = defaultdict(int)

    for i, case in enumerate(shadow_data["cases"], start=1):
        query = case["query"]
        topic = case.get("topic", "")
        expected_area = case["expected_area"]
        acceptable_routes = case["acceptable_routes"]

        area_counts[expected_area] += 1

        try:
            routed = route_query(query, topic)
            match = routed.get("match", {})
            top_route = match.get("id", "")
            confidence = float(routed.get("confidence", 0.0))
            scope = match.get("scope", "")
        except Exception as exc:  # noqa: BLE001
            top_route = ""
            confidence = 0.0
            scope = ""
            failures.append(
                {
                    "index": i,
                    "query": query,
                    "expected_routes": acceptable_routes,
                    "actual_route": "",
                    "confidence": 0.0,
                    "reason": f"routing error: {exc}",
                    "recommended_fix": "Inspect route helper execution and query formatting"
                }
            )

        acceptable = top_route in acceptable_routes
        alternative_used = acceptable and top_route != acceptable_routes[0]

        if top_route not in valid_route_ids:
            missing_route_ids += 1

        flattened = f"{top_route} {scope}".lower()
        if "kof" in flattened or (scope and scope != "core"):
            out_of_scope_matches += 1

        if acceptable:
            area_acceptable[expected_area] += 1
        else:
            failures.append(
                {
                    "index": i,
                    "query": query,
                    "expected_routes": acceptable_routes,
                    "actual_route": top_route,
                    "confidence": confidence,
                    "reason": "top route not in acceptable routes",
                    "recommended_fix": "Add alias or adjust route scoring for this intent"
                }
            )

        if confidence < args.low_confidence_threshold:
            low_confidence.append(
                {
                    "index": i,
                    "query": query,
                    "route": top_route,
                    "confidence": confidence,
                }
            )

        case_results.append(
            {
                "index": i,
                "query": query,
                "topic": topic,
                "expected_area": expected_area,
                "acceptable_routes": acceptable_routes,
                "top_route": top_route,
                "confidence": confidence,
                "acceptable": acceptable,
                "alternative_used": alternative_used,
                "notes": case.get("notes", ""),
            }
        )

    total_cases = len(case_results)
    acceptable_top1 = sum(1 for r in case_results if r["acceptable"])
    acceptable_pct = round((acceptable_top1 / total_cases) * 100, 2) if total_cases else 0.0

    category_stats = []
    for area in sorted(area_counts):
        cases = area_counts[area]
        ok = area_acceptable.get(area, 0)
        pct = round((ok / cases) * 100, 2) if cases else 0.0
        category_stats.append(
            {
                "expected_area": area,
                "cases": cases,
                "acceptable_top1": ok,
                "acceptable_pct": pct,
            }
        )

    report = {
        "version": "1",
        "generated_at": now.isoformat(),
        "commit_sha": get_commit_sha(),
        "input_file": str(input_path.relative_to(ROOT)),
        "summary": {
            "total_cases": total_cases,
            "acceptable_top1": acceptable_top1,
            "acceptable_top1_pct": acceptable_pct,
            "low_confidence_cases": len(low_confidence),
            "out_of_scope_matches": out_of_scope_matches,
            "missing_route_ids": missing_route_ids,
        },
        "category_stats": category_stats,
        "cases": case_results,
        "failures": failures,
        "low_confidence": low_confidence,
    }

    shape_errors = validate_report_shape(report)
    if shape_errors:
        return fail("; ".join(shape_errors))

    json_output_path.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")

    tuning_actions = len(failures) + len(low_confidence)
    lines = []
    lines.append(f"# Agent Shadow Report - {date_tag}")
    lines.append("")
    lines.append("## Summary")
    lines.append("")
    lines.append("| Metric | Value |")
    lines.append("|---|---:|")
    lines.append(f"| Total cases | {total_cases} |")
    lines.append(f"| Top-1 acceptable | {acceptable_top1}/{total_cases} ({acceptable_pct}%) |")
    lines.append(
        f"| Low confidence (<{args.low_confidence_threshold}) | {len(low_confidence)} |"
    )
    lines.append(f"| Out-of-scope matches | {out_of_scope_matches} |")
    lines.append(f"| Missing route IDs | {missing_route_ids} |")
    lines.append("")
    lines.append("## Category Breakdown")
    lines.append("")
    lines.append("| Area | Cases | Acceptable Top-1 | % |")
    lines.append("|---|---:|---:|---:|")
    for row in category_stats:
        lines.append(
            f"| {row['expected_area']} | {row['cases']} | {row['acceptable_top1']} | {row['acceptable_pct']} |"
        )
    lines.append("")
    lines.append("## Detailed Results")
    lines.append("")
    lines.append("| # | Query | Expected Area | Top Route | Confidence | Acceptable | Alternative Used |")
    lines.append("|---:|---|---|---|---:|---|---|")
    for row in case_results:
        lines.append(
            "| {index} | {query} | {expected_area} | {top_route} | {confidence:.3f} | {acceptable} | {alternative_used} |".format(
                **row
            )
        )

    if failures:
        lines.append("")
        lines.append("## Failures")
        lines.append("")
        lines.append("| # | Query | Expected Routes | Actual Route | Confidence | Reason | Recommended Fix |")
        lines.append("|---:|---|---|---|---:|---|---|")
        for row in failures:
            lines.append(
                f"| {row['index']} | {row['query']} | {', '.join(row['expected_routes'])} | {row['actual_route']} | {row['confidence']:.3f} | {row['reason']} | {row['recommended_fix']} |"
            )

    if low_confidence:
        lines.append("")
        lines.append("## Low-Confidence Watchlist")
        lines.append("")
        lines.append("| # | Query | Route | Confidence |")
        lines.append("|---:|---|---|---:|")
        for row in low_confidence:
            lines.append(
                f"| {row['index']} | {row['query']} | {row['route']} | {row['confidence']:.3f} |"
            )

    lines.append("")
    lines.append("## Suggested Tuning Actions")
    lines.append("")
    if tuning_actions == 0:
        lines.append("- No tuning actions suggested for this run.")
    else:
        lines.append(f"- Address {len(failures)} unacceptable top-route match(es).")
        lines.append(
            f"- Review {len(low_confidence)} low-confidence case(s) for alias/index scoring adjustments."
        )

    output_path.write_text("\n".join(lines) + "\n", encoding="utf-8")

    print(f"Top-1 acceptable: {acceptable_top1}/{total_cases} ({acceptable_pct}%)")
    print(f"Low-confidence (<{args.low_confidence_threshold}): {len(low_confidence)}")
    print(f"Out-of-scope matches: {out_of_scope_matches}")
    print(f"Suggested tuning actions: {tuning_actions}")
    print(f"Reports: {output_path.relative_to(ROOT)}, {json_output_path.relative_to(ROOT)}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
