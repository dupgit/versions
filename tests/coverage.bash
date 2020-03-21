#!/bin/bash
#
# A basic coverage script
# Usage :
# coverage.bash COVERAGE-COMMAND
# Where COVERAGE-COMMAND is the command for
# coverage program

set -eu

export COV=$1

function header_print {

    echo
    echo "-------------------------------------------------"
    echo " Running test $@"
    echo "-------------------------------------------------"
    echo
}

function first_run_test {

    header_print $@
    ${COV} run ../versions/versions.py $@

}


function run_test {

    header_print $@
    ${COV} run -a ../versions/versions.py $@

}

first_run_test -d -f coverage.yaml
run_test -d -f doesnotexist.yaml
run_test -l -f coverage.yaml
run_test -f bad_formatted.yaml
run_test -f versions.yaml
run_test -l -f versions.yaml
