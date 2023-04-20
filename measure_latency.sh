#!/bin/bash

# BMV2_PATH=../../behavioral-model
# P4C_BM_PATH=../../p4c
# PKTGEN_PATH=../pktgen/build/p4benchmark
# P4C_BM_SCRIPT=p4c-bm2-ss
# SWITCH_PATH=$BMV2_PATH/targets/simple_switch/simple_switch
# CLI_PATH=$BMV2_PATH/tools/runtime_CLI.py

TOFINO_PATH=home/tna-model/bf-sde-9-9-0
TOFINO_COMPILER_PATH=$SDE
TOFINO_SCRIPT=$HOME/tools/p4_build.sh
TOFINO_CLI_PATH=$SDE/run_tofino_model.sh
TOFINO_SWITCH_PATH=$SDE/run_switchhd.sh
PKTGEN_PATH=../pktgen/build/p4benchmark
VETH_SCRIPT=$SDE/install/bin/veth_setup.sh

PROG="main"

PACKETS=1000 
RATE=1000
# read -p "No. of Packets to send = " PACKETS
# read -p "Rate of sending packets(bytes/sec) = " RATE

ps -ef | grep simple_switch | grep -v grep | awk '{print $2}' | xargs kill
   
rm -rf output/

# for i in 1 2 3 4 5 6 7 8 9 10 11 12 13 14 15 16 17 18 19 20 21 22 23 24 25 26 27 28 29 30
# do

	p4benchmark --feature add-header --headers 1
	
	cd output
	set -m
	#compile the P4 program
	# $TOFINO_SCRIPT $PROG.p4

	if [ $? -ne 0 ]; then
	echo "Tofino compilation for $PROG.p4 failed"
	exit 1
	fi

	sudo echo "sudo" > /dev/null
	sudo $TOFINO_PATH >/dev/null 2>&1
	sudo $VETH_SCRIPT

	sleep 2
	echo "**************************************"
	echo "Sending commands to switch through CLI"
	echo "**************************************"
	$TOFINO_CLI_PATH -p $PROG < commands.txt 


	echo "READY!!!" 
	
	echo "Running the pktgen" 
	./$PKTGEN_PATH -p test.pcap -i veth4 -s veth0 -c $PACKETS -t $RATE 
	echo "Completed pktgen" 
	
    ps -ef | grep simple_switch | grep -v grep | awk '{print $2}' | xargs kill

	echo "Killed Switch Process" 
	
	cd ..

	./DataAlgo

done

./Percent pipeline-$VERSION-$PACKETS-$RATE-Percent.txt

cp output/data.txt pipeline-$VERSION-$PACKETS-$RATE.txt

