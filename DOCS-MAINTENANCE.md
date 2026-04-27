# Docs Maintenance

This repository uses MkDocs to build static HTML from the `docs/` source directory.

## Source of Truth

- Edit files in `docs/`.
- Do not edit generated files in `site/`; they are overwritten on each build.
- Build config is in `mkdocs.yml` at repository root.
- The `docs/` tree is vendored and workspace-owned in this repository for deployment-focused agent workflows. Keep local intent unless a deliberate upstream sync/import is requested.

## Build and Preview

- Build with strict validation: `make docs-build`
- Serve locally over HTTP: `make docs-serve`
- Generated output path: `site/`

## Important Local Navigation Setting

`mkdocs.yml` is configured with `use_directory_urls: false`.

This keeps navigation working when opening docs directly via `file:///...` paths.
If this is changed back to `true`, local file navigation may appear broken.

## API Specification Page (ReDoc)

The API page is implemented in `docs/api-specification/index.md` and loads the OpenAPI spec via ReDoc.

- Keep the spec URL logic using `.href` (not `.pathname`) to support `file://` browsing.
- Spec files live in `docs/openapi/`.

## Agent Docs Routing

- Primary route source: `docs/agent-docs-index.json`
- Route schema: `docs/schemas/agent-docs-index.schema.json`
- Resolver helper: `scripts/docs-agent-route.py`
- Current rollout scope for agent routing excludes `kof`.

Usage example:

```bash
python3 scripts/docs-agent-route.py --intent install-k0rdent-on-management-cluster
```

Query examples:

```bash
# direct intent
python3 scripts/docs-agent-route.py --intent verify-installation-health

# natural-language alias (template format)
python3 scripts/docs-agent-route.py --intent "cluster template format"

# natural-language alias (service template format)
python3 scripts/docs-agent-route.py --intent "service template schema"

# natural-language alias (CRD lookup)
python3 scripts/docs-agent-route.py --intent "clusterdeployment crd"

# fuzzy intent with topic hint
python3 scripts/docs-agent-route.py --intent "network latency diagnostics" --topic troubleshooting --limit 3
```

## Golden Routing Queries

- Golden test corpus: `docs/golden-queries.json`
- Checker: `scripts/docs-agent-golden-check.py`
- Included in guardrails via `make docs-check`.

Query case fields:

- `query` (required)
- `expected_top` (required route id)
- `mode` (`strict` or `lenient`)
- `allowed_alternatives` (optional, max 2 recommended)
- `topic` (optional hint)

Guidance:

- Use `strict` for deterministic operational intents (install, verify, templates, CRDs, upgrade).
- Use `lenient` only for fuzzy phrasing where two close routes are acceptable.
- Keep current scope core-only and exclude `kof` from expected matches.

## Shadow Routing Report (Report-Only)

- Shadow corpus: `docs/shadow-queries.json`
- Shadow input schema: `docs/shadow-queries.schema.json`
- Report schema: `docs/reports/schemas/agent-shadow-report.schema.json`
- Runner: `scripts/docs-agent-shadow-report.py`

Run:

```bash
make docs-shadow-report
```

Outputs:

- Markdown: `docs/reports/agent-shadow-report-YYYY-MM-DD.md`
- JSON: `docs/reports/agent-shadow-report-YYYY-MM-DD.json`

Interpretation:

- This is report-only and does not fail CI.
- Use it to evaluate top-1 acceptable match quality for real-world phrasing.
- Prioritize tuning when unacceptable matches or low-confidence cases increase.

## Agent Learning Loop (v1)

Learning loop files:

- Failure log (JSONL): `docs/agent-learning/failure-log.jsonl`
- Triage queue: `docs/agent-learning/triage-queue.json`
- Proposals: `docs/agent-learning/proposals.json`
- Schemas:
  - `docs/agent-learning/schemas/failure-log-entry.schema.json`
  - `docs/agent-learning/schemas/triage-queue.schema.json`
  - `docs/agent-learning/schemas/proposals.schema.json`

Operational flow:

1. Ingest failures from shadow/runtime routing runs into `failure-log.jsonl`.
2. Group and classify failures in `triage-queue.json`.
3. Generate candidate tuning proposals in `proposals.json`.
4. Review and approve/reject proposals manually.
5. Apply approved updates, then validate with `make docs-check` and `make docs-shadow-report`.

Current policy:

- Proposal generation cadence is manual per run.
- Keep a max of 15 proposals per run.
- Generate PR checklist items only from approved proposals.

Validation commands:

- `make docs-learning-check` validates learning-loop schemas and starter data files.
- `make docs-check` also runs learning-loop validation as part of the hard docs guardrail suite.
- `make docs-learning-propose` generates up to 15 candidate proposals per run.
- `make docs-learning-checklist` generates PR checklist items from approved proposals.

## Agent Metadata in Docs

The following key docs must keep metadata frontmatter fields:

- `intent`
- `audience`
- `prereqs`
- `inputs`
- `outputs`
- `related_docs`
- `last_verified_version`

Current key docs:

- `docs/index.md`
- `docs/admin/installation/install-k0rdent.md`
- `docs/admin/installation/verify-install.md`
- `docs/quickstarts/quickstart-1-mgmt-node-and-cluster.md`
- `docs/troubleshooting/index.md`
- `docs/api-specification/index.md`

## Version Refresh Checklist

When introducing a new docs version:

1. Update versioned examples and references in `docs/`.
2. Update OpenAPI artifact(s) in `docs/openapi/` if changed.
3. Verify the API page still loads the intended spec file.
4. Run `make docs-check` and `make docs-build`.
5. Spot-check key entry pages:
   - `site/index.html`
   - `site/api-specification/index.html`
   - `site/bare-metal-new.html`
6. Update `last_verified_version` metadata in key docs as needed.
7. Refresh `docs/agent-docs-index.json` entries and commands for new version behavior.
8. Verify routing with `scripts/docs-agent-route.py` for key intents.

## Guardrails

- Avoid introducing unresolved template tokens unless a render step is added.
- Keep product naming consistent as `k0rdent`.
- Keep `docs/docs/index.md` absent unless intentionally adding a separate docs landing page.
