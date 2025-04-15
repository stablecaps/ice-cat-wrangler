.PHONY: test
test:
	poetry run pytest

.PHONY: develop
develop:
	./.make/develop.sh


.PHONY: slsplugins
slsplugins:
	serverless plugin install --name serverless-python-requirements
	serverless plugin install --name serverless-ssm-fetch
	serverless plugin install --name serverless-prune-versions


.PHONY: slslayer
slslayer:
	./.make/sls_buildlayer.sh

.PHONY: slsdeploy
.PHONY: slsdeploy
slsdeploy:
	./.make/slsdeploy.sh

.PHONY: slsdeployfull
.PHONY: slsdeployfull
slsdeployfull:
	./.make/sls_buildlayer.sh
	./.make/slsdeploy.sh

.PHONY: slsrm
slsrm:
	serverless remove

.PHONY: pytest
pytest:
	pytest -vv

.PHONY: pytestcov - cov=tests
pytestcov:
	pytest --cov=functions tests/ --cov-report=xml
	pytest --cov=functions tests/ --cov-report=html
