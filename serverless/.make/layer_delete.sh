#!/bin/bash

LAYER_NAME=$1
MAX_LAYER_VERSION=$2
AWS_REGION=$3

if [ -z "$LAYER_NAME" ] || [ -z "$MAX_LAYER_VERSION" ]; then
  echo "Usage: $0 <layer-name> <max-layer-version>"
  exit 1
fi

if [ -z "$AWS_REGION" ]; then
  AWS_REGION="us-west-1"
fi

echo -e "\nDeleting lambda layers"

for i in $(seq 1 $MAX_LAYER_VERSION); do
  echo "Deleting layer version $i"
  aws --region $AWS_REGION lambda delete-layer-version --layer-name "$LAYER_NAME" --version-number "$i" || true
done
