.PHONY: develop
develop:
	./.make/develop.sh

.PHONY: pytest
pytest:
	pytest -vv

.PHONY: pytestcov - cov=tests
pytestcov:
	pytest --cov=api_client tests/ --junit-xml=pytest-cov.xml | tee pytest-coverage.txt
	pytest --cov=api_client tests/ --cov-report=html
	pytest --cov=api_client tests/
