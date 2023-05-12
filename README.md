TofinoBenchmark
=============

Tool to benchmark Tofino Compiler and Switch

Installation
------------

Run the following commands::

    pip install -r requirements.txt
    sudo python setup.py install

Generate P4 Program 
-------------------

* **Benchmark header addition**

The generated P4 program adds N=2 number of headers to packets::

    sudo p4benchmark --feature add-header --headers 2 

* **Benchmark header removal**

The generated P4 program removes N=2 number of headers to packets::

    sudo p4benchmark --feature rm-header --headers 2


Generated Files
---------------

The `output` directory contains::

    $ ls output
    main.p4 

    1. main.p4   The desired program to benchmark a particular feature of the P4 target


Run Tofino Switch
---------------------
Requires Tofino Switch or Model along with Tofino SDE(we are using bf-sde-9.9.0)

Set the SDE path first 
    $ $SDE_INSTALL/tools/set_sde.bash

Run Tofino Switch HD (in a seperate window) :

    $ ./run_switchd.sh -p main 

To work with the Wedge-100BF make sure to enable kernel modules:
    load the bfrt_kpt module - for the ASIC 

- there are two options
    - either use the  CPU <——> PCIE port
        - port 192
    - either use the  CPU <———> ETHERNET port
        - port 64 - 67

    NOTE - make sure the libpltfm_mgr.so is loaded - if working with Wedge 100-BF switch as the default is MODEL 

In our experiments we are using CPU ETH interface to send packet:
    10 Gbps Intel X552 MAC x2 


Make sure to add, set and enable Tofino ports using the provided cli (check Tofino 1 CPU-Ethernet port mapping):

    bf-sde.pm> port-add 33/- 10G NONE
    bf-sde.pm> an-set 33/- 2
    bf-sde.pm> port-enb 33/-

Add entries to the forward table : 

    $ $SDE_INSTALL/run_bfshell.sh -b ~/WhipperSnapper_Tofino/tofino/headers_test/bfrt_python/fill_table_forward.py

Ma


TO MEASURE LATENCIES
--------------------



## Packet processing
The above script is to automate the testing of a feature completely. The actual process going on is
1. The p4benchmark will produce the output directory to test certain feature.
2. The main.p4 program will be compiled with tofino compiler.
3. The main.p4 program will be loaded to the Tofino switch. 
4. BF_Shell uses the python script in the folder tofino/headers_test/bfrt_python/fill_table_forward.py to populate tables in the Switch.
5. Scapy python script is used to send packet on the interface exposed by the Tofino Switch(In our case we are using the port 64 to send packets).
6. As the table_forward forward packet on the port 66, we will be using Scapy to sniff the packet on the port 66.

## Latency measurements (using hardware timestamps)
 
PTP : PTP(Precision Time protocol) usage is only relevant for the synchornizing the clocks betweens switches, as we are calculating the latency withing the same device we dont the Protocol. 
Instead we use the Tofino timestamp metadata fields associated with each packet as it crosses each packet path namely the ingress parser, and egress parser.

1. We are using a custom bridge header called timestamp header with a bit<48> time_value with a default value of 0.
2. THe ingress_parser_timestamp which the Tofino timestamps when the ingress parser processing starts.
3. The egress_parser_timestamp value which the Tofino timestamps when the egress parser processing starts.
(Note - as we cannot carry metadata between ingress and egress parser, a bridge header gives us the functionality to carry ingress_parser_timestamp to the to process it in the egress processing)
4. Any queueing can affect the timestamp values, so to ensure the Traffic Manager is not queuing the packet we will not overload the system.
5. When the packet reaches the egress parser stage 


4. A simple_switch will be setup with the main.json file and with some veth interfaces as its ports.
5. RuntimeCLI will populate the match-action tables of simple_switch from commands.txt.
6. The run_test.py file will send n copies of test.pcap file to simple_switch port.
7. The simple_switch will process the packet recieved on the ingress port and send the output packet to the egress port.
8. The packet arrival epoch timestamps and their number will be printed to a file on both ingress and egress interfaces.
9. Average of difference of these timestamps is taken for all the packets, which represents the latency.
10. An algorithm is used to eliminate buggy values due to glitches in packet transfer, droppings. This is based on the fact that latency values are expected to be similar for each packet. The latency values are divided into various category. The category having the highest frequency will be the one to be selected and average of all values of only that category will be calculated. Note that if two categories are having major frequency count which is a rare case, we don't get much error by considering only one of them.


