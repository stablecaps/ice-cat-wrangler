#!/bin/bash

set -euo pipefail

if ! command -v openssl &>/dev/null ; then
  echo "openssl is not installed. Please install it and try again."
  exit 1
fi


echo "enter password for secrets"
read -s password


for secret_path in "infra-terra/envs/dev/dev.backend.hcl" "infra-terra/envs/dev/dev.tfvars" "api-client-sig4/config/dev_conf_secrets" "serverless/functions/config/dev.yml"; do

  if [ ! -f "$secret_path" ]; then
    echo "$secret_path does not exist, exiting..."
    exit 42
  fi

  rm -f "${secret_path}.enc"
  openssl enc -aes-256-cbc -salt -in "${secret_path}" -out "${secret_path}.enc" -k "$password" -pbkdf2
  if [ $? -ne 0 ]; then
    echo "Encryption failed. Exiting.."
  exit 42
  fi

done

echo "Encryption completed successfully."
