# Dev Environment Readiness Audit (M2 #6)

- Date (UTC): 2026-04-29
- Environment: `dev`
- Config: `environments/dev/config.env`
- Artifact lock: `environments/dev/artifact-lock.yaml`

## Audit Summary

- `config.env` is internally consistent for enabled components and chart/version keys.
- `artifact-lock.yaml` exists, but contains placeholder digests for `ksm` and `k0rdent-ui`.
- Script assumptions are only partially validated by current checks (`catalog-lock.sh` validates file presence, not lock quality).
- Local preflight execution failed immediately due missing `kubectl` binary in the runner environment.

## Verification Evidence

- `./scripts/preflight.sh environments/dev/config.env` -> fail: `Missing required command: kubectl`
- `./scripts/catalog-lock.sh environments/dev/config.env` -> pass: lock file present
- Placeholder digest scan (`REPLACE_WITH_REAL`) -> 4 matches in `environments/dev/artifact-lock.yaml`

## Blocker Table

| id | severity | owner | status | blocker | workaround | next_action |
|---|---|---|---|---|---|---|
| DEV-AUD-001 | must-fix | platform operator | open | `kubectl` missing in execution environment, so preflight cannot run. | Run from a host/container with `kubectl` + cluster access configured. | Install/provide `kubectl` in runner and rerun preflight. |
| DEV-AUD-002 | must-fix | release engineering | open | `artifact-lock.yaml` has placeholder digests for `ksm` and `k0rdent-ui`. | Temporarily rely on chart tags only (not acceptable for baseline hardening). | Replace placeholders with real chart/image digests and re-audit. |
| DEV-AUD-003 | must-fix | deployment automation | open | `ensure_namespace()` in `scripts/common.sh` does not pass `--context`, so namespace ops may target wrong cluster. | Use explicit kube-context in shell env before deploy. | Update helper to use configured context and add regression check. |
| DEV-AUD-004 | can-defer | deployment automation | open | Preflight registry check uses `helm registry login ... --help`, which does not verify authenticated access. | Validate OCI pull manually during deploy attempts. | Replace with real auth/state check and capture failure reason when unauthenticated. |
| DEV-AUD-005 | can-defer | security/compliance | open | `signatureVerified: false` in lock status indicates signatures are not yet part of gate. | Accept digest pinning for dev while documenting risk. | Define dev policy for signature verification (required vs informational). |

## Script Assumption Review

- `scripts/preflight.sh` assumes:
  - `kubectl` and `helm` are installed.
  - kube context from `KUBECONFIG_CONTEXT` exists and can access nodes.
- `scripts/catalog-lock.sh` assumes:
  - lock file exists at `LOCK_FILE` path.
  - it does not currently assert digest completeness or placeholder absence.
- `scripts/deploy.sh` assumes:
  - namespace creation helper acts on intended cluster context (currently not enforced in helper).

## Must-Fix vs Can-Defer Classification

- Must-fix before baseline execution issue #7:
  - DEV-AUD-001, DEV-AUD-002, DEV-AUD-003
- Can defer with documented risk for baseline execution:
  - DEV-AUD-004, DEV-AUD-005
