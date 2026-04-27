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
- `DOCS-MAINTENANCE.md`: documentation maintenance and version-refresh checklist.
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

## Deployment Rules

- Prefer OCI charts/images.
- Pin versions and digests in `environments/<env>/artifact-lock.yaml`.
- Use environment config from `environments/<env>/config.env`.
- Do not include `kof` in this deployment track.

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
