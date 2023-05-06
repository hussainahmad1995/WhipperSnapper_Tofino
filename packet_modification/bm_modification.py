import os
from subprocess import call
from pkg_resources import resource_filename
from parsing.bm_parser import add_headers_and_parsers
from parsing.bm_parser import add_headers_and_parsers_16
from parsing.bm_parser import add_egress_parser
from p4gen.genpcap import get_packetmod_pcap
from p4gen import copy_scripts
from p4gen.p4template import *


def benchmark_add_header_overhead_16(action_name, nb_header):
    instruction_set =''
    for i in range(nb_header):
        instruction_set += '\t\thdr.header_%d.setValid();\n' % i
    instruction_set += '\t\thdr.timestamp.setValid();'
    return add_compound_action(action_name, '', instruction_set)

def benchmark_remove_header_overhead_16(action_name, nb_header):
    instruction_set =''
    for i in range(nb_header):
        instruction_set += '\t\thdr.header_%d.setInvalid();\n' % i
    instruction_set += '\t\thdr.ptp.version = 8w0;'
    return add_compound_action(action_name, '', instruction_set)

def benchmark_modify_header_overhead_16(action_name, nb_header):
    instruction_set =''
    for i in range(nb_header):
        instruction_set += '\t\thdr.header_{0}.field_0 = hdr.header_{0}.field_0 + 1;\n'.format(i)
    return add_compound_action(action_name, '', instruction_set)

def benchmark_modification_16(nb_headers, nb_fields, mod_type):
    """
    This method generate the P4 program to benchmark packet modification

    :param nb_headers: the number of generic headers included in the program
    :type nb_headers: int
    :param nb_fields: the number of fields (16 bits) in each header
    :type tbl_size: int
    :param nb_fields: modification type ['add', 'rm', 'mod']
    :type tbl_size: str
    :returns: bool -- True if there is no error

    """
    out_dir = 'output'
    if not os.path.exists(out_dir):
       os.makedirs(out_dir)

    fwd_tbl = 'forward_table'

    #Ingress() parser block
    program  = add_headers_and_parsers_16(nb_headers, nb_fields)
    actions = ''

    if mod_type == 'add':
        action_name = 'add_headers'
        actions += benchmark_add_header_overhead_16(action_name, nb_headers)
    elif mod_type == 'rm':
        action_name = 'remove_headers'
        actions += benchmark_remove_header_overhead_16(action_name, nb_headers)
    elif mod_type == 'mod':
        action_name = 'mod_headers'
        actions += benchmark_modify_header_overhead_16(action_name, nb_headers)

    tables = forward_table_16()

    table_name = 'test_tbl'
    tables += add_table_no_match(table_name, '\t\t\t{0};'.format(action_name))

    #Ingress() control block arguments and apply block statements
    Ingressapplies = '\t\tforward_table.apply();\n\t\t%s.apply();' %table_name
    Ingress_arguments = '''
        inout my_ingress_headers_t                          hdr,
        inout my_ingress_metadata_t                         meta,
        in    ingress_intrinsic_metadata_t               ig_intr_md,
        in    ingress_intrinsic_metadata_from_parser_t   ig_prsr_md,
        inout ingress_intrinsic_metadata_for_deparser_t  ig_dprsr_md,
        inout ingress_intrinsic_metadata_for_tm_t        ig_tm_md'''
        
    program += add_control_block_16('Ingress', actions, tables, Ingressapplies, Ingress_arguments)

    #IngressDeparser() control block arguments and apply statements

    Ingress_deparser_arguments = """
        packet_out packet,
        inout my_ingress_headers_t                       hdr,
        in    my_ingress_metadata_t                      meta,
        in    ingress_intrinsic_metadata_for_deparser_t  ig_dprsr_md"""

    Ingress_deparser_applies = "\tpacket.emit(hdr);"
    program += add_control_block_16("IngressDeparser" ,'','',Ingress_deparser_applies, Ingress_deparser_arguments)


    #EgressParser()

    Egress_parser_argument = """
    packet_in        packet,
    out my_egress_headers_t          hdr,
    out my_egress_metadata_t         meta,
    out egress_intrinsic_metadata_t  eg_intr_md
    """
    program += add_egress_parser(nb_headers)

    #Egress() control block arguments 
    egress_arguments = """    
    inout my_egress_headers_t                          hdr,
    inout my_egress_metadata_t                         meta,
    in    egress_intrinsic_metadata_t                  eg_intr_md,
    in    egress_intrinsic_metadata_from_parser_t      eg_prsr_md,
    inout egress_intrinsic_metadata_for_deparser_t     eg_dprsr_md,
    inout egress_intrinsic_metadata_for_output_port_t  eg_oport_md
    """
    program += add_control_block_16('Egress', '', '', '', egress_arguments)

    #EgressDeparser() block arguments and apply statements

    egress_deparser_arguments = """
    packet_out packet,
    inout my_egress_headers_t                       hdr,
    in    my_egress_metadata_t                      meta,
    in    egress_intrinsic_metadata_for_deparser_t  eg_dprsr_md
    """

    egress_deparser_applies = '\t\tpacket.emit(hdr);\n'
    program += add_control_block_16('EgressDeparser', '', '', egress_deparser_applies, egress_deparser_arguments)

    program += add_main_module()

    with open ('%s/main.p4' % out_dir, 'w') as out:
        out.write(program)

    commands = add_default_rule(table_name, action_name)
    commands += cli_commands(fwd_tbl)
    with open ('%s/commands.txt' % out_dir, 'w') as out:
        out.write(commands)
    copy_scripts(out_dir)
    get_packetmod_pcap(nb_headers, nb_fields, mod_type, out_dir)
    return program
