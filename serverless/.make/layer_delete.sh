#!/bin/bash

LAYER_NAME=$1
MAX_LAYER_VERSION=$2

if [ -z "$LAYER_NAME" ] || [ -z "$MAX_LAYER_VERSION" ]; then
  echo "Usage: $0 <layer-name> <max-layer-version>"
  exit 1
fi

echo -e "\nDeleting lambda layers"

for i in $(seq 1 $MAX_LAYER_VERSION); do
  echo "Deleting layer version $i"
  aws lambda delete-layer-version --layer-name "$LAYER_NAME" --version-number "$i" || true
done
