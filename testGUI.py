__author__ = 'IMI-Demo'

import sys
sys.path.append("gen-py")
sys.path.append("i2p/tools/py")

import Inputs.SpeechGuiService as GUI_Service
from Inputs.ttypes import *
import Inputs.constants

from I2P.ttypes import *
from thrift.transport import TSocket
import ThriftTools
import time

import socket

IP = socket.gethostbyname(socket.gethostname())
print IP

gui_client = ThriftTools.ThriftClient("localhost",Inputs.constants.DEFAULT_SPEECHGUI_PORT,GUI_Service,'Speech GUI')
gui_client.connect()

id=1
while True:
    gui_client.client.updateText(str(id))
    time.sleep(5)
    id+=1