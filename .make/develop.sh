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
# python -m pip install --editable .
python -m pip install -U -r requirements-dev.txt