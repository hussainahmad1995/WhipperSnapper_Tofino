#!/usr/bin/python3

import os
import sys

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

port = 0 

if iface == "enp4s0f0":
    port = "64"
if iface == "enp4s0f1":
    port = "66"

print("Sniffing on ", iface , " port " , port)
print("Press Ctrl-C to stop...")
sniff(iface=iface, prn=lambda p: p.show())
sniff(iface=iface, prn=lambda p: p.summary())
