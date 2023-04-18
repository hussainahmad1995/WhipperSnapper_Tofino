import os
from subprocess import call
from pkg_resources import resource_filename
from parsing.bm_parser import add_headers_and_parsers
from parsing.bm_parser import add_headers_and_parsers_16
from p4gen.genpcap import get_packetmod_pcap
from p4gen import copy_scripts
from p4gen.p4template import *


def benchmark_add_header_overhead_16(action_name, nb_header):
    instruction_set =''
    for i in range(nb_header):
        instruction_set += '\t\thdr.header_%d.setValid();\n' % i
    instruction_set += '\t\thdr.ptp.reserved2 = 8w1;'
    return add_compound_action(action_name, '', instruction_set)

def benchmark_remove_header_overhead_16(action_name, nb_header):
    instruction_set =''
    for i in range(nb_header):
        instruction_set += '\t\thdr.header_%d.setInvalid();\n' % i
    instruction_set += '\t\thdr.ptp.reserved2 = 8w0;'
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

    #Adds parser
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

    applies = '\t\tforward_table.apply();\n\t\t%s.apply();' %table_name
    arguments = 'inout headers hdr, inout metadata meta, out ingress_intrinsic_metadata_t  ig_intr_md'

    program += add_control_block_16('Ingress', actions, tables, applies, arguments)
    program += add_control_block_16("IngressDeparser" ,'','',applies, arguments)
    program += add_control_block_16('egress', '', '', '', arguments)

    applies = '\t\tpacket.emit(hdr.ethernet);\n'
    applies += '\t\tpacket.emit(hdr.ptp);\n'

    for i in range(nb_headers):
        applies += '\t\tpacket.emit(hdr.header_%d);\n' % i

    program += add_control_block_16('DeparserImpl', '', '', applies, 'packet_out packet, in headers hdr')

    program += add_control_block_16('verifyChecksum', '', '', '', 'inout headers hdr, inout metadata meta')
    program += add_control_block_16('computeChecksum', '', '', '', 'inout headers hdr, inout metadata meta')

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
