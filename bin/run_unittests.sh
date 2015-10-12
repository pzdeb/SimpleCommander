#!/bin/bash

export PYTHONPATH

echo "Starting unittests"
`python3 $PYTHONPATH/src/unittests/simple_commander.py $@`