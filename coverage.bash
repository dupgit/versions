#!/bin/bash
# 
# A basic coverage script
# Usage : 
# coverage.bash COVERAGE-COMMAND
# Where COVERAGE-COMMAND is the command for 
# coverage program

export COV=$1

${COV} run ./versions.py -d -f coverage.yaml
${COV} run ./versions.py -d -f doesnotexist.yaml
${COV} run -a ./versions.py -l -f coverage.yaml
