.PHONY: develop
develop:
	./.make/develop.sh

.PHONY: pytest
pytest:
	pytest -vv

.PHONY: pytestcov - cov=tests
pytestcov:
	pytest --cov=shared_helpers tests/ --cov-report=xml
	pytest --cov=shared_helpers tests/ --cov-report=html
	pytest --cov=shared_helpers tests/
