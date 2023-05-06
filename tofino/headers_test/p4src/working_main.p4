#include <core.p4>
#include <tna.p4>
header ethernet_t {
    bit<48> dstAddr;
    bit<48> srcAddr;
    bit<16> etherType;
}
header timestamp_t {
    bit<48> time_value;
    bit<16> version;
}
header header_0_t {
	bit<16> field_0;

}
header header_1_t {
	bit<16> field_0;

}
header header_2_t {
	bit<16> field_0;

}
header header_3_t {
	bit<16> field_0;

}
header header_4_t {
	bit<16> field_0;

}
struct metadata{
	
}
struct my_ingress_headers_t{
	ethernet_t ethernet;
	timestamp_t timestamp;
	header_0_t header_0;
	header_1_t header_1;
	header_2_t header_2;
	header_3_t header_3;
	header_4_t header_4;
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
		0x777   : parse_timestamp;
		default : accept;

        }
    }
    state parse_timestamp {
        packet.extract(hdr.timestamp);
        transition select(hdr.timestamp.version) {
		0x778   : parse_header_0;
		default : accept;

        }
    }
    state parse_header_0 {
        packet.extract(hdr.header_0);
        transition select(hdr.header_0.field_0) {
		0x1000  : accept;
		default : parse_header_1;

        }
    }
    state parse_header_1 {
        packet.extract(hdr.header_1);
        transition select(hdr.header_1.field_0) {
		0x1001  : accept;
		default : parse_header_2;

        }
    }
    state parse_header_2 {
        packet.extract(hdr.header_2);
        transition select(hdr.header_2.field_0) {
		0x1002  : accept;
		default : parse_header_3;

        }
    }
    state parse_header_3 {
        packet.extract(hdr.header_3);
        transition select(hdr.header_3.field_0) {
		0x1003  : accept;
		default : parse_header_4;

        }
    }
    state parse_header_4 {
        packet.extract(hdr.header_4);
        transition select(hdr.header_4.field_0) {
		default : accept;
        }
    }
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
		hdr.header_1.setValid();
		hdr.header_2.setValid();
		hdr.header_3.setValid();
        hdr.header_4.setValid();
		hdr.timestamp.setValid();
    }

    action forward(bit<9> port) {
        ig_tm_md.ucast_egress_port = port;
        hdr.timestamp.time_value[31:0] = ig_prsr_md.global_tstamp[31:0];   
    }
    action _drop() {
        ig_dprsr_md.drop_ctl = 1;
    } 

    table forward_table {
        actions = {
            forward;
            _drop;
        }
        key = {
            hdr.ethernet.dstAddr: exact;
        }
        size = 4;
    }
    table test_tbl {
        actions = {
			add_headers;
        }
        size = 1;
    }


    apply{
		forward_table.apply();
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

struct my_egress_metadata_t
{}

struct my_egress_headers_t{
    ethernet_t ethernet;
	timestamp_t timestamp;
	header_0_t header_0;
	header_1_t header_1;
	header_2_t header_2;
	header_3_t header_3;
    header_4_t header_4;

}
parser EgressParser(
    packet_in        packet,
    out my_egress_headers_t          hdr,
    out my_egress_metadata_t         meta,
    out egress_intrinsic_metadata_t  eg_intr_md)
    {
    state start {
        packet.extract(eg_intr_md);
        transition parse_ethernet;
    }

    state parse_ethernet {
        packet.extract(hdr.ethernet);
        transition select(hdr.ethernet.etherType) {
		0x777   : parse_timestamp;
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
