#!/bin/bash
#Before running the script make sure the $SDE is set 
#path to compiling P4 program for Tofino Switch 

if [ -z "$SDE" ]; then
    echo "Error: SDE environment variable is not set."
    exit 1
fi

TOFINO_COMP_SCRIPT=$SDE/tools/p4_build.sh
TOFINO_RUN_CLI_PATH=$SDE/run_bfshell.sh
TOFINO_RUN_SWITCH=$SDE/run_switchd.sh
PKTGEN_PATH=../pktgen/build/p4benchmark
PROG="main"

set -m
#compile the P4 program
# $TOFINO_COMP_SCRIPT $PROG.p4

if [ $? -ne 0 ]; then
echo "p4 compilation failed"
exit 1
fi

sudo echo "sudo" > /dev/null
#set up virtual ethernet ports
sudo $SDE/tools/veth_setup.sh

echo "The problem is here and the $SDE"
#start tofino swithch driver
$TOFINO_RUN_SWITCH -p $PROG 


