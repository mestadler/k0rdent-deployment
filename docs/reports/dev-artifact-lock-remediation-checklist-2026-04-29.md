# Dev Artifact Lock Remediation Checklist (M2 #7 dependency)

- Date (UTC): 2026-04-29
- Scope: replace all placeholder digests in `environments/dev/artifact-lock.yaml`
- Strict policy: baseline run is blocked until placeholder count is zero

## Trusted Registry Allowlist

- `ghcr.io`
- `registry.mirantis.com`
- `registry.local`

## Current Gate Status

- Placeholder markers present: 4
- Runner tooling (`kubectl`, `helm`): unavailable in current execution environment
- Registry host usage in lock refs: currently `ghcr.io` only (allowlisted)

## Digest Replacement Workflow

1. Select digest source per artifact from allowlist (`ghcr.io`, `registry.mirantis.com`, or `registry.local`).
2. Resolve immutable digest for each placeholder entry:
   - `k0rdent/ksm/charts/ksm:1.8.0` chart digest
   - `k0rdent/ksm/manager:v1.8.0` image digest
   - `k0rdent/k0rdent-ui/k0rdent-ui:1.2.0` chart digest
   - `k0rdent/k0rdent-ui/k0rdent-ui:v1.2.0` image digest
3. Update `environments/dev/artifact-lock.yaml` with resolved `sha256:<64-hex>` values.
4. Run strict lock gate validation (command below).
5. Attach evidence in issue `#7` (source registry, resolved digest, and gate pass output).

## Validation Command

```bash
./scripts/artifact-lock-gate.py environments/dev/artifact-lock.yaml \
  --allow-registry ghcr.io \
  --allow-registry registry.mirantis.com \
  --allow-registry registry.local
```

Pass criteria:

- `placeholder_matches=0`
- `invalid_digest_format=0`
- `disallowed_refs=0`
- `strict_gate=pass`

## Evidence Template for Issue #7

For each replaced entry:

- artifact: `<component/chart-or-image>`
- source registry: `<ghcr.io|registry.mirantis.com|registry.local>`
- ref: `<registry/repo:tag or oci://...>`
- resolved digest: `sha256:<64-hex>`
- command/tool used: `<tool + command summary>`

Then include strict gate output showing pass.
