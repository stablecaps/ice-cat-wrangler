ARTIFACTS_DIR ?= build

.PHONY: test
test:
	poetry run pytest

.PHONY: develop
develop:
	./.make/develop.sh

.PHONY: build
build:
	rm -rf dist || true
	poetry build -f wheel

.PHONY: build_layer
build_layer: build
	rm -rf "$(ARTIFACTS_DIR)/python" || true
	mkdir -p "$(ARTIFACTS_DIR)/python"
	poetry export -f requirements.txt --without-hashes | python -m pip install -r /dev/stdin -t "$(ARTIFACTS_DIR)/python"
	python -m pip install dist/*.whl -t "$(ARTIFACTS_DIR)/python"

.PHONY: package_layer
package_layer: build build_layer
	cd "$(ARTIFACTS_DIR)"; zip -rq ../layer.zip python

.PHONY: build-ServerlessProjectLayer
build-ServerlessProjectLayer: build build_layer

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
