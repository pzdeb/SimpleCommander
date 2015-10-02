#!/bin/bash

WORKDIR=${WORKDIR:=`pwd`}
PYTHONPATH=$WORKDIR/
export PYTHONPATH

echo "Starting unittests"
`python3 $WORKDIR/src/unittests/simple_commander.py $@`