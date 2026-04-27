# TODO

## Completed (2026-04-27)

- [x] Normalize docs product naming to `k0rdent` under `docs/` and rebuild site.
- [x] Remove accidental MkDocs starter source (`docs/docs/index.md`).
- [x] Configure `mkdocs.yml` with `use_directory_urls: false` for reliable `file://` navigation.
- [x] Fix API specification ReDoc URL loading (`.href` instead of `.pathname`).
- [x] Improve `docs/bare-metal-new.md` as a usable work-in-progress page with starter links.
- [x] Add docs maintenance guide in `AGENT-DOCS-OPERATIONS.md`.
- [x] Add docs guardrail target `make docs-check` in `Makefile`.
- [x] Add CI workflow `.github/workflows/docs-ci.yml` for docs checks/build on PRs and `main` pushes.
- [x] Link `TODO.md` from `README.md` and `AGENTS.md`.
- [x] Expand metadata coverage for template/CRD docs (P0) with enforced required keys.
- [x] Expand metadata coverage for quickstart/user/service docs (P1) with enforced required keys.
- [x] Add report-only shadow routing workflow and keep it green.
- [x] Expand golden routing suite from 55 to 67 cases and keep it green.
- [x] Add learning-loop scaffolding, validation, proposal generation, and PR checklist scripts.

## Active Milestone

- GitHub issue: [#1 Milestone 1: Agent docs routing and deploy runbook hardening](https://github.com/mestadler/k0rdent-deployment/issues/1)
- Current focus:
  - Expand routing/index quality for agent intent resolution.
  - Harden install/verify runbooks for reproducible operator execution.
  - Validate dev deployment command flow and document blockers.

### Current Quality Snapshot

- Golden routing: `67/67` pass (`make docs-check`).
- Shadow routing: `30/30` acceptable top-1, low-confidence `0` (`make docs-shadow-report`).
- Metadata enforcement: active via `docs/metadata-required.json` (P0 + P1 files).

### Next Up (pause handoff)

- [ ] PR3: metadata coverage reporting (`make docs-metadata-report`) and policy hardening.
- [ ] Add proposal ranking/dedup consistency checks to learning-loop validation.
- [ ] Promote stable shadow query families into stricter golden coverage where appropriate.
- [ ] Publish and iterate `AGENT-DOCS-METHOD.md` as an external shareable reference.

## Agent Docs Enablement

### 1) Add machine-readable docs index
- [x] Create `docs/agent-docs-index.json` schema:
  - `topic`
  - `intent`
  - `entry_doc`
  - `related_docs`
  - `commands`
  - `last_verified_version`
- [x] Seed index with high-value paths (install, preflight, deploy, validate, troubleshoot, API).
- [x] Add CI check to validate JSON schema and required fields.

### 2) Add agent metadata to key docs
- [x] Define frontmatter fields for agent consumption:
  - `intent`
  - `audience`
  - `prereqs`
  - `inputs`
  - `outputs`
  - `related_docs`
  - `last_verified_version`
- [x] Apply to initial docs set:
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
- [x] Add deterministic "best doc for intent" lookup rules.

### 5) CI and workflow integration
- [x] Extend `make docs-check` to include:
  - `agent-docs-index.json` validation
  - frontmatter required field checks
- [x] Update `.github/workflows/docs-ci.yml` to run new checks.

### 6) Documentation for maintainers
- [x] Update `AGENT-DOCS-OPERATIONS.md`:
  - how to refresh agent index
  - how to verify metadata completeness
  - version refresh process for agent references
- [x] Add "Agent docs contract" section to `AGENTS.md`.

## Nice to have
- [ ] Add `make docs-agent-check` target.
- [ ] Add changelog section for docs IA and metadata changes.
- [ ] Add small test corpus of agent queries and expected doc routes.
