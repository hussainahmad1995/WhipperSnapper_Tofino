#!/usr/bin/python3

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

if iface == "enp4s0f0":
    port = "64"
if iface == "enp4s0f1":
    port = "66"

print("Sniffing on ", iface , " port " , port)
print("Press Ctrl-C to stop...")

# packet = sniff(iface = iface)
# packet = sniff(iface = iface)
# print("The received packet length is ", packet.length)

while(True):
    packet = sniff(count = 1 , iface=iface)[0]
    packet.show()
    print(" \n Packet received =  " + str(len(packet)) + " bytes\n")
    print("###[The latency incurred in the parser###] = " + str(packet[timestamp].time_value) +  " nanasecond \n")
    hexdump(packet)




