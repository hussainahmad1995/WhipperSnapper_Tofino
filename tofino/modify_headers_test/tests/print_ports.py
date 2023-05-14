#/usr/bin/python3

import os 
import sys

class P4ProgramTest(BfRuntimeTest):

    def setup(self):
        self.swports = []

        for (device , port , ifname) in ptf.config['interfaces']:
            self.swports.append(portt)

        print("SW Port : " , self.swports)

