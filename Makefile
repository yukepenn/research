.PHONY: install test validate status tables reproduce novelty seed-citations clean

install:
	python -m pip install -e .[dev]

test:
	python -m pytest tests -q

validate:
	python -m core.audit.validate

status:
	python -m core.dashboard.status

tables:
	python -m core.plotting.build_all

seed-citations:
	python scripts/seed_citations.py

# Full reproducibility profile (small): validate -> tests -> rebuild tables -> status
reproduce: validate test tables status
	@echo "reproduce: small profile complete"

novelty:
	@cat program/fatal_overlap.md

clean:
	rm -rf generated/ .pytest_cache/ **/__pycache__/
