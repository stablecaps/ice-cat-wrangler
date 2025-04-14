#!/bin/bash
set -euo pipefail

if ! command -v jq 2>&1 >/dev/null
then
    echo "jq could not be found"
    exit 1
fi


if [ ! -d "venv" ]; then
echo -e "making venv"
    python -m venv venv
fi

source venv/bin/activate

pip install -r requirements.txt -t modules

echo -e "\nDeploying shared helpers layer"

SERVICE_NAME=$(grep "service:" serverless.yml | tr ' ' '\n' | tail -1)
AWS_REGION=$(grep aws_region config/dev.yml | cut -d' ' -f2)
SHARED_HELPERS_ARN=$(aws --region $AWS_REGION lambda publish-layer-version --layer-name ${SERVICE_NAME}-dev-s3-shared-helpers \
    --description "Library that contains common dependencies for all lambdas" \
    --license-info "MIT" \
    --zip-file fileb://layer/shared/layer_content.zip \
    --compatible-runtimes python3.12 \
    --compatible-architectures "x86_64" | jq '.LayerVersionArn' | tr -d '"')

echo "SHARED_HELPERS_ARN: ${SHARED_HELPERS_ARN}"


echo -e "\ndeploying main service with shared services"
serverless deploy --stage dev --param="helpersarn=${SHARED_HELPERS_ARN}"
