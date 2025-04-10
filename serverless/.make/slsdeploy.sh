#!/bin/bash
set -euo pipefail

if ! command -v jq 2>&1 >/dev/null
then
    echo "jq could not be found"
    exit 1
fi

echo -e "\nBuilding lambda layer for shared helpers"
cd ../shared_helpers/
    ./1-install.sh
    ./2-package.sh
cd -


echo -e "\nDeploying shared helpers layer"

SERVICE_NAME=$(grep "service:" serverless.yml | tr ' ' '\n' | tail -1)
SHARED_HELPERS_ARN=$(aws lambda publish-layer-version --layer-name ${SERVICE_NAME}-dev-s3-shared-helpers6 \
    --description "Library that contains common dependencies for all lambdas" \
    --license-info "MIT" \
    --zip-file fileb://layer/shared/layer_content.zip \
    --compatible-runtimes python3.12 \
    --compatible-architectures "x86_64" | jq '.LayerVersionArn' | tr -d '"')

echo "SHARED_HELPERS_ARN: ${SHARED_HELPERS_ARN}"


echo -e "\ndeploying main service with shared services"
serverless deploy --stage dev --param="helpersarn=${SHARED_HELPERS_ARN}"
