#!/bin/bash

set -e

echo "Setting up develop environment"

if ! command -v python3.12 2>&1 >/dev/null
then
    echo "python3.12 could not be found"
    exit 1
fi

if [ ! -d ./venv ]; then
  echo "Creating venv"
  python3.12 -m venv venv
fi

source venv/bin/activate

pip install --upgrade pip
pre-commit install

pip install -r requirements-dev.txt
pip show boto3

echo -e "\nPlease ensure your virtual environment is activated with:\n 'source venv/bin/activate'"
