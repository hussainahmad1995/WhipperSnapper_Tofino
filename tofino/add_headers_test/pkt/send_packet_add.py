#!/usr/bin/env python
import time
import random
import argparse

import threading
from scapy.all import *

class timestamp(Packet):
    """Timestamp Protocol"""
    name = "Timestamp protocol"
    fields_desc = [
        XBitField(name = 'time_value', default = "0x02" , size = 48 , tot_size = 48 ),
        XBitField(name = 'version', default = "0x02" , size = 16 , tot_size = 16 )
    ]

bind_layers(Ether , IP)
bind_layers(IP , timestamp, proto = 100)

class headers(Packet):
    name = "Custom header"
    fields_desc = [XBitField(name = 'field_0', default = "0x" , size = 48 , tot_size = 48 )]

bind_layers(timestamp , headers , version = 0x778)

def add_layers(nb_fields, nb_headers):
    class header(Packet):
        name = "Custom header"
        fields_desc =  []
        for i in range(nb_fields):
            fields_desc.append(XBitField(name = 'field_%d' % i ,default = "0xDEFA", size = 16 , tot_size= 16))
    layers = ''
    for i in range(nb_headers):
        if i < (nb_headers - 1):
            layers = layers / header(field_0=1)
        else:
            layers = layers / header(field_0=0)    
    return layers

                
def add_padding(pkt, packet_size):
    pad_len = packet_size - len(pkt)
    if pad_len < 0:
        print ("Packet size [%d] is greater than expected %d" % (len(pkt), packet_size))
    else:
        pad = '\x00' * pad_len
        pkt = pkt/pad
    return pkt
      
if __name__ == "__main__":
    parser = argparse.ArgumentParser(prog = "send_packet_add.py", description='Number of packets to send')
    parser.add_argument('-n', '--nbpackets', default=1, type=int,
                        help='Send [n] packets to the switch')
    parser.add_argument('-c', '--nbheaders' , default = 0 , type= int,
                        help = "Add [c] headers to each packet")
    parser.add_argument('-in' , '--interface' , default = "veth0" , type = str,
                            help = "Specify interface to send packets on")
    parser.add_argument('-dip' , '--dstipaddr' , default = "10.0.0.3" , type = str , 
                            help = "Specify dst addr of packet")
    parser.add_argument('-deth' , '--dst_macaddr' , default = "3c:fd:fe:c3:e4:28" , type = str , 
                            help = "Specify dst addr of packet")
    args = parser.parse_args()
    iface = args.interface
    #MAC address of the src interface
    src_mac_addr = get_if_hwaddr(iface)
    #MAC address of the src interface
    dst_mac_addr = args.dst_macaddr
    #IP address of src interface
    src_ip_addr = get_if_addr(iface)
    #IP address of dst interface
    dst_ip_addr =  args.dstipaddr

    #create a packet
    pkt = Ether(src = src_mac_addr , dst = dst_mac_addr , type = 0x0800)  \
        / IP( src = src_ip_addr , dst = dst_ip_addr , proto = 100)        \
        / timestamp(time_value = 0, version = 0x778)

    #print its length in bytes
    print(" \n Packet sent =  " + str(len(pkt)) + " bytes")
    pkt.show()
    print("\nNo of Custom headers sent = "  + str(args.nbheaders) + "\n")
    hexdump(pkt)
    print("Sending a packet to on interface  " , iface)
    #start timer for the packet send 
    start_time = time.time()
    print("Send packet time = " , start_time)
    reply = sendp(pkt , iface = iface , count = args.nbpackets)
    end_time = time.time()
    print("Receive packet time =  " , end_time)
    latency = end_time - start_time  
    print("Latency packet(scapy) = " , latency)