# TODO

## Completed (2026-04-27)

- [x] Normalize docs product naming to `k0rdent` under `docs/` and rebuild site.
- [x] Remove accidental MkDocs starter source (`docs/docs/index.md`).
- [x] Configure `mkdocs.yml` with `use_directory_urls: false` for reliable `file://` navigation.
- [x] Fix API specification ReDoc URL loading (`.href` instead of `.pathname`).
- [x] Improve `docs/bare-metal-new.md` as a usable work-in-progress page with starter links.
- [x] Add docs maintenance guide in `DOCS-MAINTENANCE.md`.
- [x] Add docs guardrail target `make docs-check` in `Makefile`.
- [x] Add CI workflow `.github/workflows/docs-ci.yml` for docs checks/build on PRs and `main` pushes.
- [x] Link `TODO.md` from `README.md` and `AGENTS.md`.

## Active Milestone

- GitHub issue: [#1 Milestone 1: Agent docs routing and deploy runbook hardening](https://github.com/mestadler/k0rdent-deployment/issues/1)
- Current focus:
  - Expand routing/index quality for agent intent resolution.
  - Harden install/verify runbooks for reproducible operator execution.
  - Validate dev deployment command flow and document blockers.

## Agent Docs Enablement

### 1) Add machine-readable docs index
- [ ] Create `docs/agent-docs-index.json` schema:
  - `topic`
  - `intent`
  - `entry_doc`
  - `related_docs`
  - `commands`
  - `last_verified_version`
- [ ] Seed index with high-value paths (install, preflight, deploy, validate, troubleshoot, API).
- [ ] Add CI check to validate JSON schema and required fields.

### 2) Add agent metadata to key docs
- [ ] Define frontmatter fields for agent consumption:
  - `intent`
  - `audience`
  - `prereqs`
  - `inputs`
  - `outputs`
  - `related_docs`
  - `last_verified_version`
- [ ] Apply to initial docs set:
  - `docs/index.md`
  - `docs/admin/installation/install-k0rdent.md`
  - `docs/admin/installation/verify-install.md`
  - `docs/quickstarts/quickstart-1-mgmt-node-and-cluster.md`
  - `docs/troubleshooting/index.md`
  - `docs/api-specification/index.md`

### 3) Standardize task-oriented doc sections
- [ ] Add required section template for operational docs:
  - When to use
  - Inputs required
  - Commands
  - Expected output
  - Failure modes and fixes
- [ ] Add lint/check to enforce these sections in selected doc directories.

### 4) Improve retrieval for agents
- [ ] Add script to generate `docs/agent-docs-index.json` from:
  - curated mappings
  - `site/search/search_index.json` fallback
- [ ] Add deterministic "best doc for intent" lookup rules.

### 5) CI and workflow integration
- [ ] Extend `make docs-check` to include:
  - `agent-docs-index.json` validation
  - frontmatter required field checks
- [ ] Update `.github/workflows/docs-ci.yml` to run new checks.

### 6) Documentation for maintainers
- [ ] Update `DOCS-MAINTENANCE.md`:
  - how to refresh agent index
  - how to verify metadata completeness
  - version refresh process for agent references
- [ ] Add "Agent docs contract" section to `AGENTS.md`.

## Nice to have
- [ ] Add `make docs-agent-check` target.
- [ ] Add changelog section for docs IA and metadata changes.
- [ ] Add small test corpus of agent queries and expected doc routes.
