# This file handle dialogue response from the virtual human
# based on the current emotional states

import os
import sys
import speech
import math
import random
import time
#sys.path.append("../")
sys.path.append("gen-py")
sys.path.append("i2p/tools/py")
import Definition
import time

import cPickle as pickle
import nltk
import re


from copy import copy

from Inputs.ttypes import *
import Inputs.constants

import Control.AgentControl as AgentControl_Service
import Control.constants
import Control.ttypes




from I2P.ttypes import *
from thrift.transport import TSocket
#to ease client server creation in python
from Inputs.ttypes import *
import ThriftTools
import I2PTime




if __name__=='__main__':
    import socket

    IP = socket.gethostbyname(socket.gethostname())
    print IP

    ip_address=IP
    robot_address=IP
    

    vh_client = ThriftTools.ThriftClient(robot_address,9090,AgentControl_Service,'SmartBody')
    vh_client.connect()
    print "Connected to Robot!!!"

    while 1:
        pass

   
