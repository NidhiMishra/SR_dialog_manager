# This file handle dialogue response from the virtual human
# based on the current emotional states

import os
import sys
import csv
import subprocess
import math
import random
import time
from framelen import AudioDuration
from Mic_Controller import AudioUtilities
#sys.path.append("../")
sys.path.append("gen-py")
sys.path.append("i2p/tools/py")
import Definition
import time

import cPickle as pickle
import nltk
import re
from predefinedSentence import *

from copy import copy


from Inputs.ttypes import *
import Inputs.constants
import threading


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
from ChatbotWrapper import chatbot
from userQuestion import userQuestion
from utils import randomFunc
from utils import *
from textblob import TextBlob,Word
from news_online import OnlineNews
#import mtranslate as translate
from Translator import Translator
from datetime import datetime
from FaceEmotionPool import *
# import ChineseTTS
from volumeControl import volumeControl
from gtts import gTTS
from pygame import mixer
from google.cloud import translate
###for korean
# from google.cloud import texttospeech
###for korean
import mmap
from collections import Counter
import json
#from google.cloud import bigquery
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

    def getMoodStr(self):
        state=self.getMoodState()
        intensity=self.getMoodIntensity()
        if state=="Neutral":
            return " 0.5"
        else:
            return state+" "+str(intensity)

    def getMoodIntensity(self):
        res=0
        for p in self.pos:
            res+=p*p
        res=math.sqrt(res)
        return res

    def getMoodState(self):
        if abs(self.pos[0])<1e-3 and abs(self.pos[1])<1e-3 and abs(self.pos[2])<1e-3:
            return "Neutral"
        elif self.pos[0]>=0 and self.pos[1]>=0 and self.pos[2]>=0:
            return "Exuberant"
        elif self.pos[0]>=0 and self.pos[1]>=0 and self.pos[2]<0:
            return "Dependent"
        elif self.pos[0]>=0 and self.pos[1]<0 and self.pos[2]>=0:
            return "Relaxed"
        elif self.pos[0]>=0 and self.pos[1]<0 and self.pos[2]<0:
            return "Docile"
        elif self.pos[0]<0 and self.pos[1]<0 and self.pos[2]<0:
            return "Bored"
        elif self.pos[0]<0 and self.pos[1]<0 and self.pos[2]>=0:
            return "Disdainful"
        elif self.pos[0]<0 and self.pos[1]>=0 and self.pos[2]<0:
            return "Anxious"
        else:
            return "Hostile"


class ChildBotHandler:
    def __init__(self):
        self.response=None

    def __del__(self):
        return

    def childRobotCommunication(self, sentence):
        if sentence=="":
            pass
        CommonParameter._userInput=sentence.lower()
        #print "ChildRobot: ",sentence
        while CommonParameter.response==None:
            pass
        self.response=CommonParameter.response
        print "Response: ",self.response
        CommonParameter.response=None
        return self.response



class SilenceChecker(threading.Thread):
    def __init__(self,timeLimit):
        threading.Thread.__init__(self)
        self.timeLimit=timeLimit # seconds
        self.hasSilentUser=False
        self.hasUser=False
        self.reported=False

    def getSilence(self):
        if not self.reported:
            return self.hasSilentUser
        return False

    def run(self):
        print "Start Salience Detection!!!"
        while True:
            self.checkSilence()
            time.sleep(0.1)

    def stop(self):
        return

    def userAppear(self): # if user appears, start counting
        #print "User Appear!!!"
        if not self.hasUser:
            self.hasUser=True
            self._start=datetime.now()

    def userSpeaking(self): # if user speaks, count from the very beginning
        print "User Speaking!!!"
        if self.hasUser:
            self._start=datetime.now()
            self.hasSilentUser=False

    def userDisappear(self): # if user has gone, stop counting
        #print "User Disappear!!!"
        self.hasUser=False
        self.hasSilentUser=False

    def checkSilence(self):
        if self.hasUser and not self.hasSilentUser:
            _end = datetime.now()
            try:
                p_time = (_end - self._start).seconds
                if p_time >= self.timeLimit:
                    self.hasSilentUser=True
                    self.reported=False
                    print "Detected silence!!!"
            except:
                #raise Exception("Silence Detection Error!!!")
                print "Silence Detection Error!!!"


class CommonParameter:
    _userInput=''
    _lastUserInput=''
    _emotion=Emotion()
    _mood=Mood()
    speaking=False
    _toChatbot=""
    chatbotResponse=""
    recogEmo=""
    _userName=""
    _userGender ='unknown'
    _userAge = 'unknown'
    _userEthnicity= 'unknown'
    knowledgeSent=None
    germanFlag=False
    englishFlag=False
    frenchFlag=False
    chineseFlag=False
    response=None
    recongizeFlag=True
    reportUser=False
    reportUserNum=0
    numberUsers=0
    faceEmoPool=None
    speakingForFace=False # get speech if user is speaking with facial expressions
    silenceCheck=SilenceChecker(timeLimit=30)
    silenceCheck.start()
    _google_assistant_invoked=False
    _already_answered=False
    #_language=''
    _language = 'en-us'
    _face_rec_name=''
    _face_rec_thread_started=False
    AIAYesResponse = ""
    AIANoResponse = ""
    AIAShortAnswer_Flag = False

    def __init__(self):
        return
    
    def __del__(self):
        return


class FaceEmotionHandler:
    def __init__(self):
        CommonParameter.faceEmoPool=FaceEmotionPool(numPreviousFrames=10,threshold=70,coolTime=4)

    def getFacialEmotions(self, userFaceEmotion):
        CommonParameter.faceEmoPool.process(userFaceEmotion)
        #self.printFacialEmotions(userFaceEmotion)

    def printFacialEmotions(self,userFaceEmotion):
        print "\n"
        print "Joy: ", userFaceEmotion.joy
        print "Fear: ",userFaceEmotion.fear
        print "Disgust: ", userFaceEmotion.disgust
        print "Sadness: ",userFaceEmotion.sadness
        print "Anger: ",userFaceEmotion.anger
        print "Surprise: ",userFaceEmotion.surprise
        print "Contempt: ",userFaceEmotion.contempt
        print "Smile: ",userFaceEmotion.smile
        print "Valence: ",userFaceEmotion.valence
        print "Engagement: ",userFaceEmotion.engagement
        print "Gender: %s" % userFaceEmotion.gender
        print "\n"



class SpeechHandler:
    def __init__(self):
        self.stopCue=["stop it","shut up","stop"]

    def __del__(self):
        return

    def sentenceRecognized(self, sensorID, timestamp, sentence, confidence):
        print "\nReceived User Input: ", sentence,"\n"
        CommonParameter.silenceCheck.userSpeaking()
        if not CommonParameter.speaking or CommonParameter.speakingForFace or sentence.lower() in self.stopCue:
            CommonParameter._userInput=sentence.lower()
            CommonParameter.speakingForFace=False
            #CommonParameter.lastTime=time.clock()
        return CommonParameter.speaking

    def LanguageRecognized(self, sensorID, timestamp, language):
        if language in ["G", "de-DE"]:
            CommonParameter.germanFlag=True
            CommonParameter.englishFlag=False
            CommonParameter.frenchFlag=False
            CommonParameter.chineseFlag = False
            print "&&&&&&&&&&&&&&&&&&&&&&"
            print "Current Language is German"
            print "&&&&&&&&&&&&&&&&&&&&&&"
        elif language in ["E","en-US"]:
            print "&&&&&&&&&&&&&&&&&&&&&&"
            print "Current Language is English"
            print "&&&&&&&&&&&&&&&&&&&&&&"
            CommonParameter.germanFlag=False
            CommonParameter.englishFlag=True
            CommonParameter.frenchFlag=False
            CommonParameter.chineseFlag = False
        elif language in ["F","fr-FR"]:
            print "&&&&&&&&&&&&&&&&&&&&&&"
            print "Current Language is French"
            print "&&&&&&&&&&&&&&&&&&&&&&"
            CommonParameter.germanFlag=False
            CommonParameter.englishFlag=False
            CommonParameter.frenchFlag=True
            CommonParameter.chineseFlag = False
        elif language in ["C","zh-CN"]:
            print "&&&&&&&&&&&&&&&&&&&&&&"
            print "Current Language is Chinese"
            print "&&&&&&&&&&&&&&&&&&&&&&"
            CommonParameter.germanFlag=False
            CommonParameter.englishFlag=False
            CommonParameter.frenchFlag=False
            CommonParameter.chineseFlag = True



class HandInputHandler:
    def __init__(self):
        return

    def __del__(self):
        return

    def handInputRecongized(self, sentence):
        CommonParameter._userInput=sentence.lower()
        CommonParameter.lastTime=time.clock()



class EmotionHandler:
    def __init__(self):
        self._emotion=""
        return


    def __del__(self):
        return

    def emotion(self, timestamp, emotion_type, emotion_pos, emotion_intensity, mood):
        # update emotion and mood
        CommonParameter._mood.pos=[mood.x,mood.y,mood.z]
        CommonParameter._emotion.type=emotion_type
        CommonParameter._emotion.pos=[emotion_pos.x,emotion_pos.y,emotion_pos.z]
        CommonParameter._emotion.intensity=emotion_intensity

        self._emotion=""
        if not CommonParameter.recogEmo=="":
            self._emotion=CommonParameter.recogEmo
            print "Send Emotion %s to the Affective System" % self._emotion
            CommonParameter.recogEmo=""
        return self._emotion


class FeedbackHandler:
    def __init__(self):
        return

    def __del__(self):
        return
    def speakBegin(self, agentName, timestamp):
        print 'speakBegin', agentName, timestamp
        if agentName == "Sophie" or agentName == "Nadine":
            CommonParameter.speaking = True
        return
    def speakEnd(self, agentName, timestamp):
        print 'speakEnd', agentName, timestamp
        print 'Here1', CommonParameter.speaking
        print 'Here2', os.path.exists("mic_mute.txt")
        if agentName == "Sophie" or agentName == "Nadine":
            CommonParameter.speaking = False
            CommonParameter.speakingForFace=False
        return

class SpeakerIdentificationHandler:
    def __init__(self):
        return

    def speakerIdentified(self, sensorID, timestamp, name, gender):
        if CommonParameter.recongizeFlag: # if recognition is activated
            try:
                print "Speaker Name is: ",name
                print "Speaker Gender is: ",gender
                if CommonParameter._userName!=name and name!="Unknown":
                    if gender in ["m","M","Male","male","Man","man"]:
                        gender="male"
                    elif gender in ["f","F","Female","female","Woman","woman"]:
                        gender="female"
                    else:
                        gender=None
                        print "Error: The gender input is out of format."
                    CommonParameter._userName = name
                    if name not in UserGender.userGender.keys() and gender!=None:
                        print "Add New User: "+name+" with Gender: "+gender
                        UserGender.userGender[name]=gender
                        UserGender.saveGender()
            except:
                print sys.exc_info()

#----------------------------------------------------------
# Added Dialogue Manager Service Handler - Lijun 7 Sep 2015
#-----------------------------------------------------------
class DialogueManagerHandler:
    def __init__(self):
        self.r =''


    def __del__(self):
        return

    # def checkReportUser(self,NumIterReportUser=100):
    #     if CommonParameter.numberUsers>0 and \
    #     CommonParameter.numberUsers % NumIterReportUser == 0:
    #         CommonParameter.reportUser=True
    #         CommonParameter.reportUserNum=CommonParameter.numberUsers

    def sendNumUser(self, NumUser):

        if not os.path.exists("G:\\IMI-PROJECTS\\i2p_Nadine_Robot\\development\\user_available.txt"):
            file = open("G:\\IMI-PROJECTS\\i2p_Nadine_Robot\\development\\user_available.txt","w")
            file.close()
        if os.path.exists("G:\\IMI-PROJECTS\\x64\\Release\\output_name.txt"):
            os.remove("G:\\IMI-PROJECTS\\x64\\Release\\output_name.txt")
            CommonParameter._face_rec_name=""
        print "Receive NumUser: ",NumUser
        CommonParameter.numberUsers=NumUser
        #self.checkReportUser()
    def beginning_face_Rec(self):
        i=0
        output=[]
        while i<3:
            f=open("G:\\IMI-PROJECTS\\x64\\Release\\1.txt","w+")
            f.close()
            time.sleep(2)
            if not os.path.exists("G:\\IMI-PROJECTS\\x64\\Release\\output_name.txt"):
                i=i+1

            else:
                f=open("G:\\IMI-PROJECTS\\x64\\Release\\output_name.txt","r+")
                output.append(f.read())
                f.close()
                os.remove("G:\\IMI-PROJECTS\\x64\\Release\\output_name.txt")
                i=i+1
        if len(output)>0:

            c = Counter(output).most_common(1)
            print (c[0][0])
            return c[0][0]
        else:
            return ""
    def Gen_Eth_Age_Estimation(self):
        # Gender - male, female, unknown
        # Age - Under 18, 18-24, 25-34, 35-44, 45-54, 55-64, 65 plus, Unknown
        # Ethnicity - Caucasian, Black African, South Asian, East Asian, Hispanic, Unknown
        Age = {}
        Gender = {}
        Ethnicity = {}

        Unknown_count = 0

        if CommonParameter._userAge == 'unknown':
            Unknown_count = Unknown_count + 1

        if CommonParameter._userGender == 'unknown':
            Unknown_count = Unknown_count + 1

        if CommonParameter._userEthnicity == 'unknown':
            Unknown_count = Unknown_count + 1

        NumIterations = 0

        while (Unknown_count >= 2) and (NumIterations < 3):
            init_time = time.time()

            # Open the Webcam demo so that Gender Age Estimation can be done
            p = subprocess.Popen(["G:\\IMI-PROJECTS\\x64\\Release\\opencv-webcam-demo.exe","--cid", "1"])
            Subprocess_Opened = True
            while Subprocess_Opened:
                if time.time() > init_time + 15:
                    p.terminate()
                    Subprocess_Opened = False
            with open('G:\\IMI-PROJECTS\\i2p_Nadine_Robot\\development\\i2p_interaction\\i2p_dialog_manager\\Output.csv', 'rb') as f:
                reader = csv.reader(f)
                for row in reader:
                    a = row[1]
                    if (a.isdigit()):
                        # print row[4] #Age
                        if str(row[4]) != 'unknown':
                            if str(row[4]) in Age:
                                Age[str(row[4])] = Age[str(row[4])] + 1
                            else:
                                Age[str(row[4])] = 1
                        # print row[5] #Ethnicity
                        if str(row[5]) != 'unknown':
                            if str(row[5]) in Ethnicity:
                                Ethnicity[str(row[5])] = Ethnicity[str(row[5])] + 1
                            else:
                                Ethnicity[str(row[5])] = 1
                        # print row[6] #Gender
                        if str(row[6]) != 'unknown':
                            if str(row[6]) in Gender:
                                Gender[str(row[6])] = Gender[str(row[6])] + 1
                            else:
                                Gender[str(row[6])] = 1
            if (len(Age) != 0):
                Age_Sorted = sorted(Age.iteritems(), key=lambda (k, v): (v, k), reverse=True)
                CommonParameter._userAge = Age_Sorted[0][0]
                print CommonParameter._userAge

            if (len(Gender) != 0):
                Gender_Sorted = sorted(Gender.iteritems(), key=lambda (k, v): (v, k), reverse=True)
                CommonParameter._userGender = Gender_Sorted[0][0]
                print CommonParameter._userGender

            if (len(Ethnicity) != 0):
                Ethnicity_Sorted = sorted(Ethnicity.iteritems(), key=lambda (k, v): (v, k), reverse=True)
                CommonParameter._userEthnicity = Ethnicity_Sorted[0][0]
                print CommonParameter._userEthnicity

            Unknown_count = 0

            if CommonParameter._userAge == 'unknown':
                Unknown_count = Unknown_count + 1

            if CommonParameter._userGender == 'unknown':
                Unknown_count = Unknown_count + 1

            if CommonParameter._userEthnicity == 'unknown':
                Unknown_count = Unknown_count + 1

            NumIterations = NumIterations + 1

    def sendInput(self, itype, aInput):
        if itype == Inputs.ttypes.InputType.USER_NAME:
            if aInput=="":
                 CommonParameter._userName=""
                 CommonParameter.silenceCheck.userDisappear()
                 print "DialogueManagerService - UserName is Empty String"
                 CommonParameter._userAge = 'unknown'
                 CommonParameter._userGender = 'unknown'
                 CommonParameter._userEthnicity = 'unknown'
                 if os.path.exists("G:\\IMI-PROJECTS\\i2p_Nadine_Robot\\development\\user_available.txt"):
                     os.remove("G:\\IMI-PROJECTS\\i2p_Nadine_Robot\\development\\user_available.txt")
                 if os.path.exists("G:\\IMI-PROJECTS\\x64\\Release\\output_name.txt"):
                     os.remove("G:\\IMI-PROJECTS\\x64\\Release\\output_name.txt")
                     CommonParameter._face_rec_name=""
            elif aInput=="Unknown":
                CommonParameter._userName = "Unknown"
                CommonParameter.silenceCheck.userAppear()
                print "DialogueManagerService - UserName is Unknown"
            else:
                print "aInput: ",aInput
                CommonParameter.silenceCheck.userAppear()
                try:
                    if "Unknown" in aInput:
                        name,gender=aInput.split(", ")
                    else:
                        name,gender=aInput.split(" , ")
                    name=name.capitalize()
                    if name in ["Skype","Unknown"]:
                        CommonParameter._userName = "Unknown"
                        print "DialogueManagerService - UserName is Unknown"
                    else:
                        if CommonParameter.recongizeFlag: # if recognition is activated
                            print "Name: "+name
                            print "Gender: "+gender

                            if gender in ["m","M","Male","male","Man","man"]:
                                gender="male"
                            elif gender in ["f","F","Female","female","Woman","woman"]:
                                gender="female"
                            else:
                                gender=None
                                print "Error: The gender input is out of format."
                            CommonParameter._userName = name
                            if name not in UserGender.userGender.keys() and gender!=None:
                                print "Add New User: "+name+" with Gender: "+gender
                                UserGender.userGender[name]=gender
                                UserGender.saveGender()
                            print "DialogueManagerService - UserName is %s" %aInput
                        else:
                            CommonParameter._userName = "Unknown"
                            print "User Recognition Service is not activated"
                except:
                    print sys.exc_info()

#-----------------------------------------------------------

class DialogueManager:
    def __init__(self,client):
        self.client=client
        self.userInput=''
        self._emotion=Emotion()
        self._mood=Mood()
        self.sent_proc=sentenceUtils()
        self.angryFlag=False
        self.lastSent=None
        self.news=OnlineNews()
        self.translator=Translator()
        #self.zh_TTS=ChineseTTS.ChinsesTTS()
        #self.zh_TTS.setClient(client)
        self.volume_control=volumeControl()


    def __del__(self):
        return

    def setCommonParameter(self,CommonParameter):
        self.CommonParameter=CommonParameter

    def getConceptNetAnswer(self,memory_client,sentence):
        res=memory_client.client.getConceptNetAnswer(sentence)
        if res=="None":
            res=self.sent_proc.clearChatBotAnswer(sentence)
        return res

    def randomChoose(self,List):
        '''randomly choose an element in a list'''
        length=len(List)
        rand=random.randint(0,length-1)
        return List[rand]

    def pleasureLevel(self):
        pleasure=self._mood.pos[0]
        if pleasure>=-0.2 and pleasure<0:
            return "Slight Angry"
        elif pleasure>=-0.4 and pleasure<-0.2:
            return "Mild Angry"
        elif pleasure>=-0.7 and pleasure<-0.4:
            return "Very Angry"
        elif pleasure>=-1 and pleasure<-0.7:
            return "Crazy Angry"
        elif pleasure>=0 and pleasure<0.2:
            return "Slight Happy"
        elif pleasure>=0.2 and pleasure<0.4:
            return "Mild Happy"
        elif pleasure>=0.4 and pleasure<0.7:
            return "Very Happy"
        else:
            return "Crazy Happy"

    def arousalLevel(self):
        arousal=self._mood.pos[1]
        if arousal>0.3:
            return "HighArousal"
        elif arousal<-0.3:
            return "LowArousal"
        else:
            return "MidArousal"

    def getAnimationFlag(self,arousalLevel):
        if arousalLevel=="HighArousal":
            rdmNum=0.2
        elif arousalLevel=="LowArousal":
            rdmNum=0.8
        else:
            rdmNum=0.5
        if random.random()>rdmNum:
            return True
        return False

    def getQuestionFlag(self):
        pad=self._mood.pos[0]+self._mood.pos[1]+self._mood.pos[2]
        if pad>=0:
            return True
        return False

    def getQuestionFreq(self):
        arousal=self._mood.pos[1]
        if arousal>0.3:
            return 2
        elif arousal<-0.3:
            return 6
        else:
            return 4





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
                    exp=I2P.ttypes.Facial_Expression.ANGER


        return (exp,i)


    #----------------------------------------------------
    # Added Answering Behaviour - Lijun 7 Sep 2015
    #----------------------------------------------------
    def defaultChatbotAnimation(self,sentence):
        # Behaviour 1: Nod head if sentence start with "YES"
        flag=False

        if not self.CommonParameter.englishFlag:
            return flag

        tempSentence=sentence.lower()
        # Behaviour 5: Wave hand when saying "Yes, I can wave"

        if(tempSentence.find("yes, i can wave") == 0):
            self.giveWaveHand(sentence)
            flag=True
        # Behaviour 6: Smile when saying "Yes, I can smile"
        elif(tempSentence.find("yes, i can smile") == 0):
            self.giveSmile(sentence)
            flag=True

        elif self.checkGreeting(tempSentence):
            self.giveGreeting(sentence)
            flag=True

        elif self.checkBackSide(tempSentence):
            self.showBackSide(sentence)
            flag=True

        elif self.checkLeftSide(tempSentence):
            self.showLeftSide(sentence)
            flag=True

        elif self.checkRightSide(tempSentence):
            self.showRightSide(sentence)
            flag=True

        # elif (tempSentence.find("i can recognize people like you bernd, or smile or be angry or wave or laugh") == 0):
        #     self.client.client.speak("i can recognize people like you bernd",10)
        #     time.sleep(3)
        #     self.giveAllActions()
        #     flag=True



        elif(tempSentence.find("thank you bernd for this discussion") == 0):
            self.longWaitAndWave(sentence)
            flag=True

        elif tempSentence.find("yes, i can laugh") == 0:
            sentence='''yes, i can laugh <spurt audio=\"g0001_21\">ha ha ha ha</spurt>'''
            self.giveLaugh(sentence)
            flag=True

        elif (tempSentence.find("yes, i can be angry") == 0):
            self.giveAngry(sentence)
            flag=True

        return flag

    def giveAllActions(self):
        #"i can recognize people like you Bernd, or smile or be angry or wave or laugh"
        self.giveSmile("or smile",timeToWait=1)
        time.sleep(2)
        self.giveAngry("or be angry",timeToWait=1)
        time.sleep(5)
        self.giveWaveHand("or wave",timeToWait=1)
        #time.sleep(4)
        #self.giveLaugh("or laugh <spurt audio=\"g0001_21\">ha ha ha ha</spurt>",timeToWait=3)

    def giveGreeting(self,sentence,timeToWait=0.5):
        #print "Give Action: ",sentence
        print "Greeting!!!"
        # self.client.client.speak(sentence,10)
        # self.waitForSpeaking()
        # #time.sleep(timeToWait)
        #time.sleep(timeToWait)
        animList=["Receptionist_Greeting_HandRaised_NoSmile",
                  "Receptionist_Greeting_LoweredSteeple_NoSmile"]
        animation=self.randomChoose(animList)
        self.client.client.touchTarget(animation)
        time.sleep(timeToWait)
        self.waitForSpeaking()
        #self.client.client.speak(sentence,10)
        self.reply(sentence,False, True, False)
        #self.reply(sentence)

    def showBackSide(self,sentence,timeToWait=3):
        self.client.client.touchTarget("Receptionist_Direction_Front")
        time.sleep(timeToWait)
        self.waitForSpeaking()
        #self.client.client.speak(sentence,10)
        self.reply(sentence, False, True, False)

    def showLeftSide(self,sentence,timeToWait=3):
        self.client.client.touchTarget("Receptionist_Direction_Right")
        time.sleep(timeToWait)
        self.waitForSpeaking()
        #self.client.client.speak(sentence,10)
        self.reply(sentence, False, True, False)

    def showRightSide(self,sentence,timeToWait=3):
        self.client.client.touchTarget("Receptionist_Direction_Left")
        time.sleep(timeToWait)
        self.waitForSpeaking()
        #self.client.client.speak(sentence,10)
        self.reply(sentence, False, True, False)

    def checkBackSide(self,tempSentence):
        candidates=["on your back side"]
        return self.checkSentence(tempSentence,candidates)

    def checkLeftSide(self,tempSentence):
        candidates=["on your left side","on your left hand","go left"]
        return self.checkSentence(tempSentence,candidates)

    def checkRightSide(self,tempSentence):
        candidates=["on your right side","on your right hand","go right"]
        return self.checkSentence(tempSentence,candidates)


    def checkGreeting(self,tempSentence):
        #print "checkGreeting: ",tempSentence
        candidates=["i recognize you are","i can really feel your smile today",
                    "it's great to see you","how are you","nice to see you",
                    "nice to meet you","it's a pleasure to meet you",
                    "how are you doing","it's delightful to see you"]
        return self.checkSentence(tempSentence,candidates)

    def checkSentence(self,tempSentence,candidates):
        for sent in candidates:
            if tempSentence.find(sent)>-1:
                #print "match: ",sent
                return True
        return False

    def giveWaveHand(self,sentence,timeToWait=3):
        print "Give Action: ",sentence
        self.waitForSpeaking()
        #self.client.client.speak(sentence,10)
        self.reply(sentence, False, True, False)
        #self.waitForSpeaking()
        time.sleep(timeToWait)
        print "wave hand!!!"
        self.client.client.touchTarget("LOOKUP_Waving")

    def longWaitAndWave(self,sentence,timeToWait=6):
        print "Give Action: ",sentence
        self.waitForSpeaking()
        #self.client.client.speak(sentence,10)
        self.reply(sentence, False, True, False)
        #self.waitForSpeaking()
        time.sleep(timeToWait)
        print "wave hand!!!"
        self.client.client.touchTarget("LOOKUP_Waving")

    def giveSmile(self,sentence,timeToWait=2):
        print "Give Action: ",sentence
        self.waitForSpeaking()
        #self.client.client.speak(sentence,10)
        self.reply(sentence, False, True, False)
        #self.waitForSpeaking()
        time.sleep(timeToWait)
        self.client.client.touchTarget("smile")
        print "Facial Expression: Happy"

    def giveLaugh(self,sentence,timeToWait=3):
        print "Give Action: ",sentence
        self.waitForSpeaking()
        #self.client.client.speak(sentence,10)
        self.reply(sentence, False, True, False)
        #self.waitForSpeaking()
        time.sleep(timeToWait)
        self.client.client.touchTarget("happy")
        print "Facial Expression: Laugh"

    def giveAngry(self,sentence,timeToWait=2):
        print "Give Action: ",sentence
        self.waitForSpeaking()
        #self.client.client.speak(sentence,10)
        self.reply(sentence, False, True, False)
        #self.waitForSpeaking()
        time.sleep(timeToWait)
        self.client.client.touchTarget("shake")
        print "Facial Expression: Shake Head"

    def tempratureTransfer(self,sentence):
        tempSentence=sentence.lower()
        if "fahrenheit" in tempSentence:
            fahrTemp=re.search(r"\d+ fahrenheit",tempSentence).group()
            fahr=fahrTemp.split()[0]
            if fahr.isdigit():
                cent=int(round((int(fahr)-32)*(5.0/9.0)))
                centiTemp=str(cent)+" centigrade"
                tempSentence=re.sub(fahrTemp,centiTemp,tempSentence)
        return tempSentence

    def repeat(self):
        if self.lastSent!=None:
            print "Robot: "+self.lastSent
            self.waitForSpeaking()
            #self.client.client.speak("I said "+self.lastSent,10)
            self.reply("I said "+self.lastSent)

    def reply(self,sentence,animFlag=True,sentFlag=True,annoyFlag=True):

        while os.path.exists("process_mic_mute.txt"):
            try:
                os.remove("process_mic_mute.txt")
            except:
                continue
        emotion_report = True
        sentence=self.sent_proc.changeForSpeaking(sentence.lower())
        if "you look" in sentence:
            emotion_report = False

        exp,i=self.expIntensity()
        pleasureLevel=self.pleasureLevel()
        arousalLevel=self.arousalLevel()
        print "Current Pleasure Level is: "+pleasureLevel
        print "Current Arousal Level is: "+arousalLevel

        if annoyFlag:
            if pleasureLevel=="Crazy Angry":
                self.angryFlag=True
                sentence=self.randomChoose(AngryWord)
            elif self.angryFlag:
                sentence="Please be nice to me, "+sentence
                self.angryFlag=False

        sentence=self.replyUnknownIdentity(sentence)
        #sentence=self.tempratureTransfer(sentence)
        if sentence=="":
            sentence=self.randomChoose(OKWord)

        if animFlag: #and self.getAnimationFlag(arousalLevel):
            ### Default Animation
            animationFlag=self.defaultChatbotAnimation(sentence)
            if animationFlag:
                print "Robot: "+sentence
                return sentence
            ### automatic Animation
            if self._emotion.pos[0]>=0:
                AList=PositiveAnimation[pleasureLevel]
            else:
                AList=NegativeAnimation[pleasureLevel]
            a=self.randomChoose(AList)
            print "Animation: "+a
            if a != "":
                self.client.client.touchTarget(a)

        # speaking
        if self.CommonParameter.chineseFlag:
            s=sentence
        else:
            s=speechTone(sentence,pleasureLevel)
        if sentFlag:
            self.lastSent=s
        try:

            if os.path.exists("answer.mp3"):
                os.remove("answer.mp3")
            print(CommonParameter._language)
            if CommonParameter._language == "en-us":
                self.waitForSpeaking()
                if emotion_report:
                    self.client.client.speak(s, 10)
                    Audio_prop = AudioDuration("G:\\IMI-PROJECTS\\i2p_Nadine_Robot\\development\\i2p_interaction\\i2p_nadine_control\\build\\lipAnim.wav")
                    Audio_Dur = Audio_prop.len()
                    mic_control = open("mic_mute.txt","w")
                    mic_control.write(str(Audio_Dur))
                    mic_control.close()
            elif CommonParameter._language == "fr-fr":
                try:
                    translate_client = translate.Client()

                    # The text to translate
                    text = sentence
                    # The target language
                    target = 'fr'

                    # Translates some text into Russian
                    translation = translate_client.translate(
                        text,
                        target_language=target)

                    self.waitForSpeaking()

                    if emotion_report:
                        self.client.client.speak(str(translation['translatedText'].encode('utf-8')).replace("&#39;","'"), 30)
                        Audio_prop = AudioDuration("G:\\IMI-PROJECTS\\i2p_Nadine_Robot\\development\\i2p_interaction\\i2p_nadine_control\\build\\lipAnim.wav")
                        Audio_Dur = Audio_prop.len()
                        mic_control = open("mic_mute.txt", "w")
                        mic_control.write(str(Audio_Dur))
                        mic_control.close()
                except:
                    print "Unexpected error:", sys.exc_info()[0]
                    if emotion_report:
                        self.client.client.speak(s, 10)
                        Audio_prop = AudioDuration("G:\\IMI-PROJECTS\\i2p_Nadine_Robot\\development\\i2p_interaction\\i2p_nadine_control\\build\\lipAnim.wav")
                        Audio_Dur = Audio_prop.len()
                        mic_control = open("mic_mute.txt", "w")
                        mic_control.write(str(Audio_Dur))
                        mic_control.close()
            elif CommonParameter._language == "de-de":
                try:
                    translate_client = translate.Client()

                    # The text to translate
                    text = sentence
                    # The target language
                    target = 'de'

                    # Translates some text into Russian
                    translation = translate_client.translate(
                       text,
                       target_language=target)

                    self.waitForSpeaking()
                    #print
                    # _s=unicode(translation['translatedText'])
                    self.client.client.speak(str(translation['translatedText'].encode('utf-8')).replace("&#39;","'"), 20)
                    Audio_prop = AudioDuration("G:\\IMI-PROJECTS\\i2p_Nadine_Robot\\development\\i2p_interaction\\i2p_nadine_control\\build\\lipAnim.wav")
                    Audio_Dur = Audio_prop.len()
                    mic_control = open("mic_mute.txt", "w")
                    mic_control.write(str(Audio_Dur))
                    mic_control.close()
                except:
                    print "Unexpected error:", sys.exc_info()[0]
                    self.client.client.speak(s, 10)
                    Audio_prop = AudioDuration("G:\\IMI-PROJECTS\\i2p_Nadine_Robot\\development\\i2p_interaction\\i2p_nadine_control\\build\\lipAnim.wav")
                    Audio_Dur = Audio_prop.len()
                    mic_control = open("mic_mute.txt", "w")
                    mic_control.write(str(Audio_Dur))
                    mic_control.close()

            elif CommonParameter._language == "ja-jp":

                translate_client = translate.Client()

                # The text to translate
                text = sentence
                # The target language
                target = 'ja'

                # Translates some text into Russian
                translation = translate_client.translate(
                    text,
                    target_language=target)
                tts = gTTS(text=translation['translatedText'], lang='ja')
                tts.save("answer.mp3")
                self.waitForSpeaking()
                Audio_prop = AudioDuration("answer.mp3")
                Audio_Dur = Audio_prop.len()
                mic_control = open("mic_mute.txt", "w")
                mic_control.write(str(Audio_Dur))
                mic_control.close()
                self.client.client.speak(s, 40)
                os.system("G:\IMI-PROJECTS\i2p_Nadine_Robot\development\i2p_perception\i2p_speech_recognition\mpg123.exe answer.mp3")

            elif CommonParameter._language == "hi-in":

                translate_client = translate.Client()

                # The text to translate
                text = sentence
                # The target language
                target = 'hi'

                # Translates some text into Russian
                translation = translate_client.translate(
                    text,
                    target_language=target)

                # print(u'Text: {}'.format(text))
                # print(chr(text).encode("UTF-8"))
                # print(u'Translation: {}'.format(translation['translatedText']))
                tts = gTTS(text=translation['translatedText'], lang='hi')
                tts.save("answer.mp3")
                self.waitForSpeaking()
                Audio_prop = AudioDuration("answer.mp3")
                Audio_Dur = Audio_prop.len()
                mic_control = open("mic_mute.txt", "w")
                mic_control.write(str(Audio_Dur))
                mic_control.close()
                self.client.client.speak(s, 40)
                os.system("G:\IMI-PROJECTS\i2p_Nadine_Robot\development\i2p_perception\i2p_speech_recognition\mpg123.exe answer.mp3")

            elif CommonParameter._language == "cmn-hans-cn": #zh-yue
                translate_client = translate.Client()

                # The text to translate
                text = sentence
                # The target language
                target = 'zh-CN'

                # Translates some text into Russian
                translation = translate_client.translate(
                    text,
                    target_language=target)

                # print(u'Text: {}'.format(text))
                # print(chr(text).encode("UTF-8"))
                # print(u'Translation: {}'.format(translation['translatedText']))
                tts = gTTS(text=translation['translatedText'], lang='zh-cn')
                #tts.save("answer.mp3")
                #mixer.init()
                #s = s + " ##"
                tts.save("answer.mp3")
                self.waitForSpeaking()
                Audio_prop = AudioDuration("answer.mp3")
                Audio_Dur = Audio_prop.len()
                mic_control = open("mic_mute.txt", "w")
                mic_control.write(str(Audio_Dur))
                mic_control.close()
                self.client.client.speak(s, 40)
                os.system("G:\IMI-PROJECTS\i2p_Nadine_Robot\development\i2p_perception\i2p_speech_recognition\mpg123.exe answer.mp3")
                #self.client.client.speak(s, 40)
                #_s=unicode(translation['translatedText'],"utf-8")
                #self.zh_TTS.speak(translation['translatedText'])
                #with open("answer.mp3") as f:
                #    m = mmap.mmap(f.fileno(), 0, access=mmap.ACCESS_READ)
                #    mixer.music.load(m)
                #    mixer.music.play()

                #    while mixer.music.get_busy():
                #       time.sleep(0.1)
                #    else:
                #        m.close()
            elif CommonParameter._language == "yue-hant-hk": #zh-yue
                #self.client.client.speak(s, 10)
                translate_client = translate.Client()

                # The text to translate
                text = sentence
                # The target language
                target = 'zh-TW'

                # Translates some text into Russian
                translation = translate_client.translate(
                    text,
                    target_language=target)

                # print(u'Text: {}'.format(text))
                # print(chr(text).encode("UTF-8"))
                # print(u'Translation: {}'.format(translation['translatedText']))
                tts = gTTS(text=translation['translatedText'], lang='zh-yue')
                tts.save("answer.mp3")
                self.waitForSpeaking()
                self.client.client.speak(s, 40)
                mixer.init()
                #s = s + " ##"

                with open("answer.mp3") as f:
                    m = mmap.mmap(f.fileno(), 0, access=mmap.ACCESS_READ)
                    mixer.music.load(m)
                    mixer.music.play()

                    while mixer.music.get_busy():
                        time.sleep(0.1)
                    else:
                        m.close()

                Audio_prop = AudioDuration("answer.mp3")
                Audio_Dur = Audio_prop.len()
                mic_control = open("mic_mute.txt", "w")
                mic_control.write(str(Audio_Dur))
                mic_control.close()

                ###korean added by nidhi
                """
                elif CommonParameter._language == "ko-KR" or CommonParameter._language == "ko-kr":

                    translate_client = translate.Client()
                    text = sentence
                    target = 'ko'
                    translation = translate_client.translate(
                        text,
                        target_language=target)

                    # tts = gTTS(text=translation['translatedText'], lang='ko')
                    # tts.save("answer.mp3")
                    # self.waitForSpeaking()
                    # Audio_prop = AudioDuration("answer.mp3")
                    # Audio_Dur = Audio_prop.len()
                    # mic_control = open("mic_mute.txt", "w")
                    # mic_control.write(str(Audio_Dur))
                    # mic_control.close()
                    # self.client.client.speak(s, 40)
                    # os.system("G:\IMI-PROJECTS\i2p_Nadine_Robot\development\i2p_perception\i2p_speech_recognition\mpg123.exe answer.mp3")


                    # Instantiates a client
                    client = texttospeech.TextToSpeechClient()

                    # Set the text input to be synthesized
                    synthesis_input = texttospeech.types.SynthesisInput(text=translation['translatedText'])

                    # Build the voice request, select the language code ("en-US") and the ssml
                    # voice gender ("neutral")
                    voice = texttospeech.types.VoiceSelectionParams(
                        language_code='ko-KR',
                        # voice_name= 'ko-KR-Standard-B',
                        ssml_gender=texttospeech.enums.SsmlVoiceGender.FEMALE)

                    # Select the type of audio file you want returned
                    audio_config = texttospeech.types.AudioConfig(
                        audio_encoding=texttospeech.enums.AudioEncoding.MP3)

                    # Perform the text-to-speech request on the text input with the selected
                    # voice parameters and audio file type
                    response = client.synthesize_speech(synthesis_input, voice, audio_config)

                    # The response's audio_content is binary.
                    with open('answer.mp3', 'wb') as out:
                        # Write the response to the output file.
                        out.write(response.audio_content)
                        print('Audio content written to file "answer.mp3"')

                    self.waitForSpeaking()
                    print "here1"
                    Audio_prop = AudioDuration("answer.mp3")
                    print "here2"
                    Audio_Dur = Audio_prop.len()
                    print "here3"
                    mic_control = open("mic_mute.txt", "w")
                    print "here4"
                    mic_control.write(str(Audio_Dur))
                    print "here5"
                    mic_control.close()
                    print "here6"
                    self.client.client.speak(s, 40)
                    print "here7"
                    os.system("G:\IMI-PROJECTS\i2p_Nadine_Robot\development\i2p_perception\i2p_speech_recognition\mpg123.exe answer.mp3")
                    print "here8"

                ### end of korean language here
                """
            # if self.CommonParameter.germanFlag:
            #     self.volume_control.setVolume(vol="German") #30%
            #     print "&&&&&&&&&&&&&&&&&&&&&&"
            #     print "Speak German"
            #     print "&&&&&&&&&&&&&&&&&&&&&&"
            #     self.waitForSpeaking()
            #     self.client.client.speak(s,20)
            # elif self.CommonParameter.frenchFlag:
            #     print "&&&&&&&&&&&&&&&&&&&&&&"
            #     print "Speak French"
            #     print "&&&&&&&&&&&&&&&&&&&&&&"
            #     self.volume_control.setVolume(vol="French") #30%
            #     #eng_blob = TextBlob(s)
            #     #print eng_blob, blob
            #     #_s = eng_blob.translate(from_lang="en", to='fr')
            #     _s=self.translator.translation(text=s,targetLanguage="fr",freeFlag=True)
            #     print "translated: " + str(_s)
            #     self.waitForSpeaking()
            #     self.client.client.speak(str(_s),30)
            # elif self.CommonParameter.chineseFlag:
            #     print "&&&&&&&&&&&&&&&&&&&&&&"
            #     print "Speak Chinese"
            #     print "&&&&&&&&&&&&&&&&&&&&&&"
            #     self.volume_control.setVolume(vol="Chinese") #51%
            #     #eng_blob = TextBlob(s)
            #     #print eng_blob, blob
            #     #_s = eng_blob.translate(from_lang="en", to='fr')
            #     _s=self.translator.translation(text=s,targetLanguage="zh",freeFlag=True)
            #     #print "translated: ",_s.encode('utf-8')
            #     print "Translated: %s" %_s
            #     self.waitForSpeaking()
            #     self.client.client.speak(s,40)
            #     #time.sleep(0.5)
            #     _s=unicode(_s,"utf-8")
            #     self.zh_TTS.speak(_s)
            # else:  #speak English
            #     self.volume_control.setVolume(vol="English") #30%
            #     self.waitForSpeaking()
            #     self.client.client.speak(s,10)
        except Exception as error:
                #print sys.exc_info()
            print('caught this error: ' + repr(error))
            print "Error happens when speak ",s


        print "Robot: "+s
        s = s.replace("Ae I A", "AIA")
        with open("C:\\xampp\\htdocs\\Reader\\nadine_app.txt", "a") as myfile:
            myfile.write(str(datetime.now().strftime("%a, %d %B %Y %I:%M:%S")) + " ### Nadine**" + s + "\n")

        # bigquery_client = bigquery.Client()
        # dataset = bigquery_client.dataset('IMI_NTU')
        # table = dataset.table('memory')
        # # data = json.loads(json_data)
        # db_string='["Nadine","'+CommonParameter._userName+'","gender","role","'+CommonParameter._userInput+'","'+sentence+'","'+str(datetime.now().time())+'","'+str(datetime.now().date())+'","'+CommonParameter._language+'"]'
        # data = json.loads(db_string)#'["abcd","yasir","male","senior research engineer","how are you","i am good","4 22","15 9"]'
        # # Reload the table to get the schema.
        # table.reload()
        #
        # rows = [data]
        # errors = table.insert_data(rows)
        #
        # if not errors:
        #     print('Loaded 1 row into {}:{}'.format('IMI_NTU', 'memory'))
        # else:
        #     print('Errors:')

        if animFlag and self.getSmileFlag():
            self.waitForSpeaking()
            print "Give a smile!!!"
            self.client.client.touchTarget("smile")
        return sentence

    def replyUnknownIdentity(self,sentence):
        # Behaviour 5: Wave hand when saying "Yes, I can wave"
        if(sentence in ["friend","Friend"]):
            replies=["I need more time to recognize you","I am not sure"]
            sentence=self.randomChoose(replies)
        return sentence

    def waitForSpeaking(self):
        #time.sleep(0.5)
        speakFlag=False
        if CommonParameter.speaking:
            speakFlag=True
        while CommonParameter.speaking:
            time.sleep(0.1)
        if speakFlag:
            time.sleep(1)
            print "sleep for a while"

    def getSmileFlag(self):
        if self._mood.pos[0]>=-0.1:
            if self._mood.pos[0]<0.4:
                threshold=0.3
            elif self._mood.pos[0]<0.7:
                threshold=0.5
            else:
                threshold=0.7
            if random.random()<threshold:
                return True
        return False

        





def initTextBlob():
    sent=TextBlob("went")
    tags=sent.tags
    # nltk.word_tokenize("hello")
    # nltk.pos_tag("hello")
    for (w,t) in tags:
        _w=Word(w,t)
        res=_w.lemma



