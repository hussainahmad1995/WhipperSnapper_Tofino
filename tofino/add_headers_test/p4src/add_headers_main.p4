//currently adding one header only to an incoming packet
// header_0 is added to each packet

#include <core.p4>
#include <tna.p4>

typedef bit<32> ipv4_addr_t;

header ethernet_t {
    bit<48> dstAddr;
    bit<48> srcAddr;
    bit<16> etherType;
}

header ipv4_t {
    bit<4>       version;
    bit<4>       ihl;
    bit<8>       diffserv;
    bit<16>      total_len;
    bit<16>      identification;
    bit<3>       flags;
    bit<13>      frag_offset;
    bit<8>       ttl;
    bit<8>       protocol;
    bit<16>      hdr_checksum;
    ipv4_addr_t  src_addr;
    ipv4_addr_t  dst_addr;

}

header timestamp_t {
    bit<48> time_value;
    bit<16> version;
}
header header_0_t {
	bit<16> field_0;
}
// header header_1_t {
// 	bit<16> field_0;
// }
// header header_2_t {
// 	bit<16> field_0;
// }
// header header_3_t {
// 	bit<16> field_0;
// }
// header header_4_t {
// 	bit<16> field_0;
// }
// header header_5_t {
// 	bit<16> field_0;
// }
// header header_6_t {
// 	bit<16> field_0;
// }
// header header_7_t {
// 	bit<16> field_0;
// }
// header header_8_t {
// 	bit<16> field_0;
// }
// header header_9_t {
// 	bit<16> field_0;
// }

struct metadata{
	
}
struct my_ingress_headers_t{
	ethernet_t ethernet;
    ipv4_t ipv4;
	timestamp_t timestamp;
	header_0_t header_0;
    // header_1_t header_1;
	// header_2_t header_2;
	// header_3_t header_3;
	// header_4_t header_4;
    // header_5_t header_5;
	// header_6_t header_6;
	// header_7_t header_7;
	// header_8_t header_8;
	// header_9_t header_9;
}
struct my_ingress_metadata_t{

}
parser IngressParser(
    packet_in        packet,
    out my_ingress_headers_t          hdr,
    out my_ingress_metadata_t         meta,
    out ingress_intrinsic_metadata_t  ig_intr_md
    ) {
    /* This is a mandatory state, required by Tofino Architecture */

    state start {
        packet.extract(ig_intr_md);
        packet.advance(PORT_METADATA_SIZE);
        transition parse_ethernet;
    }
    state parse_ethernet {
        packet.extract(hdr.ethernet);
        transition select(hdr.ethernet.etherType) {
		0x0800   : parse_ipv4;
		default : accept;
        }
    }

    state parse_ipv4 {
        packet.extract(hdr.ipv4);
        transition select(hdr.ipv4.protocol){
            100 : parse_timestamp;
            default : accept;
        }
    }
    state parse_timestamp {
        packet.extract(hdr.timestamp);
        transition accept;
    }
 //dont need to parse header_0 because we are adding it

}
control Ingress(
        inout my_ingress_headers_t                          hdr,
        inout my_ingress_metadata_t                         meta,
        in    ingress_intrinsic_metadata_t               ig_intr_md,
        in    ingress_intrinsic_metadata_from_parser_t   ig_prsr_md,
        inout ingress_intrinsic_metadata_for_deparser_t  ig_dprsr_md,
        inout ingress_intrinsic_metadata_for_tm_t        ig_tm_md) {
	
    action add_headers() {
		hdr.header_0.setValid();
        // hdr.header_1.setValid();
		// hdr.header_2.setValid();
		// hdr.header_3.setValid();
		// hdr.header_4.setValid();
		// hdr.header_5.setValid();
		// hdr.header_6.setValid();
		// hdr.header_7.setValid();
		// hdr.header_8.setValid();
		// hdr.header_9.setValid();
    }

    action forward(bit<9> port) {
        ig_tm_md.ucast_egress_port = port;
        hdr.timestamp.time_value[31:0] = ig_prsr_md.global_tstamp[31:0];   
    }
    action drop() {
        ig_dprsr_md.drop_ctl = 1;
    }    

    table ipv4_lpm {
        key     = { hdr.ipv4.dst_addr : lpm; }
        actions = { forward; drop; }

        default_action = forward(64); //CPU PORT
        size           = 1000;
    }

    table test_tbl {

        key = {
            hdr.ipv4.dst_addr: exact;
        }
        actions = {
			add_headers;
            drop;
        }
        size = 1000;
    }

    table ipv4_host {
        key = { hdr.ipv4.dst_addr : exact; }
        actions = {
            forward; 
            drop;
        }
        size = 1000;
    }

    apply
    {   if (hdr.ipv4.isValid()) {
            if (ipv4_host.apply().miss) {
                ipv4_lpm.apply();
            }
        }
		test_tbl.apply();
    }

}
control IngressDeparser(
        packet_out packet,
        inout my_ingress_headers_t                       hdr,
        in    my_ingress_metadata_t                      meta,
        in    ingress_intrinsic_metadata_for_deparser_t  ig_dprsr_md) {
	
    apply{
	    packet.emit(hdr);
    }
}
struct my_egress_metadata_t{
}

struct my_egress_headers_t{
    ethernet_t ethernet;
    ipv4_t ipv4;
	timestamp_t timestamp;
	header_0_t header_0;

}
parser EgressParser(
    packet_in        packet,
    out my_egress_headers_t          hdr,
    out my_egress_metadata_t         meta,
    out egress_intrinsic_metadata_t  eg_intr_md){ 
    
    state start {
        packet.extract(eg_intr_md);
        transition parse_ethernet;
        }

    state parse_ethernet {
        packet.extract(hdr.ethernet);
        transition select(hdr.ethernet.etherType) {
		0x0800   : parse_ipv4;
		default : accept;
        }
    }

    state parse_ipv4 {
        packet.extract(hdr.ipv4);
        transition select(hdr.ipv4.protocol){
            100 : parse_timestamp;
            default : accept;
        }
    }
    state parse_timestamp {
        packet.extract(hdr.timestamp);
        transition accept;
    }
    }
control Egress(    
    inout my_egress_headers_t                          hdr,
    inout my_egress_metadata_t                         meta,
    in    egress_intrinsic_metadata_t                  eg_intr_md,
    in    egress_intrinsic_metadata_from_parser_t      eg_prsr_md,
    inout egress_intrinsic_metadata_for_deparser_t     eg_dprsr_md,
    inout egress_intrinsic_metadata_for_output_port_t  eg_oport_md
    ) {
	
    apply{
        hdr.timestamp.time_value[31:0]= eg_prsr_md.global_tstamp[31:0] - hdr.timestamp.time_value[31:0];
    }

}
control EgressDeparser(
    packet_out packet,
    inout my_egress_headers_t                       hdr,
    in    my_egress_metadata_t                      meta,
    in    egress_intrinsic_metadata_for_deparser_t  eg_dprsr_md
    ) {
	
    apply{
		packet.emit(hdr);
    }

}

Pipeline(IngressParser(), Ingress(), IngressDeparser(), EgressParser(), Egress(), EgressDeparser() ) pipe; 
Switch(pipe) main;
