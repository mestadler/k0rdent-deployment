.PHONY: docs-build docs-serve docs-check docs-shadow-report

docs-build:
	mkdocs build --strict -f mkdocs.yml

docs-serve:
	mkdocs serve -f mkdocs.yml

docs-check:
	! test -f docs/docs/index.md
	! rg -n "sans\\.k0rdent1\\.8" docs --glob "*.md"
	! rg -n "\\{\\{\\{" docs --glob "*.md"
	! rg -n "\\.pathname" docs/api-specification/index.md
	python3 scripts/docs-agent-check.py
	python3 scripts/docs-agent-golden-check.py
	python3 scripts/docs-agent-route.py --intent install-k0rdent-on-management-cluster --limit 1 >/dev/null

docs-shadow-report:
	python3 scripts/docs-agent-shadow-report.py
