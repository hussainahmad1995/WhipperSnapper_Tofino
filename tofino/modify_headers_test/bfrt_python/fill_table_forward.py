from netaddr import IPAddress
from netaddr import EUI

p4 = bfrt.add_headers_main.pipe.Ingress

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
ipv4_host = p4.ipv4_host
test_table = p4.test_tbl

#dst addr 3 represents the atlas 3 
#dst addr 23 represents the atlas 23

ipv4_host.add_with_forward(dst_addr=IPAddress("10.0.0.3"),   port=148)
ipv4_host.add_with_forward(dst_addr=IPAddress("10.0.0.23"),   port=52)

test_table.add_with_add_headers(dst_addr=IPAddress("10.0.0.3"))
test_table.add_with_add_headers(dst_addr=IPAddress("10.0.0.23"))


bfrt.complete_operations()

# Final programming
print("""
******************* PROGAMMING RESULTS *****************
""")
print ("Table ipv4_host:")
ipv4_host.dump(table=True)
print ("Table test_tbl:")
test_table.dump(table=True)

