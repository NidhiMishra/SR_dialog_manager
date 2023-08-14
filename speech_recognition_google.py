import speech_recognition as sr
import pyaudio
import time
import sys
#sys.path.append("../")
sys.path.append("gen-py")
sys.path.append("i2p/tools/py")

import Inputs.SpeechGuiService as GUI_Service
import Inputs.SpeechRecognitionService as SR_Service
from Inputs.ttypes import *
import Inputs.constants


from I2P.ttypes import *
from thrift.transport import TSocket
#to ease client server creation in python
import ThriftTools
import I2PTime

from nltk.metrics import edit_distance


sentenceRecognized=''
r=sr.Recognizer()


import socket

IP = socket.gethostbyname(socket.gethostname())
print IP

pic_input=["take a picture",
           "take a photo",
           "take my picture",
           "take my photo"]

def checkSent(sentence):
    for sent in pic_input:
        if sent in sentence:
            return True
    return False
                
def startListening():
    #sr_client = ThriftTools.ThriftClient('155.69.52.73', Inputs.constants.DEFAULT_SPEECHRECOGNITION_SERVICE_PORT, SR_Service, 'Speech Recognition')
    sr_client = ThriftTools.ThriftClient(IP, 1200,SR_Service, 'Speech Recognition')
    rl_client = ThriftTools.ThriftClient("155.69.54.66", 12038,SR_Service, 'Speech Recognition for Reactive Layer')
    gui_client = ThriftTools.ThriftClient("localhost",Inputs.constants.DEFAULT_SPEECHGUI_PORT,GUI_Service,'Speech GUI')
    while True:
        try:
            print("AAAAAAAAAAAA")
            sr_client.connect()
            gui_client.connect()
            rl_client.connect()
        except TSocket.TTransportException:
            print 'can not connect to Speech Recognition service'
            time.sleep(1)
        except:
            break
        print("TTTTTTTTTTTTTTT")
       
        while True:
            while not sr_client.connected:
                sr_client.connect()
            while not gui_client.connected:
                gui_client.connect()
            print("Start Listening")
            with sr.Microphone() as source:
                audio = r.listen(source)
                print("End Listening")
                try:
                    sentenceRecognized=r.recognize(audio)
                    print("input: "+sentenceRecognized)
                    flag=checkSent(sentenceRecognized.lower())
                    if not flag:
                        sr_client.client.sentenceRecognized('Microphone', I2PTime.getTimeStamp(), sentenceRecognized, 0.0)
                    else:
                        rl_client.client.sentenceRecognized('Microphone', I2PTime.getTimeStamp(), "TAKEPIC", 0.0)
                        print "send TakePic to reactive layer"


                    gui_client.client.updateText(sentenceRecognized)
                    sentenceRecognized=''
                    
                except LookupError:
                    #sr_client.client.sentenceRecognized('Microphone', I2PTime.getTimeStamp(), "None", 0.0)
                    print("Could not recognize the speech")
                    gui_client.client.updateText("SPEAK AGAIN")
                
                    


if __name__ == "__main__":
    startListening()
    

    

