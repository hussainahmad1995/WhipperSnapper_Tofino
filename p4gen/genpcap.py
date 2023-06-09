import logging
logging.getLogger("scapy.runtime").setLevel(logging.ERROR)
from scapy.all import Packet, ShortField, XBitField, IntField
from scapy.all import Ether, IP, UDP, Padding
from scapy.all import wrpcap, bind_layers


# bind_layers(UDP, PTP, dport=319)

def add_eth_ip_udp_headers(dport):
    eth = Ether(src='0C:C4:7A:A3:25:34', dst='0C:C4:7A:A3:25:35')
    ip  = IP(dst='10.0.0.2', ttl=64)
    udp = UDP(sport=65231, dport=dport)
    pkt = eth / ip / udp
    return pkt

def add_layers(nb_fields, nb_headers):
    class P4Bench(Packet):
        name = "P4Bench Message"
        fields_desc =  []
        for i in range(nb_fields):
            fields_desc.append(ShortField('field_%d' %i , 0))
    layers = ''
    for i in range(nb_headers):
        if i < (nb_headers - 1):
            layers = layers / P4Bench(field_0=1)
        else:
            layers = layers / P4Bench(field_0=0)
    return layers

def vary_header_field(nb_fields):
    class P4Bench(Packet):
        name = "P4Bench Message"
        fields_desc =  []
        for i in range(nb_fields):
            fields_desc.append(ShortField('field_%d' % i , i))
    return P4Bench()

def add_padding(pkt, packet_size):
    pad_len = packet_size - len(pkt)
    if pad_len < 0:
        print "Packet size [%d] is greater than expected %d" % (len(pkt), packet_size)
    else:
        pad = '\x00' * pad_len
        pkt = pkt/pad
    return pkt

def get_parser_header_pcap(nb_fields, nb_headers, out_dir, packet_size=256):
    pkt = Ether(src='0C:C4:7A:A3:25:34', dst='0C:C4:7A:A3:25:35') / PTP()
    pkt /= add_layers(nb_fields, nb_headers)
    pkt = add_padding(pkt, packet_size)
    wrpcap('%s/test.pcap' % out_dir, pkt)

def get_parser_field_pcap(nb_fields, out_dir, packet_size=256):
    pkt = Ether(src='0C:C4:7A:A3:25:34', dst='0C:C4:7A:A3:25:35') / PTP()
    pkt /= vary_header_field(nb_fields)
    pkt = add_padding(pkt, packet_size)
    wrpcap('%s/test.pcap' % out_dir, pkt)

def get_read_state_pcap(udp_dest_port, out_dir, packet_size=256):

    class MemTest(Packet):
        name = "P4Bench Message for MemTest"
        fields_desc =  [
            XBitField("op", 0x1, 4),
            XBitField("index", 0x1, 12),
            XBitField("data", 0xf1f2f3f4, 32),
        ]

    pkt = add_eth_ip_udp_headers(udp_dest_port)
    pkt /= MemTest(op=1, index=0)

    pkt = add_padding(pkt, packet_size)
    wrpcap('%s/test.pcap' % out_dir, pkt)

def get_write_state_pcap(udp_dest_port, out_dir, packet_size=256):

    class MemTest(Packet):
        name = "P4Bench Message for MemTest"
        fields_desc =  [
            XBitField("op", 0x1, 4),
            XBitField("index", 0x1, 12),
            XBitField("data", 0xf1f2f3f4, 32),
        ]

    pkt = add_eth_ip_udp_headers(udp_dest_port)

    pkt /= MemTest(op=2, index=0, data=0)

    pkt = add_padding(pkt, packet_size)
    wrpcap('%s/test.pcap' % out_dir, pkt)

def get_pipeline_pcap(out_dir, packet_size=256):
    pkt = add_eth_ip_udp_headers(15432)
    pkt = add_padding(pkt, packet_size)
    wrpcap('%s/test.pcap' % out_dir, pkt)


def get_packetmod_pcap(nb_headers, nb_fields, mod_type, out_dir, packet_size=256):
    pkt = Packet()
    if mod_type == 'add':
        eth = Ether(src='0C:C4:7A:A3:25:34', dst='0C:C4:7A:A3:25:35')
        pkt = eth 
    elif mod_type == 'rm':
        eth = Ether(src='0C:C4:7A:A3:25:34', dst='0C:C4:7A:A3:25:35')
        pkt = eth 
        pkt /= add_layers(nb_fields, nb_headers)
        pkt = add_padding(pkt, packet_size)
    elif mod_type == 'mod':
        eth = Ether(src='0C:C4:7A:A3:25:34', dst='0C:C4:7A:A3:25:35')
        pkt = eth 
        pkt /= add_layers(nb_fields, nb_headers)
        pkt = add_padding(pkt, packet_size)

    wrpcap('%s/test.pcap' % out_dir, pkt)

def get_set_field_pcap(out_dir, packet_size=256):
    pkt = add_eth_ip_udp_headers(0x9091)
    pkt = add_padding(pkt, packet_size)
    wrpcap('%s/test.pcap' % out_dir, pkt)

def set_custom_field_pcap(nb_fields, out_dir, packet_size=256):
    pkt = Ether(src='0C:C4:7A:A3:25:34', dst='0C:C4:7A:A3:25:35') / PTP()
    pkt /= add_layers(nb_fields, 1)
    pkt = add_padding(pkt, packet_size)
    wrpcap('%s/test.pcap' % out_dir, pkt)
