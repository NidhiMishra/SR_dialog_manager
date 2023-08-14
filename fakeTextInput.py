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


questions=[
    "Hello Nadine",
    "My name is Felix",
    "I am a student in the marketing department at the business school",
    "I study consumer behaviour",
    "Yes but interesting",
    "Can you introduce yourself",
    "You look beautiful today",
    "It is so nice to talk with you",
    "How do you feel today",
    "Why do you feel that way",
    "What are some things you can do",
    "What are some of your hobbies",
    "My hobby is playing tennis",
    "What are the jobs that you can do in the future",
    "Could you remember my name",
    "What is my hobby?",
    "What is my study",
    "How can you be useful in a business setting",
    "Can you remember some things I asked you earlier in this conversation",
    "Goodbye"
]

def startListening():
    hi_client = ThriftTools.ThriftClient(IP,Inputs.constants.DEFAULT_HANDINPUT_PORT, HI_Service, 'Hand Input')
    while not hi_client.connected:
        hi_client.connect()

    print("start working...")
    while True:
        for question in questions:
            while not hi_client.connected:
                hi_client.connect()
            raw_input("[Press Enter]")
            print "User: ",question
            hi_client.client.handInputRecongized(question)
        print "End of Question!!\n\n"





if __name__ == "__main__":
    startListening()
