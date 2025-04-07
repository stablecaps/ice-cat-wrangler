#!/bin/bash

set -euo pipefail

echo -e "usage:\nsupply_path e.g: ./secrets_decryptor.sh \$secrets_path"
echo -e "stdin e.g: ./secrets_decryptor.sh\n"

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
  echo "Decrypting $secret_path"

  if [ ! -f "$secret_path" ]; then
    echo "$secret_path does not exist, exiting..."
    exit 42
  fi


  openssl enc -aes-256-cbc -d -in "${secret_path}.enc" -out "${secret_path}" -k "$password" -pbkdf2
  if [ $? -ne 0 ]; then
    echo "Decryption failed. Exiting.."
  exit 42
  fi

done

echo -e "\nDecryption completed successfully."
