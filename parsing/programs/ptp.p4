#define ETHERTYPE_IPV4 0x0800

#define TCP_PROTOCOL    0x06
#define UDP_PROTOCOL    0x11
#define PTP_SYNC        319
#define PTP_MESSAGE     320

header_type ethernet_t {
    fields {
        dstAddr : 48;
        srcAddr : 48;
        etherType : 16;
    }
}
header ethernet_t ethernet;

parser start {
    return parse_ethernet;
}

parser parse_ethernet {
    extract(ethernet);
    return select(latest.etherType) {
        ETHERTYPE_IPV4 : parse_ipv4; 
        default : ingress;
    }
}
header_type ipv4_t {
    fields {
        version : 4;
        ihl : 4;
        diffserv : 8;
        totalLen : 16;
        identification : 16;
        flags : 3;
        fragOffset : 13;
        ttl : 8;
        protocol : 8;
        hdrChecksum : 16;
        srcAddr : 32;
        dstAddr : 32;
    }
}
header ipv4_t ipv4;

parser parse_ipv4 {
    extract(ipv4);
    return select(latest.protocol) {
        UDP_PROTOCOL : parse_udp;
        default : ingress;
    }
}

header_type udp_t {
    fields {
        srcPort : 16;
        dstPort : 16;
        length_ : 16;
        checksum : 16;
    }
}
header udp_t udp;

parser parse_udp {
    extract(udp);
    return select(latest.dstPort) {
    	PTP_SYNC	: parse_ptp;
    	PTP_MESSAGE	: parse_ptp;
    	default     : ingress;
    }
}

header_type ptp_t {
    fields {
	ptptype		: 1;
	version		: 1;
	ptplength	: 2;
	domain		: 1;
	reserved	: 1;
	flags		: 2;
	correction	: 8;
	reserved2	: 4;
	srcPortId	: 10;
	seqId		: 2;
	ptpcontrol	: 1;
	logMsgInt	: 1;
	originTS	: 10;
    }
}

header ptp_t ptp;

parser parse_ptp {
    extract(ptp);
    return ingress;
}

action _drop() {
    drop();
}

action forward(port) {
    modify_field(ig_intr_md.egress_spec, port);
}

table forward_table {
    reads {
        ethernet.dstAddr : exact;
    } actions {
        forward;
        _drop;
    }
    size : 4;
}

control ingress {
    apply(forward_table);
}
