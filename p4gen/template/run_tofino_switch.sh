#!/bin/bash

#Before running the script make sure the $SDE is set 
TOFINO_PATH=$SDE
TOFINO_SCRIPT=$SDE/tools/p4_build.sh
TOFINO_RUN_CLI_PATH=$SDE/tools/run_bfshell.sh
TOFINO_RUN_SWITCH=$SDE/run_switchhd.sh
PKTGEN_PATH=../pktgen/build/p4benchmark
VETH_SCRIPT=$SDE/tools/veth_setup.sh

PROG="main"

set -m
#compile the P4 program
# $TOFINO_SCRIPT $PROG.p4

if [ $? -ne 0 ]; then
echo "p4 compilation failed"
exit 1
fi

sudo echo "sudo" > /dev/null
#set up virtual ethernet ports
sudo .$VETH_SCRIPT 

#
sudo $TOFINO_SWITCH_RUN -p $PROG >/dev/null 2>&1

sleep 2
echo "**************************************"
echo "Sending commands to switch through CLI"
echo "**************************************"
./$TOFINO_CLI_PATH $PROG < commands.txt
echo "READY!!!"
fg
