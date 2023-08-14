import os
import sys
import math
import random
import time
#sys.path.append("../")
sys.path.append("gen-py")
sys.path.append("i2p/tools/py")
sys.path.append("New_Functionality")
import Definition
import time

import cPickle as pickle
import nltk
import re
from predefinedSentence import *


from copy import copy


from Inputs.ttypes import *
import Inputs.constants

import Control.AgentControl as AgentControl_Service
import Control.constants
import Control.ttypes

import VHSimpleService.VHSimpleService as VH_Service
import VHSimpleService.constants
import VHSimpleService.ttypes

#----------------------------------------------------
# Added Dialogue Service - Lijun 7 Sep 2015
#----------------------------------------------------
# for Dialogue Manager
import Inputs.DialogueManagerService as Dialogue_Service
#----------------------------------------------------

#for cerevoice
import Feedback.AgentFeedbackService as Feedback_Service
from Feedback.ttypes import *
import Feedback.constants


from I2P.ttypes import *
from thrift.transport import TSocket
#to ease client server creation in python
from Inputs.ttypes import *
import ThriftTools
import I2PTime

from Question import *
from nltk.metrics import edit_distance
import SearchConcepts
import math
from QuestionAnswering import QuestionAnswering
import ChatbotWrapper
from userQuestion import userQuestion
from utils import randomFunc
from utils import *
from textblob import TextBlob,Word

class FrechSpeaking:
    def __init__(self):
        self.connectRobot()
        print "Connected"

    def connectRobot(self):
        robot_address="155.69.54.66"
        self.client = ThriftTools.ThriftClient(robot_address,9090,AgentControl_Service,'SmartBody')
        while not self.client.connected:
            self.client.connect()

    def answerQuestion(self):
        answers=["J'habite a Singapore","Je suis une receptioniste"]
        while True:
            for ans in answers:
                input=raw_input("speaking?")
                self.client.client.speak(ans,30)


if __name__ == "__main__":
    speak=FrechSpeaking()
    speak.answerQuestion()
