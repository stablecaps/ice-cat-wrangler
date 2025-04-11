#!/bin/bash

set -e

echo -e "\nAvailable entrypoints:\n$(ls -1 entrypoints/ | sort -n )\n"


function print_help() {
    echo "Usage: $0 terraform_exec=[terraform_v1.11.3] inipath=[path] autoapprove=[yes|no] env=[dev|prod] action=[init|validate|plan|apply|full|destroy]"
    echo
    echo "Parameters:"
    echo "  terraform_exec   Path to the Terraform executable."
    echo "  inipath          Path from which Terraform is invoked."
    echo "  autoapprove      Whether to auto-approve actions (yes or no)."
    echo "  env              Environment (dev or prod)."
    echo "  action           Terraform action to perform (init, plan, apply, full, destroy)."
    echo
    exit 0
}

# Check for -h or --help
if [[ "$1" == "-h" || "$1" == "--help" ]]; then
    print_help
fi

###
if [ -z "$1" ]; then
    echo "Error: \$terraform_exec is unset"
    echo $correct_usage_str
    exit 42
fi

###
if [ -z "$2" ]; then
    echo "Error: \$inipath variable is unset [path_from_which_tf_is_invoked]"
    echo $correct_usage_str
    exit 42
fi

###
if [ -z "$3" ]; then
    echo "Error: \$autoapprove variable is unset [yes|no]). Set to no if this is not applicable"
    echo $correct_usage_str
    exit 42
fi

###
if [ -z "$4" ]; then
    echo "Error: \$env variable is unset"
    echo $correct_usage_str
    exit 42
fi

###
if [ -z "$5" ]; then
    echo "Error: \$action variable is unset"
    echo $correct_usage_str
    exit 42
fi

###
terraform_exec=$1
inipath=$2
autoapprove=$3
env=$4
action=$5


###
if ! command -v $terraform_exec &> /dev/null
then
    echo "\$terraform_exec <$terraform_exec> could not be found"
    echo $correct_usage_str
    exit 42
fi

###
if ! [[ -d "entrypoints/${inipath}" ]]; then
    echo -e "<entrypoints/${inipath}> relative path does not exist \nExiting.."
    echo $correct_usage_str
    exit 42
fi

###
if ! [[ "$autoapprove" =~ ^(yes|no)$ ]]; then
    echo -e "<$autoapprove> is not in the allowed autoapprove options list \nExiting.."
    echo $correct_usage_str
    exit 42
fi

###
if ! [[ "$action" =~ ^(init|validate|plan|apply|full|destroy)$ ]]; then
    echo -e "<$action> is not in the allowed actions options list \nExiting.."
    echo $correct_usage_strcd
    exit 42
fi

################################################
function tf_exec_with_autoapprove() {
    local tfcommand=$1
    if [ $action != "plan" ] && [ $autoapprove == "yes" ]; then
        tfcommand+=" -auto-approve"
    fi
    echo $tfcommand
}

################################################

cd entrypoints/${inipath}
    echo -e "Running terraform from path $inipath"
    if [ "$action" == "init" ]; then
        echo -e "\nRunnning TF init\n"

        rm -rf .terraform .terraform.lock.hcl
        $terraform_exec init -backend-config ../../envs/${env}/${env}.backend.hcl

    elif [ "$action" == "validate" ]; then
        echo -e "\nRunnning TF validate\n"

        $terraform_exec validate

    elif [ "$action" == "plan" ]; then
        echo -e "\nRunnning TF plan\n"

        exec_str=$(tf_exec_with_autoapprove "$terraform_exec plan -var-file=../../envs/${env}/${env}.tfvars")
        $exec_str

    elif [ "$action" == "apply" ]; then
        echo -e "\nRunnning TF apply with -auto-approve set to **${autoapprove}**\n"

        exec_str=$(tf_exec_with_autoapprove "$terraform_exec apply -var-file=../../envs/${env}/${env}.tfvars")
        $exec_str


    elif [ "$action" == "full" ]; then
        echo -e "\nYOLO! Runnning TF full with -auto-approve set to **${autoapprove}**\n"

        rm -rf .terraform .terraform.lock.hcl
        $terraform_exec init -backend-config ../../envs/${env}/${env}.backend.hcl

        $terraform_exec validate

        exec_str=$(tf_exec_with_autoapprove "$terraform_exec apply -var-file=../../envs/${env}/${env}.tfvars -auto-approve")
        $exec_str

    elif [ "$action" == "destroy" ]; then
        echo -e "\nDestroying TF with -auto-approve set to **${autoapprove}**\n"


        exec_str=$(tf_exec_with_autoapprove "$terraform_exec destroy -var-file=../../envs/${env}/${env}.tfvars")
        $exec_str
    fi

cd -
