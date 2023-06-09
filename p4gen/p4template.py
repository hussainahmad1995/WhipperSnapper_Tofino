from string import Template
from pkg_resources import resource_string

def read_template(filename, binding={}):
    """
    This method and substitutes the variables in the template with the binding
    and returns the result of the substitution

    :param filename: The path to the template
    :type filename: string
    :param binding: the mapping of variables to their values
    :type binding: dictionary
    :returns:  str -- the code in plain text
    :raises: None

    """
    src = Template(resource_string(__name__, filename))
    return src.substitute(binding)

def p4_define(version):
    """
    This method returns the constant definitions in P4

    :returns:  str -- the code in plain text
    :raises: None

    """
   
    p4_define = read_template('template/headers/define_16.txt')
    return p4_define

def ethernet_header(version):
    """
    This method returns the Ethernet header definition and its parser

    :returns:  str -- the code in plain text
    :raises: None

    """
    return read_template('template/headers/ethernet_16.txt')

def ethernet():
    """
    This method returns the Ethernet header definition and its parser

    :returns:  str -- the code in plain text
    :raises: None

    """
    ethernet_hdr = read_template('template/headers/ethernet.txt')
    parse_eth = read_template('template/parsers/parse_ethernet.txt')
    return (ethernet_hdr + parse_eth)

def ipv4(checksum=False):
    """
    This method returns the IPv4 header definition and its parser
    :param checksum: include checksum calculation
    :type checksum: bool
    :returns:  str -- the code in plain text
    :raises: None

    """
    ipv4_hdr = read_template('template/headers/ipv4.txt')
    if checksum:
        parse_ipv4 = read_template('template/parsers/parse_ipv4_checksum.txt')
    else:
        parse_ipv4 = read_template('template/parsers/parse_ipv4.txt')
    return (ipv4_hdr + parse_ipv4)

def ipv4_header(version):

    if version == 16:
        return read_template('template/headers/ipv4_16.txt')
    else: 
        return read_template('template/headers/ipv4.txt')

def tcp():
    """
    This method returns the TCP header definition and its parser

    :returns:  str -- the code in plain text
    :raises: None

    """
    tcp_hdr = read_template('template/headers/tcp.txt')
    parse_tcp = read_template('template/parsers/parse_tcp.txt')
    return (tcp_hdr + parse_tcp)

def tcp_header(version):

    if version == 14:
        return read_template('template/headers/tcp.txt')
    else: 
        return read_template('template/headers/tcp_16.txt')

def nop_action():
    """
    This method returns the _nop action definition

    :returns:  str -- the code in plain text
    :raises: None

    """
    return read_template('template/actions/nop.txt')

def forward_table():
    """
    This method returns the 'forwarding_table' definition

    :returns:  str -- the code in plain text
    :raises: None

    """
    d = { 'tbl_name': 'forward_table' }
    return read_template('template/tables/forward_table.txt', d)

def forward_table_16():
    """
    This method returns the 'forwarding_table' definition
    :returns:  str -- the code in plain text
    :raises: None
    """
    d = { 'table_name': 'forward_table' }
    return read_template('template/tables/forward_table_16.txt', d)

def test_table_16(tbl_name):
    """
    This method returns the 'forwarding_table' definition

    :returns:  str -- the code in plain text
    :raises: None

    """
    d = { 'table_name': tbl_name }
    return read_template('template/tables/test_table.txt', d)

def add_table_no_match(tbl_name, actions='_nop;', tbl_size=1):
    """
    This method returns the table definition that matches everything

    :param tbl_name: the name of the table
    :type tbl_name: str
    :param actions: the possible actions to be performed
    :type actions: str
    :param tbl_size: the size of the table
    :type tbl_size: int
    :returns:  str -- the code in plain text
    :raises: None

    """
    binding = {'tbl_name': tbl_name, 'actions': actions, 'tbl_size': tbl_size}

    return read_template('template/tables/table_no_match.txt', binding)

def add_table_no_match_14(tbl_name, actions='_nop;', tbl_size=1):
    """
    This method returns the table definition that matches everything

    :param tbl_name: the name of the table
    :type tbl_name: str
    :param actions: the possible actions to be performed
    :type actions: str
    :param tbl_size: the size of the table
    :type tbl_size: int
    :returns:  str -- the code in plain text
    :raises: None

    """
    binding = {'tbl_name': tbl_name, 'actions': actions, 'tbl_size': tbl_size}

    return read_template('template/tables/table_no_match_14.txt', binding)

def add_default_rule(tbl_name, default_action):
    """
    This method returns a rule that sets a default action for the table

    :param tbl_name: the name of the table
    :type tbl_name: str
    :param default_action: the default action if there is no match rule
    :type default_action: str
    :returns:  str -- the code in plain text
    :raises: None

    """
    binding = {'tbl_name': tbl_name, 'default_action': default_action}
    return read_template('template/commands/default_action.txt', binding)

def add_state(state_name, header_name, select_field, next_states):

    binding = { 'state_name' : state_name, 'header_name' : header_name, 
                'select_field' : select_field, 'next_states' : next_states}

    return read_template('template/parsers/state_16.txt', binding)

def add_state_without_select(state_name, next_state):

    binding = { 'state_name' : state_name, 'next_state' : next_state }

    return read_template('template/parsers/state_without_select_16.txt', binding)

def add_state_type_3(state_name , next_state, header_name):

    binding = { 'state_name' : state_name , 'next_state' : next_state, 'header_name' : header_name }
 
    return read_template('template/parsers/state_type_3_16.txt', binding)

def add_state_type_egress_parser(state_name, next_state,  header_name):

    binding = {'state_name' : state_name , 'next_state' : next_state, 'header_name' : header_name}

    return read_template('template/parsers/egress_parser_state.txt', binding)

def add_table(tbl_name, matches, actions, tbl_size, version):
    """
    This method returns the table definition with generic match-actions

    :param tbl_name: the name of the table
    :type tbl_name: str
    :param matches: the fields and matching method
    :type matches: str
    :param actions: the possible actions of the table
    :type actions: str
    :param tbl_size: the size of the table
    :type tbl_size: int
    :returns:  str -- the code in plain text
    :raises: None

    """
    binding = {
        'tbl_name': tbl_name,
        'matches' : matches,
        'actions' : actions,
        'tbl_size': tbl_size}

    if version == 14:
        return read_template('template/tables/table.txt', binding)
    else:
        return read_template('template/tables/table_16.txt', binding)

def apply_table(tbl_name):
    """
    This method returns the apply statement used in the control flow

    :param tbl_name: the name of the table
    :type tbl_name: str
    :returns:  str -- the code in plain text
    :raises: None

    """
    return read_template('template/controls/apply_table.txt', {'tbl_name': tbl_name})

def control(fwd_tbl, applies):
    """
    This method returns the apply statement and apply forward_table used in the control flow

    :param tbl_name: the name of the table
    :type tbl_name: str
    :param applies: the apply statement for other table
    :type applies: str
    :returns:  str -- the code in plain text
    :raises: None

    """
    d = { 'fwd_tbl' : fwd_tbl, 'applies': applies }
    return read_template('template/controls/ingress.txt', d)

def add_control_block_16(block_name, actions, tables, applies, arguments):

    binding = { 'block_name' : block_name, 'actions' : actions,
                 'tables' : tables, 'applies' : applies, 'arguments' : arguments }

    return read_template('template/controls/control_block_16.txt', binding)

def add_main_module():

    return '\nPipeline(IngressParser(), Ingress(), IngressDeparser(), EgressParser(), Egress(), EgressDeparser() ) pipe; \nSwitch(pipe) main;\n'

def cli_commands(fwd_tbl, ):
    """
    This method returns the commands for installing rules of table

    :param fwd_tbl: the name of the forwarding table
    :type fwd_tbl: str
    :returns:  str -- the code in plain text
    :raises: None

    """
    return read_template('template/commands/forward.txt', { 'fwd_tbl' : fwd_tbl})

def add_rule(tbl_name, action, match_value, params=''):
    """
    This method returns the command for installing a rule to a table

    :param tbl_name: the name of the table
    :type tbl_name: str
    :param match_value: the value to match on
    :type match_value: str
    :param action: the action that will be invoked if matched
    :type action: str
    :param params: the action parameters
    :type params: str
    :returns:  str -- the code in plain text
    :raises: None

    """
    binding = {
        'tbl_name': tbl_name,
        'action' : action,
        'match_value' : match_value,
        'params': params
    }
    return read_template('template/commands/add_rule.txt', binding)

def default_nop(tbl_name):
    """
    This method returns the command for installing the default action _nop for a table

    :param tbl_name: the name of the table
    :type tbl_name: str
    :returns:  str -- the code in plain text
    :raises: None

    """
    return add_default_rule(tbl_name, '_nop')

def add_header_field(field_name, field_width, version):
    """
    This method returns header field declaration

    :param field_name: the name of the field
    :type field_name: str
    :param field_width: the size in bit of the field
    :type field_width: int
    :returns:  str -- the code in plain text
    :raises: None

    """
    if version == 14:
        return '\t\t{0: <8}: {1};\n'.format(field_name, field_width)
    else:
        return '\tbit<{1}> {0};\n'.format(field_name, field_width)

def add_header(header_type_name, field_dec, version):
    """
    This method returns a header definition with its fields description

    :param header_type_name: the type name of the header
    :type header_type_name: str
    :param field_dec: the field description of the header
    :type field_dec: str
    :returns:  str -- the code in plain text
    :raises: None

    """
    binding = {'header_type_name': header_type_name, 'field_dec': field_dec}

    if version == 14:
        return read_template('template/headers/generic.txt', binding)
    else:
        return read_template('template/headers/generic_16.txt', binding)

def add_metadata():

    return read_template('template/structs/metadata.txt')

def add_ingress_headers(header_dec):
    binding = {'header_dec' : header_dec}
    return read_template('template/structs/ingress_headers.txt', binding)

def add_egress_headers(header_dec):
    binding = {'header_dec' : header_dec}
    return read_template('template/structs/egress_headers.txt', binding)

def add_struct_item(item_type_name, item_name):

    return '\t{0: <8} {1};\n'.format(item_type_name, item_name)


def add_metadata_instance(header_type_name, instance_name):
    """
    This method returns a code block that instantiates a metadata instance

    :param header_type_name: the type name of the header
    :type header_type_name: str
    :param instance_name: the identifier of the metadata
    :type instance_name: str
    :returns:  str -- the code in plain text
    :raises: None

    """
    binding = {'header_type_name': header_type_name, 'instance_name': instance_name}
    return read_template('template/headers/metadata.txt', binding)

def select_case(select_key, next_state):
    """
    This method returns select case for a parser

    :param select_key: the action to read registers
    :type select_key: str
    :param next_state: the next state associated with the select key
    :type next_state: str
    :returns:  str -- the code in plain text
    :raises: None

    """
    return '\t\t{0: <8}: {1};\n'.format(select_key, next_state)


def add_parser(header_type_name, header_name, parser_state_name, select_field, next_states):
    """
    This method returns a parser definition for a header

    :param header_type_name: the type name of the header
    :type header_type_name: str
    :param header_name: the name of a header instance to extract
    :type header_name: str
    :param parser_state_name: the name of this parser
    :type parser_state_name: str
    :param select_field: the header field that used to select the next parser
    :type select_field: str
    :param next_states: the possible next states
    :type next_states: str
    :returns:  str -- the code in plain text
    :raises: None

    """
    binding = {'header_type_name': header_type_name, 'header_name': header_name,
             'parser_state_name': parser_state_name, 'select_field': select_field,
             'next_states': next_states}
    return read_template('template/parsers/parse_generic.txt', binding)

def add_parser_without_select(header_type_name, header_name, parser_state_name,
        next_state):
    """
    This method returns a parser without select statement

    :param header_type_name: the type name of the header
    :type header_type_name: str
    :param header_name: the name of a header instance to extract
    :type header_name: str
    :param parser_state_name: the name of this parser
    :type parser_state_name: str
    :param next_states: the possible next states
    :type next_states: str
    :returns:  str -- the code in plain text
    :raises: None

    """
    binding = {'header_type_name': header_type_name, 'header_name': header_name,
             'parser_state_name': parser_state_name, 'next_state': next_state}
    return read_template('template/parsers/parse_no_select.txt', binding)

def add_compound_action(action_name, params, instruction_set):
    """
    This method returns a compound action

    :param action_name: the name of the compound action
    :type action_name: str
    :param params: the parameters for the action
    :type params: str
    :param instruction_set: the instruction set of this compound action
    :type instruction_set: str
    :returns:  str -- the code in plain text
    :raises: None

    """
    binding = {'action_name' : action_name, 'params': params,
                'instruction_set': instruction_set}
    return read_template('template/actions/compound_action.txt', binding)

def add_register(register_name, element_width, nb_element ,version):
    """
    This method returns a register definition

    :param register_name: the name of the register
    :type register_name: str
    :param element_width: the size of an element in the register
    :type element_width: int
    :param nb_element: the number of elements in the register
    :type nb_element: int
    :returns:  str -- the code in plain text
    :raises: None

    """
    binding = {'register_name': register_name, 'element_width': element_width,
                 'nb_element': nb_element}

    if version == 14:
        return read_template('template/states/register.txt', binding)
    else: 
        return read_template('template/states/register_16.txt', binding)

def register_actions(read_set, write_set, version):
    """
    This method returns two action: read and write to a set of registers

    :param read_set: the action to read registers
    :type read_set: str
    :param write_set: the action to write to registers
    :type write_set: int
    :returns:  str -- the code in plain text
    :raises: None

    """
    binding = {'read_set' : read_set, 'write_set': write_set}

    if version == 14:
        return read_template('template/actions/register_actions.txt', binding)
    else:
        return read_template('template/actions/register_actions_16.txt', binding)

def register_read(register, field, index, element_width, version):
    """
    This method returns a primitive action: read a register at a specific index

    :param register: the register name
    :type register: str
    :param field: the field to put the data to
    :type field: int
    :param index: the index on the register
    :type index: int
    :returns:  str -- the code in plain text
    :raises: None

    """
    binding = {'register' : register, 'field': field, 'index': index , 'width' : element_width}

    if version == 14:
        return read_template('template/actions/read_action.txt', binding)
    else:
        return read_template('template/actions/read_action_16.txt', binding)

def register_write(register, field, index, element_width, version):
    """
    This method returns a primitive action: write a register at a specific index

    :param register: the register name
    :type register: str
    :param field: the field to get the data from
    :type field: int
    :param index: the index on the register
    :type index: int
    :returns:  str -- the code in plain text
    :raises: None

    """
    binding = {'register' : register, 'field': field, 'index': index ,'width' : element_width}

    if version == 14:
        return read_template('template/actions/write_action.txt', binding)
    else:
        return read_template('template/actions/write_action_16.txt', binding)

def add_udp_header(version):
    """
    This method returns the UDP header definition
    :returns:  str -- the UDP header in plain text
    :raises: None

    """
    if version == 14:
        return read_template('template/headers/udp.txt')
    else: 
        return read_template('template/headers/udp_16.txt')

def add_udp_parser(other_states='', checksum=False):
    """
    This method returns the UDP parser. It's possible
    to provide an option to a next state along the default ingress

    :param other_states: other options in 'return select' statement
    :type other_states: str
    :param checksum: include checksum calculation
    :type checksum: bool
    :returns:  str -- the code in plain text
    :raises: None

    """
    next_states = other_states + select_case('default', 'ingress')
    binding = {'next_states' : next_states}
    if checksum:
        return read_template('template/parsers/parse_udp_checksum.txt', binding)
    else:
        return read_template('template/parsers/parse_udp.txt', binding)

def udp(other_states=''):
    """
    This method returns the UDP header and parser. It's possible
    to provide an option to a next state along the default ingress

    :param other_states: other options in 'return select' statement
    :type other_states: str
    :returns:  str -- the code in plain text
    :raises: None

    """
    return (add_udp_header(14) + add_udp_parser(other_states))

def timestamp_header(version):
    """
    This method returns the timestamp header definition
    """
    return read_template('template/headers/timestamp.txt')

def parser_start(next_parser='parse_ethernet'):
    """
    This method returns the start of the parser
    """
    parser_str = 'parser start { return %s; }\n'  % next_parser

    return parser_str

def Ingress_parser_16(states_dec, parser_name):

    binding = { 'ParserName' : parser_name, 'states_dec' : states_dec } 
    return read_template('template/parsers/Ingress_parser_16.txt' , binding)

def Egress_parser_16(parser_name , states_dec):

    binding = {'ParserName' : parser_name, 'states_dec' : states_dec }
    return read_template('template/parsers/Egress_parser_16.txt' , binding)