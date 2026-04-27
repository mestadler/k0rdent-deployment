#!/usr/bin/env python3

import argparse
import json
from difflib import SequenceMatcher
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
INDEX_PATH = ROOT / "docs/agent-docs-index.json"
SEARCH_INDEX_PATH = ROOT / "site/search/search_index.json"


def similarity(a: str, b: str) -> float:
    return SequenceMatcher(None, a.lower(), b.lower()).ratio()


def score_entry(entry: dict, intent: str, topic: str) -> float:
    score = 0.0
    if entry["intent"].lower() == intent.lower():
        score += 5.0
    score += similarity(intent, entry["intent"]) * 3.0
    score += similarity(intent, entry["topic"]) * 1.0
    aliases = entry.get("aliases", []) or []
    for alias in aliases:
        if alias.lower() == intent.lower():
            score += 4.5
        score += similarity(intent, alias) * 2.5
    if topic:
        if entry["topic"].lower() == topic.lower():
            score += 3.0
        score += similarity(topic, entry["topic"]) * 2.0
    return score


def route_from_index(intent: str, topic: str, limit: int) -> dict:
    data = json.loads(INDEX_PATH.read_text(encoding="utf-8"))
    entries = data.get("entries", [])
    scored = sorted(
        [{"score": score_entry(e, intent, topic), "entry": e} for e in entries],
        key=lambda x: x["score"],
        reverse=True,
    )

    if scored and scored[0]["score"] >= 2.2:
        best = scored[0]
        alternatives = [x["entry"] for x in scored[1:limit]]
        return {
            "source": "agent-docs-index",
            "confidence": round(best["score"], 3),
            "match": best["entry"],
            "alternatives": alternatives,
        }

    return {"source": "fallback", "reason": "no strong index match"}


def route_from_search(intent: str, topic: str, limit: int) -> dict:
    if not SEARCH_INDEX_PATH.exists():
        return {
            "source": "search-index",
            "error": "site/search/search_index.json not found; run make docs-build",
            "matches": [],
        }

    search_data = json.loads(SEARCH_INDEX_PATH.read_text(encoding="utf-8"))
    query = (intent + " " + topic).strip().lower()
    terms = [t for t in query.split() if t]
    docs = search_data.get("docs", [])
    scored = []

    for d in docs:
        hay = (d.get("location", "") + " " + d.get("text", "")).lower()
        term_hits = sum(hay.count(t) for t in terms)
        fuzzy = similarity(query, d.get("location", ""))
        score = term_hits + fuzzy
        if score > 0:
            scored.append(
                {
                    "score": round(score, 3),
                    "location": d.get("location"),
                }
            )

    scored.sort(key=lambda x: x["score"], reverse=True)
    return {
        "source": "search-index",
        "matches": scored[:limit],
    }


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Resolve best docs page for agent intent"
    )
    parser.add_argument("--intent", required=True, help="Intent to resolve")
    parser.add_argument("--topic", default="", help="Optional topic filter")
    parser.add_argument("--limit", type=int, default=5, help="Max fallback matches")
    args = parser.parse_args()

    if not INDEX_PATH.exists():
        print(json.dumps({"error": f"Missing {INDEX_PATH}"}, indent=2))
        return 1

    result = route_from_index(args.intent, args.topic, args.limit)
    if result.get("source") == "fallback":
        result = route_from_search(args.intent, args.topic, args.limit)

    print(json.dumps(result, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
