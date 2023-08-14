__author__ = 'Zhang Juzheng'


import sys
sys.path.append("../../i2p/i2pThrift/gen-py")
sys.path.append("../../i2p/i2pThrift/tools/py")

import Inputs.HandInputService as HI_Service
from Inputs.ttypes import *
import Inputs.constants


from I2P.ttypes import *
from thrift.transport import TSocket
#to ease client server creation in python
import ThriftTools
import I2PTime






import socket

IP = socket.gethostbyname(socket.gethostname())
print IP


def startListening():
    hi_client = ThriftTools.ThriftClient(IP,Inputs.constants.DEFAULT_HANDINPUT_PORT, HI_Service, 'Hand Input')
    while not hi_client.connected:
        hi_client.connect()

    print("start working...")
    while True:
        while not hi_client.connected:
            hi_client.connect()
        input=raw_input("User: ")
        if input!="":
            hi_client.client.handInputRecongized(input)





if __name__ == "__main__":
    startListening()
