#!/usr/bin/env python3

import argparse
import json
import re
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
FAILURE_LOG = ROOT / "docs/agent-learning/failure-log.jsonl"
TRIAGE_QUEUE = ROOT / "docs/agent-learning/triage-queue.json"
PROPOSALS = ROOT / "docs/agent-learning/proposals.json"
INDEX_PATH = ROOT / "docs/agent-docs-index.json"

MAX_PROPOSALS_DEFAULT = 15
CONFIDENCE_THRESHOLD = 4.5


def normalize_text(text: str) -> str:
    lowered = text.strip().lower()
    lowered = re.sub(r"\s+", " ", lowered)
    lowered = re.sub(r"[^a-z0-9\-_/ ]", "", lowered)
    return lowered.strip()


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def load_failure_events(path: Path) -> list[dict]:
    events = []
    for line in path.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        events.append(json.loads(line))
    return events


def classify_failure(event: dict) -> str:
    if event.get("scope_violation"):
        return "scope_violation"

    expected = event.get("expected_routes", []) or []
    candidates = {c.get("route_id") for c in event.get("route_candidates", []) if c.get("route_id")}

    if expected:
        if any(route in candidates for route in expected):
            return "missing_alias"
        return "ambiguous_route"

    if float(event.get("confidence", 0.0)) < CONFIDENCE_THRESHOLD:
        return "scoring_issue"
    return "doc_gap"


def severity_value(classification: str) -> float:
    table = {
        "scope_violation": 1.0,
        "missing_alias": 0.8,
        "ambiguous_route": 0.7,
        "scoring_issue": 0.6,
        "doc_gap": 0.5,
    }
    return table.get(classification, 0.5)


def impact_value(events: list[dict]) -> float:
    score = 0.0
    for e in events:
        # v1: shadow failures are treated as medium priority by default.
        score += 0.6
    return score / max(len(events), 1)


def freshness_value(last_seen: str, now: datetime) -> float:
    try:
        ts = datetime.fromisoformat(last_seen.replace("Z", "+00:00"))
    except Exception:  # noqa: BLE001
        return 0.4
    delta = now - ts
    hours = delta.total_seconds() / 3600
    if hours < 24:
        return 1.0
    if hours < 24 * 7:
        return 0.7
    return 0.4


def confidence_gap(avg_conf: float) -> float:
    if avg_conf >= CONFIDENCE_THRESHOLD:
        return 0.0
    return max(0.0, (CONFIDENCE_THRESHOLD - avg_conf) / CONFIDENCE_THRESHOLD)


def rank_score(frequency: float, severity: float, impact: float, conf_gap: float, freshness: float) -> float:
    return (
        35 * frequency
        + 20 * severity
        + 20 * impact
        + 15 * conf_gap
        + 10 * freshness
    )


def build_clusters(events: list[dict]) -> list[dict]:
    grouped = defaultdict(list)
    for event in events:
        if event.get("acceptable") is True and not event.get("scope_violation", False):
            continue
        classification = classify_failure(event)
        query_pattern = normalize_text(event.get("query", ""))
        expected = tuple(event.get("expected_routes", []))
        key = (classification, query_pattern, expected)
        grouped[key].append(event)

    clusters = []
    for (classification, query_pattern, expected), items in grouped.items():
        linked_ids = [e.get("event_id", "") for e in items if e.get("event_id")]
        confidences = [float(e.get("confidence", 0.0)) for e in items]
        first_seen = min(e.get("timestamp", "") for e in items)
        last_seen = max(e.get("timestamp", "") for e in items)
        matched_routes = sorted({e.get("matched_route", "") for e in items if e.get("matched_route")})
        clusters.append(
            {
                "classification": classification,
                "query_pattern": query_pattern,
                "expected_routes": list(expected),
                "actual_routes": matched_routes,
                "linked_event_ids": linked_ids,
                "events": items,
                "evidence_count": len(items),
                "avg_confidence": sum(confidences) / max(len(confidences), 1),
                "first_seen": first_seen,
                "last_seen": last_seen,
            }
        )
    return clusters


def determine_target_route(cluster: dict, valid_routes: set[str]) -> str:
    for route in cluster.get("expected_routes", []):
        if route in valid_routes:
            return route
    if cluster.get("actual_routes"):
        if cluster["actual_routes"][0] in valid_routes:
            return cluster["actual_routes"][0]
    return "overview-home"


def proposal_type_for(classification: str) -> str:
    if classification in {"missing_alias", "ambiguous_route", "scoring_issue"}:
        return "add_alias"
    if classification == "scope_violation":
        return "adjust_route_scoring"
    return "doc_update"


def dedup_key(proposal_type: str, target: str, query_pattern: str) -> str:
    return f"{proposal_type}::{target}::{query_pattern}"


def upsert_triage_queue(queue: dict, cluster: dict, now_iso: str) -> str:
    items = queue.get("items", [])
    for item in items:
        if (
            item.get("query_pattern") == cluster["query_pattern"]
            and item.get("failure_class") == cluster["classification"]
        ):
            item["updated_at"] = now_iso
            linked = set(item.get("linked_event_ids", []))
            linked.update(cluster.get("linked_event_ids", []))
            item["linked_event_ids"] = sorted(linked)
            item["status"] = "proposed"
            return item["triage_id"]

    triage_id = f"triage-{now_iso[:10]}-{len(items)+1:04d}"
    items.append(
        {
            "triage_id": triage_id,
            "created_at": now_iso,
            "updated_at": now_iso,
            "status": "proposed",
            "query_pattern": cluster["query_pattern"],
            "failure_class": cluster["classification"],
            "linked_event_ids": sorted(set(cluster.get("linked_event_ids", []))),
            "expected_routes": cluster.get("expected_routes", []),
            "actual_routes": cluster.get("actual_routes", []),
            "priority": "high" if cluster["classification"] == "scope_violation" else "medium",
            "owner": "",
            "notes": "",
        }
    )
    queue["items"] = items
    return triage_id


def main() -> int:
    parser = argparse.ArgumentParser(description="Generate learning proposals from routing failures")
    parser.add_argument("--max-proposals", type=int, default=MAX_PROPOSALS_DEFAULT)
    args = parser.parse_args()

    if not FAILURE_LOG.exists() or not TRIAGE_QUEUE.exists() or not PROPOSALS.exists() or not INDEX_PATH.exists():
        print("ERROR: missing required learning loop files")
        return 1

    now = datetime.now(timezone.utc)
    now_iso = now.isoformat()

    events = load_failure_events(FAILURE_LOG)
    queue = load_json(TRIAGE_QUEUE)
    proposals_payload = load_json(PROPOSALS)
    index = load_json(INDEX_PATH)
    valid_routes = {e.get("id") for e in index.get("entries", [])}

    existing = proposals_payload.get("proposals", [])
    existing_keys = {p.get("dedup_key"): p for p in existing}

    clusters = build_clusters(events)
    if not clusters:
        print("No failure clusters found; no proposals generated")
        return 0

    max_count = max(c["evidence_count"] for c in clusters)
    scored = []

    for cluster in clusters:
        target_route = determine_target_route(cluster, valid_routes)
        ptype = proposal_type_for(cluster["classification"])
        dkey = dedup_key(ptype, target_route, cluster["query_pattern"])

        if dkey in existing_keys and existing_keys[dkey].get("status") in {
            "pending_review",
            "approved",
            "applied",
        }:
            continue

        freq = cluster["evidence_count"] / max_count
        sev = severity_value(cluster["classification"])
        imp = impact_value(cluster["events"])
        cgap = confidence_gap(cluster["avg_confidence"])
        fresh = freshness_value(cluster["last_seen"], now)
        score = rank_score(freq, sev, imp, cgap, fresh)

        scored.append(
            {
                "cluster": cluster,
                "target_route": target_route,
                "proposal_type": ptype,
                "dedup_key": dkey,
                "score": round(score, 3),
                "score_breakdown": {
                    "frequency": round(freq, 3),
                    "severity": round(sev, 3),
                    "impact": round(imp, 3),
                    "confidence_gap": round(cgap, 3),
                    "freshness": round(fresh, 3),
                    "weights": {
                        "frequency": 35,
                        "severity": 20,
                        "impact": 20,
                        "confidence_gap": 15,
                        "freshness": 10,
                    },
                },
            }
        )

    scored.sort(key=lambda x: x["score"], reverse=True)
    selected = scored[: args.max_proposals]

    for i, item in enumerate(selected, start=1):
        cluster = item["cluster"]
        triage_id = upsert_triage_queue(queue, cluster, now_iso)
        proposal_id = f"prop-{now.strftime('%Y-%m-%d')}-{i:04d}"

        proposal = {
            "proposal_id": proposal_id,
            "created_at": now_iso,
            "updated_at": now_iso,
            "triage_id": triage_id,
            "status": "pending_review",
            "type": item["proposal_type"],
            "target": {"entity": "route", "id": item["target_route"]},
            "change": {
                "op": "append_alias",
                "value": cluster["query_pattern"],
            },
            "dedup_key": item["dedup_key"],
            "rationale": f"{cluster['classification']} observed for query pattern '{cluster['query_pattern']}'",
            "confidence": 0.8,
            "classification": cluster["classification"],
            "evidence": {
                "evidence_count": cluster["evidence_count"],
                "linked_event_ids": cluster["linked_event_ids"],
                "query_examples": [e.get("query", "") for e in cluster["events"][:3]],
                "first_seen": cluster["first_seen"],
                "last_seen": cluster["last_seen"],
                "avg_confidence": round(cluster["avg_confidence"], 3),
                "priority_mix": {"high": 0, "medium": cluster["evidence_count"], "low": 0},
            },
            "score": item["score"],
            "score_breakdown": item["score_breakdown"],
            "expected_impact": {
                "shadow_acceptance_delta_pct": 1.0,
                "golden_regression_risk": "low",
            },
            "review": {
                "reviewed_by": "",
                "review_notes": "",
                "approved_at": "",
                "rejected_at": "",
            },
            "applied": {
                "applied_in_commit": "",
                "applied_at": "",
                "apply_notes": "",
            },
        }
        proposals_payload["proposals"].append(proposal)

    TRIAGE_QUEUE.write_text(json.dumps(queue, indent=2) + "\n", encoding="utf-8")
    PROPOSALS.write_text(json.dumps(proposals_payload, indent=2) + "\n", encoding="utf-8")

    print(f"Generated {len(selected)} proposal(s) (max {args.max_proposals})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
