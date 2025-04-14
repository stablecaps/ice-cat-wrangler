#!/bin/bash

# set -e

if ! command -v pylint 2>&1 >/dev/null
then
    echo "pylint could not be found"
    exit 1
fi


pyfile=$1
echo "Running pylint on $pyfile"
if [ -z "$pyfile" ]; then
    echo "Usage: $0 <python_file>"
    exit 1
fi

cwd=$(pwd)
export PYTHONPATH=${cwd}:$PYTHONPATH

pylint $pyfile
