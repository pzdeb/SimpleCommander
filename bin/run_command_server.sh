#!/bin/bash

WORKDIR=${WORKDIR:=$(dirname `pwd`)}
PYTHONPATH=$WORKDIR/src
export PYTHONPATH

LOG_LEVEL=DEBUG

echo "Starting Web Server as `whoami`"
`python3 $WORKDIR/src/command_server.py --loglevel=$LOG_LEVEL $@`
