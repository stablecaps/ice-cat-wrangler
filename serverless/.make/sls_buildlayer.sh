#!/bin/bash
set -euo pipefail

echo -e "\nBuilding lambda layer for shared helpers"
cd ../shared_helpers/
    ./1-install.sh
    ./2-package.sh
cd -
