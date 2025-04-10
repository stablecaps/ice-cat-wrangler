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


.PHONY: build_layer
build_layer:
	./.make/sls_buildlayer.sh

.PHONY: slsdeploy
.PHONY: slsdeploy
slsdeploy:
	./.make/slsdeploy.sh

.PHONY: slsdeployfull
.PHONY: slsdeployfull
slsdeploy:
	./.make/sls_buildlayer.sh
	./.make/slsdeploy.sh



# https://dev.to/fwojciec/how-to-structure-a-python-aws-serverless-project-4ace

# ARTIFACTS_DIR ?= build

# .PHONY: test
# test:
# 	pytest


# .PHONY: develop
# develop:
# 	./.make/develop.sh

# .PHONY: build
# build:
# 	rm -rf dist || true
# 	python -m build -w

# .PHONY: build_layer
# build_layer: build
# 	rm -rf "$(ARTIFACTS_DIR)/python" || true
# 	mkdir -p "$(ARTIFACTS_DIR)/python"
# 	python -m pip install -r requirements.txt -t "$(ARTIFACTS_DIR)/python"
# 	python -m pip install dist/*.whl -t "$(ARTIFACTS_DIR)/python"

# .PHONY: package_layer
# package_layer: build build_layer
# 	cd "$(ARTIFACTS_DIR)"; zip -rq ../layer.zip python

# .PHONY: build-ServerlessProjectLayer
# build-ServerlessProjectLayer: build build_layer

# # https://dev.to/fwojciec/how-to-structure-a-python-aws-serverless-project-4ace
