# AGENT-DOCS-METHOD

This method makes operational documentation usable by agents in a predictable way. It combines deterministic routing, hard regression gates, and a continuous learning loop. Instead of relying only on keyword search or semantic ranking, it introduces explicit data contracts, enforced metadata, and repeatable quality checks. The goal is simple: agents should reliably pick the right doc, execute the right workflow, and improve over time without hidden regressions.

## Purpose

- Turn docs into an execution system, not just a knowledge base.
- Make routing behavior deterministic and testable.
- Improve coverage over time through controlled feedback loops.
- Keep changes auditable and safe for production workflows.

## When To Use This System

Use this method when:

- agents must execute operational runbooks,
- routing mistakes can cause real deployment risk,
- documentation changes happen frequently,
- and you need measurable quality, not best-effort retrieval.

Do not use this as a first step for tiny or static doc sets. Start lightweight and add this method once ambiguity and regressions become a problem.

## Problem Statement

Operational docs are usually written for humans. Agents need stricter structure.

Without explicit contracts, common failure modes are:

- correct docs exist but the agent picks the wrong page,
- similar intents collide (for example templates vs service docs),
- quality silently degrades after minor updates,
- retrieval scope drifts into excluded areas.

This method addresses those failure modes with explicit artifacts and gates.

## Core Components

- **Routing index**: a machine-readable map from intent/aliases to entry docs.
- **Golden query suite**: deterministic hard gate for critical intents.
- **Shadow query suite**: report-only real-world phrasing quality check.
- **Metadata-required policy**: frontmatter contract on high-impact docs.
- **Learning loop**: failure logging, triage, proposal generation, review, apply.
- **Build and CI gates**: strict checks to prevent regressions.

## Contracts and Artifacts

Keep each artifact small, explicit, and schema-backed.

- `docs/agent-docs-index.json`: canonical route map.
- `docs/schemas/agent-docs-index.schema.json`: route schema.
- `docs/golden-queries.json`: hard-gate test corpus.
- `docs/shadow-queries.json`: report-only corpus.
- `docs/metadata-required.json`: required metadata keys + enforced file list.
- Learning-loop data:
  - `docs/agent-learning/failure-log.jsonl`
  - `docs/agent-learning/triage-queue.json`
  - `docs/agent-learning/proposals.json`
  - `docs/agent-learning/pr-checklist.md`
- Learning-loop schemas:
  - `docs/agent-learning/schemas/*.json`

Principle: if behavior matters, represent it in a contract and validate it.

## Quality Model: Golden vs Shadow

### Golden (hard gate)

- Contains deterministic, high-signal intents.
- Runs in CI and must pass.
- Prevents regressions in critical workflows.

### Shadow (report-only)

- Contains natural/noisy operator phrasing.
- Measures practical usability and drift.
- Feeds the learning loop.

Promotion rule:

- promote a shadow query to golden only after repeated stable passes.

## Metadata Strategy

Metadata makes docs routable and composable.

Required fields:

- `intent`
- `audience`
- `prereqs`
- `inputs`
- `outputs`
- `related_docs`
- `last_verified_version`

Policy guidance:

- enforce metadata on a prioritized file set first,
- keep `related_docs` in repository-relative paths,
- expand coverage in waves (P0, P1, P2), not all at once.

## Learning Loop

The learning loop converts failures into approved improvements.

1. **Collect**
   - Log failed or low-confidence cases.
2. **Classify**
   - missing alias, ambiguous route, scoring issue, doc gap, scope violation.
3. **Propose**
   - Generate candidate fixes (manual cadence initially).
4. **Review**
   - Human approves or rejects proposals.
5. **Apply**
   - Implement approved changes in small batches.
6. **Validate**
   - Rerun golden + shadow + build checks.
7. **Promote**
   - Move stable shadow patterns into golden.

Never auto-apply proposals at the start. Require human review until the system has proven stability.

## Proposal Ranking and Dedup

Rank proposals by weighted signal, for example:

- frequency,
- severity,
- impact,
- confidence gap,
- freshness.

Dedup by normalized key:

- proposal type + target + normalized query pattern.

Operational rule:

- cap proposal output per run (for example 15) to keep review manageable.

## Operational Cadence

### Per change

- run docs checks,
- run strict docs build.

### Periodic (manual first)

- run shadow report,
- run proposal generation,
- generate PR checklist from approved proposals.

### After stabilization

- move proposal generation to scheduled runs,
- keep human approval and apply gates.

## Adoption Guide

### Day 0: Deterministic base

- add route index + schema,
- add route resolver,
- add strict docs build gate.

### Day 1: Regression safety

- add golden suite + checker,
- add metadata-required policy for high-impact docs,
- enforce docs guardrails in CI.

### Day 2: Continuous improvement

- add shadow reporting,
- add learning-loop artifacts and validation,
- add proposal generation and PR checklist tooling.

This staged rollout keeps implementation risk low while delivering value early.

## Metrics and KPIs

Track these metrics on every cycle:

- golden pass rate,
- shadow top-1 acceptable percentage,
- low-confidence rate,
- out-of-scope match count,
- proposal throughput (generated/approved/applied),
- mean time to resolve routing misses.

Use trends, not single runs, to make policy changes.

## Risk and Tradeoffs

Benefits:

- deterministic behavior,
- reproducibility,
- regression protection,
- measurable quality.

Costs:

- curation overhead,
- alias growth pressure,
- scoring complexity over time.

Mitigations:

- schema validation,
- dedup and proposal caps,
- staged metadata rollout,
- strict promotion rules.

## Governance and Scope Controls

- Define explicit in-scope and out-of-scope routing domains.
- Fail fast on scope violations.
- Keep human-in-the-loop for proposal approval and promotions.
- Require evidence (checks and reports) before broad policy changes.

## Appendix: Minimal Starter Pack

Minimum artifacts:

- route index + schema,
- golden/shadow corpora + schemas,
- metadata-required policy,
- learning-loop data + schemas.

Minimum commands:

- `make docs-check`
- `make docs-build`
- `make docs-shadow-report`
- `make docs-learning-check`
- `make docs-learning-propose`
- `make docs-learning-checklist`

## External Sharing Checklist

Before sharing this system outside your project:

- replace project-specific names, paths, and examples,
- remove environment-specific details and sensitive references,
- keep schemas/contracts and workflow mechanics intact,
- include a small starter template bundle,
- publish one KPI example and one promotion-policy example,
- document scope policy clearly (what is intentionally excluded).
