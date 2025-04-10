#!/bin/bash

set -euo pipefail

# Create a virtual environment for the layer
rm -rf create_layer python
python3.12 -m venv create_layer
source create_layer/bin/activate

# Upgrade pip
pip install --upgrade pip

# Install dependencies into the layer directory
pip install -r ./requirements.txt --platform=manylinux2014_x86_64 --only-binary=:all: --target ./create_layer/lib/python3.12/site-packages

# Copy the shared_helpers module into the layer directory
cp -r shared_helpers ./create_layer/lib/python3.12/site-packages/
