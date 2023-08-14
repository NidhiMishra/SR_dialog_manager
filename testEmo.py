# This file handle dialogue response from the virtual human
# based on the current emotional states

import sys
import math
import random
import time
#sys.path.append("../")
sys.path.append("gen-py")
sys.path.append("i2p/tools/py")

from copy import copy

import Inputs.SpeechRecognitionService as SR_Service
import Inputs.EmotionEngineService as Emotion_Service
from Inputs.ttypes import *
import Inputs.constants

import Control.AgentControl as AgentControl_Service
import Control.constants
import Control.ttypes

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

import aiml


phraseListening=["I don't like you",
                 "You look ugly today",
                 "You are so mean",
                 "Your voice sounds sleepy",
                 "You are so boring",
                 "I don't like to talk with you",
                 "I like you so much",
                 "You look pretty today",
                 "You are so nice",
                 "Your voice sounds charming",
                 "You are so interesting",
                 "You are my best friend",
                 "Hi Nadine",
                 "Goodbye"]

pattern=[" ".join(phrase.split(", ")).lower() for phrase in phraseListening]

def matchPattern(_str,threshold):
    idx=0
    _str=_str.lower()
    for pat in pattern:
        total=len(pat)
        match=edit_distance(_str,pat)
        match=match/float(total)
        if match < threshold:
            return phraseListening[idx]
        idx+=1
    return None


class Emotion:
    def __init__(self):
        self.type=''
        self.pos=[0,0,0]
        self.intensity=0
        
    def __del__(self):
        return

class Mood:
    def __init__(self):
        self.pos=[0,0,0]
        
    def __del__(self):
        return

class CommonParameter:
    _userInput=''
    _emotion=Emotion()
    _mood=Mood()
    speaking=False
    _toChatbot=""
    chatbotResponse=""
    recogEmo=""
    
    def __init__(self):
        return
    
    def __del__(self):
        return
        

class SpeechHandler:
    def __init__(self):
        return
        
    def __del__(self):
        return

    def sentenceRecognized(self, sensorID, timestamp, sentence, confidence):
        if sentence=="None":
            pass
        elif not CommonParameter.speaking:
            CommonParameter._userInput=sentence
        
        return CommonParameter.speaking

class EmotionHandler:
    def __init__(self):
        self.emotion="None"
        return
        
    
    def __del__(self):
        return
    
    def emotion(self, timestamp, emotion_type, emotion_pos, emotion_intensity, mood):
        # update emotion and mood
        CommonParameter._mood.pos=[mood.x,mood.y,mood.z]
        CommonParameter._emotion.type=emotion_type
        CommonParameter._emotion.pos=[emotion_pos.x,emotion_pos.y,emotion_pos.z]        
        CommonParameter._emotion.intensity=emotion_intensity

        print "self.emotion: "+self.emotion
        if self.emotion=="":
            return "None"
        else:
            inputEmo=self.emotion
            self.emotion="None"
            return inputEmo
            

##        self.emotion=""
##        if not CommonParameter.recogEmo=="":
##            self.emotion=CommonParameter.recogEmo
##            CommonParameter.recogEmo=""

		
##        return self.emotion

    

class FeedbackHandler:
    def __init__(self):
        return
        
    def __del__(self):
        return
    def speakBegin(self, agentName, timestamp):
        #print 'speakBegin', agentName, timestamp
        if agentName == "Sohpie" or agentName == "Nadine":
            CommonParameter.speaking = True
        return
    def speakEnd(self, agentName, timestamp):
        #print 'speakEnd', agentName, timestamp 
        if agentName == "Sophie" or agentName == "Nadine":
            CommonParameter.speaking = False
        return  

class DialogueManager:
    def __init__(self, client):
        self.client=client
        self.userInput=''
        self._emotion=None
        self._mood=None
    
    def __del__(self):
        return

    def randomChoose(self,List):
        '''randomly choose an element in a list'''
        length=len(List)
        rand=random.randint(0,length-1)
        return List[rand]

    def moodLevel(self):
        mood=self._mood.pos[0]
        if mood>=-0.2 and mood<0:
            return "Slight Angry"
        elif mood>=-0.4 and mood<-0.2:
            return "Mild Angry"
        elif mood>=-0.7 and mood<-0.4:
            return "Very Angry"
        elif mood>=-1 and mood<-0.7:
            return "Crazy Angry"
        elif mood>=0 and mood<0.2:
            return "Slight Happy"
        elif mood>=0.2 and mood<0.4:
            return "Mild Happy"
        elif mood>=0.4 and mood<0.7:
            return "Very Happy"
        else:
            return "Crazy Happy"
       

    def expIntensity(self):
        exp=None
        i=None
        if self._emotion.pos[0]*self._mood.pos[0]>= 0:
            i=self._emotion.intensity+math.fabs(self._mood.pos[0])
            #i=i/2.0
            if i>1:
                i=1
            if self._emotion.type=='GRATITUDE':
                exp=I2P.ttypes.Facial_Expression.HAPPINESS
            elif self._emotion.type=='ANGER':
                exp=I2P.ttypes.Facial_Expression.ANGER
            
        else:
            if self._emotion.intensity >= math.fabs(self._mood.pos[0]):
                i=self._emotion.intensity-math.fabs(self._mood.pos[0])
                if i>1:
                    i=1
                if self._emotion.type=='GRATITUDE':
                    exp=I2P.ttypes.Facial_Expression.HAPPINESS
                elif self._emotion.type=='ANGER':
                    exp=I2P.ttypes.Facial_Expression.ANGER
                
            else:
                i=math.fabs(self._mood.pos[0])-self._emotion.intensity
                if i>1:
                    i=1
                if self._mood.pos[0]>=0:
                    exp=I2P.ttypes.Facial_Expression.HAPPINESS
                else:
                    exp=I2P.ttypes.Facial_Expression.ANGERS
            
    
        return (exp,i)
                

    def reply(self,sentence):
        print self._mood.pos[0]
            
        exp,i=self.expIntensity()
        moodLevel=self.moodLevel()
        print moodLevel
        Alist=None
        if self._emotion.pos[0]>=0:
            AList=PositiveAnimation[moodLevel]
        else:
            AList=NegativeAnimation[moodLevel]
        s=speechTone(sentence,moodLevel)
        a=self.randomChoose(AList)
        if a != "None":
                self.client.client.touchTarget(a)
        if self._mood.pos[0]<-0.4:
            self.client.client.touchTarget("angry")
        self.client.client.speak(s,10)
    
        print "Nadine: "+s
        
        
    def response(self):
        if self.userInput=='':
            pass
     
       
        ###### Positive Words#########

        elif self.userInput in PositiveComment:
            print self._mood.pos[0]
            
            exp,i=self.expIntensity()
            moodLevel=self.moodLevel()
            print moodLevel
            SList=PositiveResponse[moodLevel]
            AList=PositiveAnimation[moodLevel]
            s=self.randomChoose(SList)
            a=self.randomChoose(AList)
            self.client.client.playAnimation(a)
            self.client.client.setFaceExpression(exp,i*10)
            self.client.client.speak(s,10)
            self.userInput==''
            if a != "None":
                self.client.client.touchTarget(a)
            print "Nadine: "+s
            #print moodLevel

        

       ###### Negative Words######### 

        elif self.userInput in NegativeComment:
            moodLevel=self.moodLevel()
            
            print self._mood.pos[0]
            
            SList=NegativeResponse[moodLevel]
            print moodLevel
                
            exp,i=self.expIntensity()
    
            
            AList=NegativeAnimation[moodLevel]
            s=self.randomChoose(SList)
            a=self.randomChoose(AList)
            if a != "None":
                self.client.client.touchTarget(a)
            if self._mood.pos[0]<-0.4:
                self.client.client.touchTarget("angry")
            self.client.client.speak(s,10)

            print "Nadine: "+s
            
            self.userInput==''
            

           

if __name__=='__main__':
    ip_address='155.69.53.137'
    robot_address="155.69.53.137"
    

    ## starting emotion service
    emotion_handler = EmotionHandler()
    #emotion_server = ThriftTools.ThriftServerThread(Inputs.constants.DEFAULT_EMOTIONENGINE_SERVICE_PORT,Emotion_Service,emotion_handler,'Emotion Engine Service','localhost')
    emotion_server = ThriftTools.ThriftServerThread(Inputs.constants.DEFAULT_EMOTIONENGINE_SERVICE_PORT,Emotion_Service,emotion_handler,'Emotion Engine Service',ip_address)
    emotion_server.start()


                

        
    
