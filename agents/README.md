# Agent Responsibilities

This folder defines agent contracts for deployment orchestration.

## Agent Set

- `planner`: builds the run graph and resolves environment/version targets.
- `preflight`: validates cluster/tooling prerequisites and blocks unsafe runs.
- `catalog`: resolves and locks OCI charts/images and digests.
- `deploy`: installs/upgrades `kcm`, `ksm`, `k0rdent-ui` in order.
- `validation`: runs post-deploy checks and smoke tests.
- `report`: writes run summary and evidence.

## Contract Rules

- All specs consume the shared input schema in `agents/schemas/input.schema.json`.
- All specs emit the shared output schema in `agents/schemas/output.schema.json`.
- Each agent should write phase evidence to `state/<run-id>/<phase>.json`.
- `kof` remains excluded from all phases for this deployment track.
