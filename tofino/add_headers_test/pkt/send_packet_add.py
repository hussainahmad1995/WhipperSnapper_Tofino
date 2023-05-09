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

bind_layers(Ether , timestamp , type = 0x777)

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
    parser = argparse.ArgumentParser(prog = "send_packet_add.py", description='A')

    # parser.add_argument('-n', '--nb-packets', default=10, type=int,
    #                     help='Send [n] packets to the switch')

    parser.add_argument('-c', '--nbheaders' , default = 1 , type= int,
                        help = "Add [c] headers to each packet")

    parser.add_argument('-in' , '--interface' , default = "veth0" , type = str,
                            help = "Specify interface to send packets on")



    args = parser.parse_args()
    #create a packet with  packets 
    # the mac address for the interface enp4s0f0 is 00:a0:c9:00:00:00  
    # the mac address for the interface enp4s0f1 is 34:12:78:56:01:00

    pkt = Ether(dst="42:70:c7:3b:c5:2c",type = 0x777) / timestamp( time_value = 0, version = 0x778)

    # pkt/= header.add_fields(nb_fields = 1 )

    pkt /= headers(field_0 = 0)
    

    print("The length of the packet is " , len(pkt))
    
    # pkt = add_padding(pkt , packet_size = 256)
    pkt.show()
    iface = args.interface

    print("The length of the packet before sending the packet " , len(pkt))

    # use this when testing on the device
    # ifaces = { 1 : "enp0s20u1u2" , 2 : "enp4s0f0" , 3 : "enp4s0f1" }
    # iface = input("Select interface do you want to send ?  \n 1 -  enp0s20u1u2 (port 192) \n 2 - enp4s0f0 (port 66)  \n 3 - enp4s0f1 (port 64s) " )
    #Interface enp4s0f0 -----> port 64

    if iface == "enp4s0f0":
        print("Port number on which pkt is sent port = 64")
    if iface ==  "enp4s0f1":
        print("Port number on which pkt is sent port = 64")


    hexdump(pkt)

    print("Sending a packet to on interface  " , iface)

    #start timer for the packet send 
    # sent , receive = srp(pkt , iface = iface)



    start_time = time.time()
    print("Start Timestamping before sending " , start_time)
    reply = sendp(pkt , iface = iface)
    end_time = time.time()
    print("End time before sending " , end_time)
    latency = end_time - start_time  
    print("The latency for the packet from scapy is " , latency)





