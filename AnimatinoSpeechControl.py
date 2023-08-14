__author__ = 'IMI-Demo'

import sys
sys.path.append("../../i2p/i2pThrift/gen-py")
sys.path.append("../../i2p/i2pThrift/tools/py")

import time

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

class AnimationSpeechControl:
    def __init__(self):
        self.getClientConnection()

    def getClientConnection(self):
        self.client = ThriftTools.ThriftClient("localhost",9090,AgentControl_Service,'SmartBody')
        while not self.client.connected:
            self.client.connect()
        print "Connection is built!!"

    def interactiveControl(self):
        while True:
            sentence=raw_input("Speak: ").lower()
            animation=raw_input("Animation: ")
            self.synchronizedExecution(sentence,animation)

    def scriptControl(self,scripts):
        while True:
            self.pause()
            for script in scripts:
                if script[0]=="synExe":
                    self.onceExecution(script[1],script[2],script[3])
                elif script[0]=="synExeSmile":
                    self.onceExecutionWithSmile(script[1],script[2],script[3])

    def synchronizedExecution(self,sentence,animation,sTime=0,emotion=None):
        if animation!="":
            self.client.client.touchTarget(animation)
        if sentence!="":
            sentence=self.speechTone(sentence,emotion)
            self.client.client.speak(sentence,10)
            print "Robot: ", sentence
        if sTime>0:
            time.sleep(sTime)

    def onceExecutionWithSmile(self,sentence,animation,sTime,emotion=None):
        self.synchronizedExecution(sentence,animation,sTime,emotion)
        self.smile()
        self.pause()

    def onceExecution(self,sentence,animation,sTime,emotion=None):
        self.synchronizedExecution(sentence,animation,sTime,emotion)
        self.pause()

    def smile(self):
        self.client.client.touchTarget("smile")

    def pause(self):
        raw_input("[Press any key to continue]")

    def speechTone(self,_str, emotion):
        if emotion == "angry":
            res="<voice emotion='cross'>"+_str+"</voice>"
            return res
        elif emotion == "happy":
            res="<voice emotion='happy'>"+_str+"</voice>"
            return res
        else:
            return _str






if __name__=="__main__":
    customerFocusedScript=[
        ["synExeSm"
         ""
         "ile","Hello Felix, it makes me so happy to see you again! How is the new shirt you bought last week","Business_Static",6],
        ["synExeSmile","We have 5 kinds of hats with different colors","Business_Introduction_Pointing",4],
        ["synExeSmile","Why you do not try this one on","Business_Recommand",4],
        ["synExeSmile","It looks great on you","Business_Static",3,"happy"],
        ["synExeSmile","The blue looks better on you","Business_Recommand",4],
        ["synExe","Thank you Felix, see you soon","LOOKUP_Waving",0]
    ]

    productFocusedScript=[
        ["synExeSmile","Hello Felix, it makes me so happy to see you again! How is the new shirt you bought last week","Business_Static",6],
        ["synExeSmile","We have 5 kinds of hats with different colors","Business_Introduction_Pointing",4],
        ["synExeSmile","It is made of cotton","Business_Static",3],
        ["synExeSmile","No, we have only this color","Business_Static",3],
        ["synExeSmile","25 dollars","Business_Static",3],
        ["synExeSmile","Thank you","Business_Thank_You",3]
    ]

    control=AnimationSpeechControl()
    #control.scriptControl(customerFocusedScript)
    control.scriptControl(productFocusedScript)