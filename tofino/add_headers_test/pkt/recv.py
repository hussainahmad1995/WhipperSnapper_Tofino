#!/usr/bin/python3

import csv
import os
import sys
from scapy.utils import hexdump
from send_packet_add import timestamp
# from send_packet_add import header
# from send_packet_add import add_layers.header


if os.getuid() !=0:
    print("""
ERROR: This script requires root privileges.
       Use 'sudo' to run it.
""")
    quit()

from scapy.all import *
try:
    iface=sys.argv[1]
except:
    iface="veth1"

port = ""

print("\nSniffing on " + str(iface) )
print("\nPress Ctrl-C to stop...")

latency_list = []
packet_count = 0 
    
packet = sniff(count = 1 , iface=iface, filter = "ip proto 100")[0]
packet.show()
print(" \n Packet received =  " + str(len(packet)) + " bytes\n")

while(packet_count < 1000):
    packet_count += 1
    packet = sniff(count = 1 , iface=iface, filter = "ip proto 100")[0]
    latency_list.append(packet[timestamp].time_value)


packet.show()
print("###[Last latency value = ###] = " + str(packet[timestamp].time_value) +  " nanosecond \n")
hexdump(packet)

latency_sum = 0
count = 0 
for latency in latency_list:
    count += 1 
    latency_sum += latency

average = latency_sum / count 

print("\n\n ###Average latency for 1000 packets ### = \n\n" , average)
