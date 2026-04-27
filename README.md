# k0rdent deployment workspace

This workspace orchestrates deployment of k0rdent platform components for
multicluster management.

Scope for this track:

- Included: `kcm`, `ksm`, `catalog`, `k0rdent-ui`
- Excluded: `kof`

Operator contract and workflow rules live in `AGENTS.md`.
Planned follow-up work is tracked in `TODO.md`.

## Quick start

1. Edit `environments/dev/config.env` and `environments/dev/artifact-lock.yaml`.
2. Run pipeline:
   - `./pipelines/deploy-dev.sh`

## Docs build

- Build docs HTML (strict): `make docs-build`
- Serve docs locally: `make docs-serve`
- Run docs guardrail checks: `make docs-check`
- Generated HTML output: `site/`

## Layout

- `DEPLOYMENT-PLAN.md`: phase plan and definition of done.
- `AGENTS.md`: operator contract, workflow, guardrails, and quick commands.
- `agents/`: agent responsibilities and schema-based handoff contracts.
- `environments/dev/`: environment config, values, and artifact lock.
- `scripts/`: preflight, deploy, validate, smoke, and report steps.
- `pipelines/`: orchestration entrypoints.
- `docs/agent-docs-index.json`: machine-readable docs routing index for agents.
- `AGENT-DOCS-OPERATIONS.md`: operator runbook for docs routing, quality gates, and maintenance.
- `AGENT-DOCS-METHOD.md`: reusable method for agent-ready documentation systems.
- `TODO.md`: backlog of planned implementation and docs improvements.
