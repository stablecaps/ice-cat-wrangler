#!/bin/bash

set -e

if ! command -v pluralith &> /dev/null
    then
    echo "!!! Plaese ensure you have pluralith installed & on your path !!!"
    exit 42
fi

unique_tf_dirs=$(find ./ -not -path "*/\.*" -not -path "*venv/*" -not -path "*node_modules/*" -iname "*.tf" -exec dirname {} \; | grep init_points | grep -v deprecated_or_errored | grep -v 0_terraform_backend_setup_CAREFUL | grep -v local_modules| uniq)

for tf_dirs in $unique_tf_dirs; do
    echo -e "\nProcessing $tf_dirs"
    cd $tf_dirs
        mkdir -p images
        pluralith graph \
                    --author stablecaps.com \
                    --var-file ../../envs/prod/prod.tfvars \
                    --cost-mode total \
                    --cost-period month \
                    --local-only \
                    --file-name images/pluralith \
                    --title $tf_dirs

        convert \
            -verbose \
            -density 300 \
            -trim \
            images/pluralith.pdf \
            -quality 100 \
            -flatten \
            -sharpen 0x1.0 \
            images/terraform_infra.png

        rm -fv images/pluralith.pdf
    cd -
done

