# Scripts

This directory contains operational scripts for deployment execution and agent-focused docs routing checks.

## Deployment Flow Scripts

- `preflight.sh`: validates local tools and cluster access.
- `catalog-lock.sh`: verifies artifact lock presence and usage.
- `deploy.sh`: installs/upgrades core components in configured order.
- `validate.sh`: checks rollout status for enabled components.
- `smoke.sh`: runs basic pod-level smoke checks.
- `report.sh`: writes a run report under `state/<run-id>/`.
- `common.sh`: shared shell helper functions.

## Agent Docs Scripts

- `docs-agent-route.py`
  - Resolves best documentation route for an intent.
  - Primary source: `docs/agent-docs-index.json`
  - Fallback source: `site/search/search_index.json`
  - Example:
    - `python3 scripts/docs-agent-route.py --intent "cluster template format"`

- `docs-agent-check.py`
  - Validates docs routing/index contract:
    - index structure and required fields
    - key docs metadata frontmatter
    - core scope enforcement (excludes `kof`)

- `docs-agent-golden-check.py`
  - Runs golden query regression checks from `docs/golden-queries.json`.
  - Enforces strict/lenient route expectations.

## Common Commands

- Full docs guardrails: `make docs-check`
- Strict docs build: `make docs-build`
- Example route lookup: `python3 scripts/docs-agent-route.py --intent verify-installation-health`
