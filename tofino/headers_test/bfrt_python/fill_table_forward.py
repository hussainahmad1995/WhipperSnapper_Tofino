from netaddr import IPAddress
from netaddr import EUI

p4 = bfrt.p4_main.pipe.Ingress

# This function can clear all the tables and later on other fixed objects
# once bfrt support is added.
def clear_all(verbose=True, batching=True):
    global p4
    global bfrt

    # The order is important. We do want to clear from the top, i.e.
    # delete objects that use other objects, e.g. table entries use
    # selector groups and selector groups use action profile members

    for table_types in (['MATCH_DIRECT', 'MATCH_INDIRECT_SELECTOR'],
                        ['SELECTOR'],
                        ['ACTION_PROFILE']):
        for table in p4.info(return_info=True, print_info=False):
            if table['type'] in table_types:
                if verbose:
                    print("Clearing table {:<40} ... ".
                          format(table['full_name']), end='', flush=True)
                table['node'].clear(batch=batching)
                if verbose:
                    print('Done')
clear_all(verbose=True)

# #add entries to forward_table
forward_table = p4.forward_table
test_table = p4.test_tbl

#add entry for the the address of the enp4s0f0 - port 66 
# forward_table.add_with_forward(dstAddr=EUI('00:a0:c9:00:00:00'),   port=66)

#entry represents veth-251 MAC address
# forward_table.add_with_forward(dstAddr=EUI('c2:15:a9:1b:a9:c4'),   port=64)

#entry represent veth-250 MAC addresss
forward_table.add_with_forward(dstAddr=EUI("42:70:c7:3b:c5:2c"),   port=64)
bfrt.complete_operations()

# Final programming
print("""
******************* PROGAMMING RESULTS *****************
""")
print ("Table forward_table:")
forward_table.dump(table=True)
print ("Table test_tbl:")
test_table.dump(table=True)