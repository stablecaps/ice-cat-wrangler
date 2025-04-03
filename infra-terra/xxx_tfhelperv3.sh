#!/bin/bash

set -e

correct_usage_str="e.g: ./script.sh =[terraform_v1.11.3] inipath=[\$tf_init_path] autoapprove=[yes|no] env=[dev|prod] action=[init|plan|apply|full|destroy]"

echo -e "\nAvailable entrypoints:\n$(find entrypoints/ -mindepth 1 -maxdepth 1 -printf '%Ts %p\n' | sort -n | cut -d ' ' -f2-)\n"

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
if ! [[ -d "$inipath" ]]; then
    echo -e "<$inipath> relative path does not exist \nExiting.."
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
if ! [[ "$action" =~ ^(init|plan|apply|full|destroy)$ ]]; then
    echo -e "<$action> is not in the allowed actions options list \nExiting.."
    echo $correct_usage_str
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

cd $inipath
    echo -e "Running terraform from path $inipath"
    if [ "$action" == "init" ]; then
        echo -e "\nRunnning TF init\n"

        rm -rf .terraform .terraform.lock.hcl
        $terraform_exec init -backend-config ../../envs/${env}/${env}.backend.hcl

    elif [ "$action" == "apply" ]; then
        echo -e "\nRunnning TF apply with -auto-approve set to **${autoapprove}**\n"

        exec_str=$(tf_exec_with_autoapprove "$terraform_exec apply -var-file=../../envs/${env}/${env}.tfvars")
        $exec_str

    elif [ "$action" == "plan" ]; then
        echo -e "\nRunnning TF plan\n"

        exec_str=$(tf_exec_with_autoapprove "$terraform_exec plan -var-file=../../envs/${env}/${env}.tfvars")
        $exec_str

    elif [ "$action" == "full" ]; then
        echo -e "\nYOLO! Runnning TF full with -auto-approve set to **${autoapprove}**\n"

        rm -rf .terraform .terraform.lock.hcl
        $terraform_exec init -backend-config ../../envs/${env}/${env}.backend.hcl

        exec_str=$(tf_exec_with_autoapprove "$terraform_exec apply -var-file=../../envs/${env}/${env}.tfvars -auto-approve")
        $exec_str

    elif [ "$action" == "destroy" ]; then
        echo -e "\nDestroying TF with -auto-approve set to **${autoapprove}**\n"


        exec_str=$(tf_exec_with_autoapprove "$terraform_exec destroy -var-file=../../envs/${env}/${env}.tfvars")
        $exec_str
    fi

cd -
