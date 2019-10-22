#!/bin/bash
# versions27 is a python 2.7.x environment
# versions36 is a python 3.6.x environment
#

function test_in_conda_env {

    CONDA_ENV=$1

    echo ""
    echo "################# ${CONDA_ENV} #################" 

    source activate ${CONDA_ENV}
    bash coverage.bash python-coverage
    source deactivate ${CONDA_ENV}

}


test_in_conda_env versions27
test_in_conda_env versions36


