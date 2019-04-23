#!/bin/bash
# 
# A basic coverage script
# Usage : 
# coverage.bash COVERAGE-COMMAND
# Where COVERAGE-COMMAND is the command for 
# coverage program

export COV=$1

${COV} run ../versions/versions.py -d -f coverage.yaml
${COV} run -a ../versions/versions.py -d -f doesnotexist.yaml
${COV} run -a ../versions/versions.py -l -f coverage.yaml
${COV} run -a ../versions/versions.py -f bad_formatted.yaml
${COV} run -a ../versions/versions.py -f versions.yaml
${COV} run -a ../versions/versions.py
${COV} run -a ../versions/versions.py -l
