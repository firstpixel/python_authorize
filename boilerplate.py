 #!/usr/bin/env python2
# coding: latin-1
import sys, json, datetime;
from array import *
import os
import sys
import atexit
 
class Testing:
    
    def __init__(self):

        k = 0
        try:
            while True:
                for line in iter(sys.stdin.readline, b''):
                    k = k + 1
                    print line
        except KeyboardInterrupt:
            sys.stdout.flush()
            pass
        print k


test = Testing()