#!/bin/bash
set -euo pipefail

mkdir -p python
cp -r create_layer/lib python/
zip -r layer_content.zip python

rm -f ../serverless/layer/shared/layer_content.zip
cp layer_content.zip ../serverless/layer/shared/
