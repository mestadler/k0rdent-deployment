# AGENT-DOCS-METHOD

This method turns operational documentation into a reliable system for agent execution by combining deterministic routing, regression-tested query suites, and a continuous learning loop. Instead of relying only on keyword or semantic search, it introduces explicit contracts (routing index, metadata requirements, query corpora), hard quality gates (golden checks), and report-driven improvement workflows (shadow checks and proposal triage). The result is higher reproducibility, safer updates, and measurable coverage growth over time. Teams can adopt it incrementally: start with routing and golden tests, add metadata enforcement for high-impact docs, then scale with learning-loop proposals and promotion rules. This balances precision, speed, and governance for agent-driven documentation workflows across projects.

## Purpose

- Define a reusable method for making documentation reliably usable by agents.
- Combine deterministic routing, quality gates, and a learning loop to improve coverage over time.
- Keep outcomes auditable, repeatable, and policy-controlled.

## When To Use This System

- Use when agents must execute operational workflows from docs, not just answer questions.
- Use when plain keyword search or pure semantic retrieval causes drift or inconsistent guidance.
- Use when regression protection is required after docs/routing updates.

## Problem Statement

- Typical docs are optimized for human browsing, not deterministic agent intent resolution.
- Search-only approaches can produce unstable route selection and weak reproducibility.
- Teams need a controlled path to improve retrieval quality without introducing regressions.

## Core Components

- **Routing index**: machine-readable map from intent to best entry docs.
- **Golden queries**: hard-gate deterministic checks for critical intents.
- **Shadow queries**: report-only real-world phrasing quality checks.
- **Metadata-required policy**: frontmatter contract on high-impact docs.
- **Learning loop**: failure logging, triage, proposal generation, and review.
- **Build/validation pipeline**: docs-check/build tasks and CI integration.

## Contracts and Artifacts

- `agent-docs-index.json`: canonical route map.
- `golden-queries.json`: strict/lenient deterministic routing tests.
- `shadow-queries.json`: non-blocking query corpus for real phrasing.
- `metadata-required.json`: required keys + enforced file list.
- Learning-loop artifacts:
  - `failure-log.jsonl`
  - `triage-queue.json`
  - `proposals.json`
  - `pr-checklist.md`
- Schemas for each artifact to keep data stable and toolable.

## Quality Model: Golden vs Shadow

- **Golden (hard gate)**:
  - deterministic, high-signal queries
  - must pass in CI
  - protects against regressions
- **Shadow (report-only)**:
  - noisy/real-world phrasing
  - identifies alias gaps and ambiguities
  - informs tuning and promotion candidates

## Metadata Strategy

- Require minimal frontmatter on priority docs:
  - `intent`, `audience`, `prereqs`, `inputs`, `outputs`, `related_docs`, `last_verified_version`
- Enforce `related_docs` path convention (repo-relative for tooling consistency).
- Expand metadata coverage in waves (P0/P1/P2) based on routing impact.

## Learning Loop

- **Collect**: capture misses/low-confidence outcomes.
- **Classify**: missing alias, ambiguous route, scoring issue, doc gap, scope violation.
- **Propose**: generate candidate fixes (manual cadence initially).
- **Review**: human approve/reject.
- **Apply**: implement approved proposals in small batches.
- **Validate**: rerun golden + shadow + build checks.
- **Promote**: move stable shadow phrases into golden.

## Proposal Ranking and Dedup

- Rank proposals with weighted score:
  - frequency, severity, impact, confidence gap, freshness.
- Deduplicate by proposal type + target + normalized query pattern.
- Cap generated proposals per run (for example, 15) to keep review manageable.

## Operational Cadence

- **Daily/per change**: run docs checks and strict build.
- **Periodic (manual initially)**:
  - run shadow report
  - run proposal generation
  - review checklist
- **After stability**:
  - consider scheduled proposal generation while retaining manual approval.

## Adoption Guide

### Day 0

- Establish routing index + schema.
- Add a basic route resolver.
- Add CI build gate.

### Day 1

- Add golden queries + checker.
- Add metadata-required policy for highest-impact docs.
- Enforce baseline docs guardrails.

### Day 2

- Add shadow report workflow.
- Add learning-loop artifacts and checks.
- Add proposal generation and PR checklist tooling.

## Metrics and KPIs

- Golden pass rate (strict + lenient).
- Shadow top-1 acceptable percentage.
- Low-confidence rate.
- Out-of-scope match count.
- Proposal throughput (generated/approved/applied).
- Mean time to resolve routing misses.

## Risk and Tradeoffs

- **Pros**: deterministic behavior, reproducibility, regression control.
- **Cons**: curation overhead, alias bloat risk, scoring complexity over time.
- **Mitigations**: schema enforcement, dedup rules, capped proposals, staged rollout.

## Governance and Scope Controls

- Define explicit scope inclusion/exclusion for routing.
- Fail fast on scope violations.
- Keep a human in the loop for proposal approval and promotions.

## Appendix: Minimal Starter Pack

- Starter files:
  - route index + schema
  - golden and shadow corpora + schemas
  - metadata-required config
  - learning-loop files + schemas
- Starter commands:
  - docs-check
  - docs-build
  - docs-shadow-report
  - docs-learning-check / docs-learning-propose / docs-learning-checklist

## External Sharing Checklist

- Replace project-specific names/paths with generic placeholders.
- Remove internal environment details, credentials references, and private repo URLs.
- Keep schemas/contracts and workflows; redact organization-specific policy where needed.
- Provide a starter template folder for quick adoption.
- Include one KPI dashboard example and one promotion policy example.
