#!/bin/bash

set -euo pipefail

echo -e "usage:\nsupply_path e.g: ./secrets_encryptor.sh \$secrets_path"
echo -e "stdin e.g: ./secrets_encryptor.sh\n"

if ! command -v openssl &>/dev/null ; then
  echo "openssl is not installed. Please install it and try again."
  exit 1
fi

path=$1

if [ $# -lt 1 ]; then
  echo "enter password for secrets"
  read -s password
else
  password=$(cat $path)
fi

##############################

ALL_SECRETS=$(cat secrets.txt)

for secret_path in $ALL_SECRETS; do
  echo "Encrypting $secret_path"

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

echo -e "\nEncryption completed successfully."
