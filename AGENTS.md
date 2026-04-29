# AGENTS.md

## Purpose

This repository orchestrates agent-driven deployment of k0rdent for multicluster management.

Current rollout scope:

- Included: `kcm`, `ksm`, `catalog`, `k0rdent-ui`
- Excluded: `kof`

## Repo Map

- `agents/`: agent contracts, schemas, and phase specs.
- `environments/`: per-environment config, values, and artifact locks.
- `scripts/`: executable phase steps (preflight, deploy, validate, smoke, report).
- `pipelines/`: workflow entrypoints (for example, `deploy-dev.sh`).
- `catalog/`: charts/images source references and docs.
- `docs/`: k0rdent product and operations documentation.
- `docs/agent-docs-index.json`: machine-readable routing index for agent intent lookup.
- `docs/schemas/agent-docs-index.schema.json`: schema contract for the routing index.
- `AGENT-DOCS-OPERATIONS.md`: operator runbook for docs routing, quality gates, and maintenance.
- `AGENT-DOCS-METHOD.md`: reusable reference for implementing this method in other projects.
- `TODO.md`: tracked backlog for upcoming agent and docs improvements.

## Execution Workflow

Canonical phase order:

1. planner
2. preflight
3. catalog
4. deploy
5. validation
6. report

Each run should write evidence to `state/<run-id>/`.

## Dev Workflow Contract

Use this contract for all `dev` installation runs and issue evidence.

### Stage sequence

1. planner
2. preflight (`./scripts/preflight.sh`)
3. catalog (`./scripts/catalog-lock.sh`)
4. deploy (`./scripts/deploy.sh`)
5. validation (`./scripts/validate.sh`)
6. smoke (`./scripts/smoke.sh`)
7. report (`./scripts/report.sh`)

### Required run evidence format

Record evidence under `state/<run-id>/` and summarize in the active issue comment with this minimum structure:

- `run_id`: UTC timestamp-style id (for example `20260429T101530Z`)
- `environment`: expected `dev`
- `config_path`: `environments/dev/config.env`
- `artifact_lock`: `environments/dev/artifact-lock.yaml`
- `cluster_context`: kube context used for the run
- `stage_status`: table with `stage | status(pass/fail/blocked) | evidence_path | notes`
- `blockers`: table with `id | severity(must-fix/can-defer) | owner | workaround | next_action | status`
- `env_snapshot`: key versions and tools (`kubectl`, `helm`, chart versions from config/lock)

### Stage go/no-go criteria

- planner -> preflight: proceed only when scope excludes `kof`, environment is `dev`, and run id/output path are defined.
- preflight -> catalog: proceed only when required CLIs exist, context resolves, and node access succeeds.
- catalog -> deploy: proceed only when lock file exists and required artifacts/versions are pinned for enabled components.
- deploy -> validation: proceed only when Helm install/upgrade commands succeed for all enabled components.
- validation -> smoke: proceed only when enabled component deployments report successful rollout status.
- smoke -> report: proceed only when smoke commands return expected component pod listings without command failure.
- report -> done: proceed only when `state/<run-id>/run-report.md` exists and issue evidence includes stage status + blocker tables.

If any stage fails, stop the forward sequence, mark the stage as `fail` or `blocked`, and log blocker details before rerun.

## Agent Contracts

- Shared input schema: `agents/schemas/input.schema.json`
- Shared output schema: `agents/schemas/output.schema.json`
- Per-agent behavior specs: `agents/specs/*.yaml`

Required handoff fields:

- Input: `run_id`, `environment`, `cluster_context`, `version_set`, `artifact_lock`, `policy_profile`
- Output: `status`, `evidence`, `next_action`, `rollback_hint`, `updated_artifacts`

## Agent Docs Contract

- Resolve documentation intents through `docs/agent-docs-index.json` first.
- If no strong match is found, fall back to `site/search/search_index.json`.
- Use `scripts/docs-agent-route.py` for deterministic resolution.
- Keep the current routing scope to core rollout docs and exclude `kof`.
- Validate routing quality with both:
  - `docs/golden-queries.json` (hard gate via `make docs-check`)
  - `docs/shadow-queries.json` (report-only via `make docs-shadow-report`)

## Doc Usage Guide

- Use `AGENTS.md` for repository policy and execution contract.
- Use `AGENT-DOCS-OPERATIONS.md` for day-to-day operator workflows and maintenance commands.
- Use `AGENT-DOCS-METHOD.md` for a shareable, project-agnostic implementation blueprint.

## Current Baseline

- Golden routing coverage: 67 cases, expected to remain green.
- Shadow routing quality: 30/30 acceptable top-1 in latest report.
- Metadata-required enforcement is active for template/CRD and quickstart/user-service priority docs.

## Deployment Rules

- Prefer OCI charts/images.
- Pin versions and digests in `environments/<env>/artifact-lock.yaml`.
- Use environment config from `environments/<env>/config.env`.
- Do not include `kof` in this deployment track.
- Treat `docs/` as vendored and workspace-owned in this repository; do not auto-sync from upstream docs sources without explicit review.

## Safety Guardrails

- Never commit secrets, credentials, or kubeconfigs.
- Do not run destructive cluster or git operations unless explicitly requested.
- Fail fast on preflight and policy violations.
- Promote environments only after validation evidence is complete.

## Quick Commands

```bash
# Full dev pipeline
./pipelines/deploy-dev.sh

# Step-by-step (dev)
./scripts/preflight.sh environments/dev/config.env
./scripts/catalog-lock.sh environments/dev/config.env
./scripts/deploy.sh environments/dev/config.env
./scripts/validate.sh environments/dev/config.env
./scripts/smoke.sh environments/dev/config.env
./scripts/report.sh environments/dev/config.env

# Documentation checks/build
make docs-check
make docs-build
```

## Definition of Done

- `kcm`, `ksm`, and `k0rdent-ui` are deployed and healthy in target environment.
- Artifacts are pinned and recorded.
- Validation and smoke checks pass.
- Run report and evidence are written under `state/<run-id>/`.
