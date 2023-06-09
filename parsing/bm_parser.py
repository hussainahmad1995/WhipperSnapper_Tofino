import os
from subprocess import call
from pkg_resources import resource_filename
from p4gen.genpcap import get_parser_header_pcap, get_parser_field_pcap
from p4gen.p4template import *
from p4gen import copy_scripts

class ParseNode():
    def __init__(self, parent=None, node_name='', code = '', code_header='', code_parser='', header_dec='', headers = ''):
        self.parent = parent
        self.node_name = node_name
        self.code = code 
        self.code_header = code_header
        self.code_parser = code_parser
        self.header_dec = header_dec
        self.headers = headers
        self.children = []

    def set_parent(self, parent):
        self.parent = parent

    def add_children(self, child):
        self.children.append(child)

    def get_node_name(self):
        return self.node_name

    def get_children(self):
        return self.children

    def get_code(self):
        return self.code

    def get_code_header(self):
        return self.code_header

    def get_code_parser(self):
        return self.code_parser

    def get_header_dec(self):
        return self.header_dec

    def get_headers(self):
        return self.headers

def preorder(node):
    program = ''
    if node:
        program += node.get_code()
        for n in node.get_children():
            program += preorder(n)
    return program


def preorder_header(node):
    program = ''
    if node:
        program += node.get_code_header()
        for n in node.get_children():
            program += preorder_header(n)
    return program

def preorder_headers(node):
    program = ''
    if node:
        program += node.get_headers()
        for n in node.get_children():
            program += preorder_headers(n)
    return program

def preorder_parser(node):
    program = ''
    if node:
        program += node.get_code_parser()
        for n in node.get_children():
            program += preorder_parser(n)
    return program

def preorder_header_dec(node):
    program = ''
    if node:
        program += node.get_header_dec()
        for n in node.get_children():
            program += preorder_header_dec(n)
    return program

def loop_rec(root, depth, fanout):
    for i in range(fanout):
        node_name = root.get_node_name() + '_%d' % i
        header_type_name = 'header{0}_t'.format(node_name)
        header_name = 'header{0}'.format(node_name)
        parser_state_name = 'parse_header{0}'.format(node_name)
        select_field = 'field_0'
        next_states = ''
        if depth == 0:
            next_states = select_case('default', 'ingress')
        else:
            for j in range(fanout):
                next_states += select_case(j+1, '{0}_{1}'.format(parser_state_name, j))
            next_states += select_case('default', 'ingress')

        field_dec = add_header_field('field_0', 16, 14)
        code = add_header(header_type_name, field_dec, 14)
        code += add_parser(header_type_name, header_name, parser_state_name,
            select_field, next_states)

        n = ParseNode(root, node_name, code, '', '', '', '')

        root.add_children(n)
        if depth > 0:
            loop_rec(n, depth-1, fanout)

def loop_rec_16(root, depth, fanout):
    for i in range(fanout):
        node_name = root.get_node_name() + '_%d' % i
        header_type_name = 'header{0}_t'.format(node_name)
        header_name = 'header{0}'.format(node_name)
        parser_state_name = 'parse_header{0}'.format(node_name)
        select_field = 'field_0'
        next_states = ''
        if depth == 0:
            next_states = select_case('default', 'accept')
        else:
            for j in range(fanout):
                next_states += select_case('16w%d' %(j+1), '{0}_{1}'.format(parser_state_name, j))
            next_states += select_case('default', 'accept')

        field_dec = add_header_field('field_0', 16, 16)
        code_header = add_header(header_type_name, field_dec, 16)
        code_parser = add_state(parser_state_name, header_name, select_field, next_states)
        header_dec = '\t{0: <8} {1};\n'.format(header_type_name, header_name)
        headers = '\t\tpacket.emit(hdr.%s);\n' % header_name

        n = ParseNode(root, node_name, code_header, code_header, code_parser, header_dec, headers)

        root.add_children(n)
        if depth > 0:
            loop_rec_16(n, depth-1, fanout)


def add_forwarding_table(output_dir, program):
    fwd_tbl = 'forward_table'
    program += forward_table()
    program += control(fwd_tbl, '')
    commands = cli_commands(fwd_tbl)
    with open ('%s/commands_for_tofino.txt' % output_dir, 'w') as out:
        out.write(commands)
    return program

def add_ingress_block_16():
    
    actions = ''
    tables = forward_table_16()
    applies = '\t\tforward_table.apply();\n'
    arguments = 'inout headers hdr, inout metadata meta, out ingress_intrinsic_metadata_t  ig_intr_md'

    return add_control_block_16('ingress', actions, tables, applies, arguments)


def write_output(output_dir, program):
    with open ('%s/main.p4' % output_dir, 'w') as out:
        out.write(program)
    copy_scripts(output_dir)

def parser_complexity_16(depth, fanout):
    """
    This method adds Ethernet, IPv4, TCP, UDP, and a number of generic headers
    which follow the UDP header. The UDP destination port 0x9091 is used to
    identify the generic header

    :param depth: the depth of the parsing graph
    :type depth: int
    :param fanout: the number branches for each node
    :type fanout: int
    :returns: str -- the header and parser definition

    """
    output_dir = 'output'
    if not os.path.exists(output_dir):
       os.makedirs(output_dir)

    fwd_tbl = 'forward_table'

    program = p4_define(16) + ethernet_header(16) + ptp_header(16)

    root = ParseNode()
    loop_rec_16(root, depth, fanout)

    program += preorder_header(root)

    program += add_metadata()

    header_dec = ''
    header_dec += add_struct_item('ethernet_t', 'ethernet')
    header_dec += add_struct_item('ptp_t', 'ptp')

    header_dec += preorder_header_dec(root)

    program += add_headers(header_dec)

    states_dec = ''
    states_dec += add_state_without_select('start','parse_ethernet')

    next_states = select_case('0x02', 'parse_ptp')
    next_states += select_case('default', 'accept')
    states_dec += add_state('parse_ethernet', 'ethernet', 'etherType', next_states)

    next_states = select_case('8w1', 'parse_header_0')
    next_states += select_case('default', 'accept')
    states_dec += add_state('parse_ptp', 'ptp', 'version', next_states)

    states_dec += preorder_parser(root)

    program += parser_16(states_dec, 'IngressParser')

    program += add_ingress_block_16()

    arguments = 'inout headers hdr, inout metadata meta, out ingress_intrinsic_metadata_t  ig_intr_md'
    program += add_control_block_16('egress', '', '', '', arguments)

    applies = '\t\tpacket.emit(hdr.ethernet);\n'
    applies += '\t\tpacket.emit(hdr.ptp);\n'

    applies += preorder_headers(root)

    program += add_control_block_16('DeparserImpl', '', '', applies, 'packet_out packet, in headers hdr')

    program += add_control_block_16('verifyChecksum', '', '', '', 'inout headers hdr, inout metadata meta')
    program += add_control_block_16('computeChecksum', '', '', '', 'inout headers hdr, inout metadata meta')

    program += add_main_module()


    commands = cli_commands(fwd_tbl)
    with open ('%s/commands.txt' % output_dir, 'w') as out:
        out.write(commands)
    write_output(output_dir, program)
    get_parser_header_pcap(depth+1, 1, output_dir)

    return True

def add_headers_and_parsers(nb_headers, nb_fields, do_checksum=False):
    """
    This method adds Ethernet, IPv4, TCP, UDP, and a number of generic headers
    which follow the UDP header. The UDP destination port 0x9091 is used to
    identify the generic header

    :param nb_headers: the number of generic headers included in the program
    :type nb_headers: int
    :param nb_fields: the number of fields (16 bits) in each header
    :type nb_fields: int
    :returns: str -- the header and parser definition

    """
    program = p4_define(14) + ethernet_header(14) + ptp_header(14) + parser_start()

    next_headers = select_case('ETHERTYPE_PTP', 'parse_ptp')
    next_headers += select_case('default', 'ingress')
    program += add_parser('ethernet_t', 'ethernet', 'parse_ethernet',
                            'etherType', next_headers)

    ptp_next_states = ''
    if (nb_headers > 0):
        ptp_next_states += select_case(0x1, 'parse_header_0')
    ptp_next_states += select_case('default', 'ingress')
    program += add_parser('ptp_t', 'ptp', 'parse_ptp',
                            'version', ptp_next_states)

    field_dec = ''
    for i in range(nb_fields):
        field_dec += add_header_field('field_%d' % i, 16, 14)

    for i in range(nb_headers):
        header_type_name = 'header_%d_t' % i
        header_name = 'header_%d' % i
        parser_state_name = 'parse_header_%d' % i
        if (i < (nb_headers - 1)):
            next_state  = select_case(0, 'ingress')
            next_state += select_case('default', 'parse_header_%d' % (i + 1))
        else:
            next_state = select_case('default', 'ingress')
        program += add_header(header_type_name, field_dec, 14)
        program += add_parser(header_type_name, header_name, parser_state_name,
                                'field_0', next_state)
    return program

def add_headers_and_parsers_16(nb_headers, nb_fields, do_checksum=False):
    """
    This method adds Ethernet, IPv4, TCP, UDP, and a number of generic headers
    which follow the UDP header. The UDP destination port 0x9091 is used to
    identify the generic header

    :param nb_headers: the number of generic headers included in the program
    :type nb_headers: int
    :param nb_fields: the number of fields (16 bits) in each header
    :type nb_fields: int
    :returns: str -- the header and parser definition

    """
    program = p4_define(16) + ethernet_header(16) + timestamp_header(16)

    field_dec = ''
    for i in range(nb_fields):
        field_dec += add_header_field('field_%d' % i, 16, 16)

    for i in range(nb_headers):
        header_type_name = 'header_%d_t' % i
        program += add_header(header_type_name, field_dec, 16)

    program += add_metadata()

    header_dec = ''
    header_dec += add_struct_item('ethernet_t', 'ethernet')
    header_dec += add_struct_item('timestamp_t', 'timestamp')

    for i in range(nb_headers):
        item_type_name = 'header_%d_t' % i
        item_name = 'header_%d' % i
        header_dec += add_struct_item(item_type_name, item_name)

    program += add_ingress_headers(header_dec)

    states_dec = ''
    states_dec += add_state_without_select('start','parse_ethernet')

    next_states = select_case('0x777', 'parse_timestamp')
    next_states += select_case('default', 'accept')
    states_dec += add_state('parse_ethernet', 'ethernet', 'etherType', next_states)

    next_states = select_case('0x778', 'parse_header_0')
    next_states += select_case('default', 'accept')
    states_dec += add_state('parse_timestamp', 'timestamp', 'version', next_states)

    for i in range(nb_headers):
        header_name = 'header_%d' % i
        state_name = 'parse_header_%d' % i
        if (i < (nb_headers - 1)):
            next_states  = select_case("0x100%d" % i , 'accept')
            next_states += select_case('default', 'parse_header_%d' % (i + 1))
        else:
            next_states = select_case('default', 'accept')
        states_dec += add_state(state_name, header_name,'field_0', next_states)

    program += Ingress_parser_16(states_dec, 'IngressParser')
    return program

def add_egress_parser(nb_headers):
    """This method adds the Egress Parser which is a mandatory state in the 
        Tofino Architecture, the parser state start and only extracts the header and emits
        the header onto the egress processing

    """
    program = ""
    header_dec = ''
    header_dec += add_struct_item('ethernet_t', 'ethernet')
    header_dec += add_struct_item('timestamp_t', 'timestamp')

    for i in range(nb_headers):
        item_type_name = 'header_%d_t' % i
        item_name = 'header_%d' % i
        header_dec += add_struct_item(item_type_name, item_name)

    program += add_egress_headers(header_dec)

    states_dec = ''
    states_dec += add_state_type_egress_parser("start" , "parse_ethernet" , "eg_intr_md")

    next_states = select_case('0x777', 'parse_timestamp')
    next_states += select_case('default', 'accept')
    states_dec += add_state('parse_ethernet', 'ethernet', 'etherType', next_states)

    states_dec += add_state_type_egress_parser("parse_timestamp" , "accept" , "hdr.timestamp")

    program += Egress_parser_16("EgressParser", states_dec )

    # states_dec += add_state_without_select("")
    return program


def benchmark_parser_header(nb_headers, nb_fields, do_checksum=False):
    """
    This method generate the P4 program to benchmark the P4 parser

    :param nb_headers: the number of generic headers included in the program
    :type nb_headers: int
    :param nb_fields: the number of fields (16 bits) in each header
    :type tbl_size: int
    :returns: bool -- True if there is no error

    """
    output_dir = 'output'
    if not os.path.exists(output_dir):
       os.makedirs(output_dir)
    program  = add_headers_and_parsers(nb_headers, nb_fields, do_checksum)
    program = add_forwarding_table(output_dir, program)
    write_output(output_dir, program)
    get_parser_header_pcap(nb_fields, nb_headers, output_dir)
    generate_pisces_command(output_dir, nb_headers, nb_fields, do_checksum)

    return True

def benchmark_parser_header_16(nb_headers, nb_fields, do_checksum=False):
    """
    This method generate the P4 program to benchmark the P4 parser

    :param nb_headers: the number of generic headers included in the program
    :type nb_headers: int
    :param nb_fields: the number of fields (16 bits) in each header
    :type tbl_size: int
    :returns: bool -- True if there is no error

    """
    output_dir = 'output'
    if not os.path.exists(output_dir):
       os.makedirs(output_dir)
    program  = add_headers_and_parsers_16(nb_headers, nb_fields, do_checksum)
    program += add_ingress_block_16()

    arguments = 'inout headers hdr, inout metadata meta, out ingress_intrinsic_metadata_t  ig_intr_md'
    program += add_control_block_16('egress', '', '', '', arguments)

    applies = '\t\tpacket.emit(hdr.ethernet);\n'
    applies += '\t\tpacket.emit(hdr.ptp);\n'

    for i in range(nb_headers):
        applies += '\t\tpacket.emit(hdr.header_%d);\n' % i

    program += add_control_block_16('DeparserImpl', '', '', applies, 'packet_out packet, in headers hdr')

    program += add_control_block_16('verifyChecksum', '', '', '', 'inout headers hdr, inout metadata meta')
    program += add_control_block_16('computeChecksum', '', '', '', 'inout headers hdr, inout metadata meta')

    program += add_main_module()

    fwd_tbl = 'forward_table'
    commands = cli_commands(fwd_tbl)
    with open ('%s/commands.txt' % output_dir, 'w') as out:
        out.write(commands)
    write_output(output_dir, program)
    get_parser_header_pcap(nb_fields, nb_headers, output_dir)
    generate_pisces_command(output_dir, nb_headers, nb_fields, do_checksum)

    return True

def benchmark_parser_with_header_field(nb_fields, do_checksum=False):
    """
    This method generate the P4 program to benchmark the P4 parser

    :param nb_fields: the number of fields (16 bits) in each header
    :type tbl_size: int
    :returns: bool -- True if there is no error

    """
    output_dir = 'output'
    if not os.path.exists(output_dir):
       os.makedirs(output_dir)
    program  = add_headers_and_parsers(1, nb_fields, do_checksum)
    program = add_forwarding_table(output_dir, program)
    write_output(output_dir, program)
    get_parser_field_pcap(nb_fields, output_dir)
    generate_pisces_command(output_dir, 1, nb_fields)

    return True

def benchmark_parser_with_header_field_16(nb_fields, do_checksum=False):
    """
    This method generate the P4 program to benchmark the P4 parser

    :param nb_headers: the number of generic headers included in the program
    :type nb_headers: int
    :param nb_fields: the number of fields (16 bits) in each header
    :type tbl_size: int
    :returns: bool -- True if there is no error

    """
    nb_headers = 1
    output_dir = 'output'
    if not os.path.exists(output_dir):
       os.makedirs(output_dir)
    program  = add_headers_and_parsers_16(nb_headers, nb_fields, do_checksum)
    program += add_ingress_block_16()

    arguments = 'inout headers hdr, inout metadata meta, out ingress_intrinsic_metadata_t  ig_intr_md'
    program += add_control_block_16('egress', '', '', '', arguments)

    applies = '\t\tpacket.emit(hdr.ethernet);\n'
    applies += '\t\tpacket.emit(hdr.ptp);\n'

    for i in range(nb_headers):
        applies += '\t\tpacket.emit(hdr.header_%d);\n' % i

    program += add_control_block_16('DeparserImpl', '', '', applies, 'packet_out packet, in headers hdr')

    program += add_control_block_16('verifyChecksum', '', '', '', 'inout headers hdr, inout metadata meta')
    program += add_control_block_16('computeChecksum', '', '', '', 'inout headers hdr, inout metadata meta')

    program += add_main_module()

    fwd_tbl = 'forward_table'

    commands = cli_commands(fwd_tbl)
    with open ('%s/commands.txt' % output_dir, 'w') as out:
        out.write(commands)
    write_output(output_dir, program)
    get_parser_field_pcap(nb_fields, output_dir)
    generate_pisces_command(output_dir, 1, nb_fields)

    return True