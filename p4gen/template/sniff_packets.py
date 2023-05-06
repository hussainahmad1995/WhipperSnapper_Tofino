#!/usr/bin/env python

from scapy.all import sniff

iface = "enp0s20u1u2"

def print_source_ethernet(frame):
    print(frame[Ether].src)


if __name__ == "__main__":
    packet = sniff(iface = iface , prn = lambda x : x.summary())

    print_source_ethernet()
