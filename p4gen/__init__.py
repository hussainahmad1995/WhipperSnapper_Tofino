"""
A python module that generates P4 benchmarking programs
.. moduleauthor:: Tu Dang <huynh.tu.dang@usi.sh>
"""

from subprocess import call
from pkg_resources import resource_filename

def copy_scripts(output_dir):
    call(['cp', resource_filename(__name__, 'template/run_tofino_switch.sh'), output_dir])
    call(['cp', resource_filename(__name__, 'template/run_tofino_test.py'), output_dir])
    # call(['cp', resource_filename(__name__, 'tofino/headers_test'), output_dir])