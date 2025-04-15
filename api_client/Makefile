.PHONY: develop
develop:
	./.make/develop.sh

.PHONY: pytest
pytest:
	pytest -vv

.PHONY: pytestcov - cov=tests
pytestcov:
	pytest --cov=api_client tests/ --cov-report=xml
	pytest --cov=api_client tests/ --cov-report=html
	pytest --cov=api_client tests/
