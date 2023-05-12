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

    args = parser.parse_args()

    pkt = Ether(src = "16:ee:82:a5:56:37" , dst = "0a:1d:4d:ba:d7:e4" ,type = 0x0800) / IP( dst = "10.0.0.23" , proto = 100) / timestamp(time_value = 0, version = 0x778)
    
    print(" \n Packet sent =  " + str(len(pkt)) + " bytes")
    
    pkt.show()
    iface = args.interface
    print("\nThe length of the packet before sending the packet : " + str(len(pkt)))
    print("\nNo of Custom headers sent = "  + str(args.nbheaders) + "\n")

    hexdump(pkt)

    print("Sending a packet to on interface  " , iface)
    #start timer for the packet send 
    start_time = time.time()
    print("Start Timestamping before sending " , start_time)
    reply = sendp(pkt , iface = iface , count = args.nbpackets)
    end_time = time.time()
    print("End time before sending " , end_time)
    latency = end_time - start_time  
    print("The latency for the packet from scapy is " , latency)





