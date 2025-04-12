#!/bin/bash

set -eo pipefail

if [[ "$1" == "--help" || "$1" == "-h" ]]; then
  echo -e "Usage:\n"
  echo -e "1. Provide a file path containing the password: $0 /path/to/password_file"
  echo -e "2. Provide a text password directly: $0 '\$password'\n"
  exit 0
fi

if ! command -v openssl &>/dev/null ; then
  echo "openssl is not installed. Please install it and try again."
  exit 1
fi

if [ $# -lt 1 ]; then
  echo "Error: No argument provided."
  echo "Usage: $0 <password_file_path or text_password>"
  exit 1
fi


input=$1
if [ -f "$input" ]; then
  password=$(cat "$input")
else
  password="$input"
fi


##############################

ALL_SECRET_FILES=$(cat secrets.txt)

for secret_path in $ALL_SECRET_FILES; do
  echo "Encrypting $secret_path"

  if [ ! -f "$secret_path" ]; then
    echo "$secret_path does not exist, exiting..."
    exit 42
  fi

  rm -f "${secret_path}.enc"
  openssl enc -aes-256-cbc -salt -in "${secret_path}" -out "${secret_path}.enc" -k "$password" -pbkdf2
  if [ $? -ne 0 ]; then
    # TODO: this does not catch error
    echo "Encryption failed. Exiting.."
    exit 42
  fi

done

echo -e "\nEncryption completed successfully."
