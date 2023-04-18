#!/usr/bin/env python

import argparse
from packet_modification.bm_modification import benchmark_modification_16

features = ['add-header' , "rm-header" ]                     # Packet Modification
            
def main():
    parser = argparse.ArgumentParser(description='A programs that generate a'
                            ' P4 program for benchmarking a particular feature')
    parser.add_argument('--feature', choices=features,
                help='select a feature for benchmarking')
    # Processing options
    parser.add_argument('--tables', default=1, type=int, help='number of tables')
    parser.add_argument('--table-size', default=1, type=int,
                            help='number of rules in the table')
    parser.add_argument('--headers', default=1, type=int, help='number of headers')
    parser.add_argument('--fields', default=1, type=int, help='number of fields')

    args = parser.parse_args()

    if args.feature == 'add-header':
        benchmark_modification_16(args.headers, args.fields, 'add')
    elif args.feature == 'rm-header':
        benchmark_modification_16(args.headers, args.fields, 'rm')

if __name__=='__main__':
    main()
