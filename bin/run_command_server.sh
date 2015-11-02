#!/bin/bash

WORKDIR=${WORKDIR:=`pwd`}
PYTHONPATH=$WORKDIR/src
export PYTHONPATH

LOG_LEVEL=DEBUG

echo "Starting Web Server as `whoami`"
`python3 $WORKDIR/src/command_server/command_server.py --loglevel=$LOG_LEVEL $@`