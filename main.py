__author__ = 'IMI-Demo'
import os
import sys
import math
import random
import time
import threading
import os.path
#sys.path.append("../")
sys.path.append("../../i2p/i2pThrift/gen-py")
sys.path.append("../../i2p/i2pThrift/tools/py")
sys.path.append("New_Functionality")
import Definition
import time
import config
import cPickle as pickle
import nltk
import re
from predefinedSentence import *

from copy import copy

import Inputs.ChatbotService as Chat_Service
import Inputs.EMNadineService as EMNadine_Service
import Inputs.StanfordNLPService as NLP_Service
import Inputs.EmotionEngineService as Emotion_Service
import Inputs.SpeechRecognitionService as SR_Service
import Inputs.HandInputService as HI_Service
import Inputs.QuepyService as QA_Service
import Inputs.SpellCheckService as SpellCheck_Service
import Inputs.SpeakerIdentification as Speaker_Service
import Inputs.ChildRobotService as ChildBot_Service
import Inputs.FaceEmotionService as FaceEmotion_Service
from Inputs.ttypes import *
import Inputs.constants

import Control.AgentControl as AgentControl_Service
import Control.constants
import Control.ttypes

import VHSimpleService.VHSimpleService as VH_Service
import VHSimpleService.constants
import VHSimpleService.ttypes
import shutil
#----------------------------------------------------
# Added Dialogue Service - Lijune 7 Sep 2015
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
from news_online import OnlineNews
from e_mail import Email
from chatterbot import ChatBot

from DialogueManager import *
from InteractionBT import *
from LearnQA import *


###changes by nidhi for face recognition
import datetime
from datetime import date
import mysql.connector
try:
    conn = mysql.connector.connect( user='root',
                                password='',
                                host='127.0.0.1',
                                database='nadine'
                                )
except:
    print("Error: could not connect with SQL server")

###changes over for face recognition

class Main:
    def __init__(self):
        self.checkDebug()
        self.checkBecassine()
        self.checkMemory()
        self.checkRecognition()
        self.checkQuestion()
        self.checkActive()
        self.startThirft()
        self.initVariables()
        self.setBTree()

    def setBTree(self):
        self.bt = myBT()
        self.bt.buildFromFile('InteractionBT.json')
        self.bt.setMain(self)
        self.bt.execute()

    def checkDebug(self):
        self.debug=False
        if len(sys.argv)>1:
            for arg in sys.argv[1:]:
                if arg in ["Debug","debug","D","d"]:
                    self.debug=True
                    break

    def checkBecassine(self):
        self.becassineFlag=False
        if len(sys.argv)>1:
            for arg in sys.argv[1:]:
                if arg in ["Becassine","becassine","Child","child"]:
                    self.becassineFlag=True
                    break

    def checkMemory(self):
        self.memoryFlag=True
        if len(sys.argv)>1:
            for arg in sys.argv[1:]:
                if arg in ["nomem","NoMem"]:
                    self.memoryFlag=False
                    break

    def checkQuestion(self):
        self.AskQuestionFlag=False
        if len(sys.argv)>1:
            for arg in sys.argv[1:]:
                if arg in ["AskQues","AskQuestion"]:
                    self.AskQuestionFlag=True
                    break

    def checkRecognition(self):
        CommonParameter.recongizeFlag=True
        if len(sys.argv)>1:
            for arg in sys.argv[1:]:
                if arg in ["norecog","NoRecog"]:
                    CommonParameter.recongizeFlag=False
                    break

    def checkActive(self): # if active, speak something to break silence
        self.activeFlag=False
        if len(sys.argv)>1:
            for arg in sys.argv[1:]:
                if arg in ["active","Active"]:
                    self.activeFlag=True
                    break



    def startThirft(self):
        import socket

        IP = socket.gethostbyname(socket.gethostname())
        print IP

        ip_address=IP
        robot_address=IP

        self.chatbot_client = ThriftTools.ThriftClient(ip_address,Inputs.constants.DEFAULT_CHATBOT_PORT,Chat_Service,'ChatBot')
        while not self.chatbot_client.connected:
            self.chatbot_client.connect()
        self.chatbot=ChatbotWrapper.chatbot(self.chatbot_client)



        #################################################
        ##############  IF NOT ChildRobot ###############
        #################################################
        if not self.becassineFlag:
            ##starting speech service
            ##starting feedback service
            feedback_handler = FeedbackHandler()
            feedback_server = ThriftTools.ThriftServerThread(Feedback.constants.DEFAULT_AGENT_FEEDBACK_SERVICE_PORT,Feedback_Service,feedback_handler,'Agent Feedback Service',ip_address)
            feedback_server.start()
            #print "feedback server started..."

            speech_handler = SpeechHandler()
            speech_server = ThriftTools.ThriftServerThread(1200,SR_Service,speech_handler,'Speech Recognition Service',ip_address)
            speech_server.start()
            #print "speech server started..."

            face_emotion_handler = FaceEmotionHandler()
            face_emotion_server = ThriftTools.ThriftServerThread(Inputs.constants.DEFAULT_FACE_EMOTION_SERVICE_PORT,FaceEmotion_Service,face_emotion_handler,'Face Emotion Service',"localhost")
            face_emotion_server.start()

            ##starting speech service
            handinput_handler = HandInputHandler()
            handinput_server = ThriftTools.ThriftServerThread(Inputs.constants.DEFAULT_HANDINPUT_PORT,HI_Service,handinput_handler,'Hand Input Service',ip_address)
            handinput_server.start()
            #print "hand input server started..."


            ## starting emotion service
            emotion_handler = EmotionHandler()
            emotion_server = ThriftTools.ThriftServerThread(Inputs.constants.DEFAULT_EMOTIONENGINE_SERVICE_PORT,Emotion_Service,emotion_handler,'Emotion Engine Service','localhost')
            emotion_server.start()

            #----------------------------------------------------
            # Added Dialogue Service - Lijun 7 Sep 2015
            #----------------------------------------------------
            ## Starting Dialogue Manager service
            dialogueManager_handler = DialogueManagerHandler()
            dialogueManager_server = ThriftTools.ThriftServerThread(Inputs.constants.DEFAULT_DIALOGUE_MANAGER_PORT, Dialogue_Service, dialogueManager_handler, 'Dialogue Service', "localhost")
            #dialogueManager_server = ThriftTools.ThriftServerThread(Inputs.constants.DEFAULT_DIALOGUE_MANAGER_PORT, Dialogue_Service, dialogueManager_handler, 'Dialogue Service', ip_address)
            dialogueManager_server.start()
            #print "Dialogue server started..."
            #----------------------------------------------------


            if self.memoryFlag:
                self.emNadine_client = ThriftTools.ThriftClient(ip_address,Inputs.constants.DEFAULT_EMNADINE_PORT,EMNadine_Service,'EpisodicMemory')
                while not self.emNadine_client.connected:
                    self.emNadine_client.connect()
            else:
                self.emNadine_client=None


            speakerIdentification_handler=SpeakerIdentificationHandler()
            speakerIdentification_server=ThriftTools.ThriftServerThread(Inputs.constants.DEFAULT_SPEAKERIDENTIFICATION_PORT, Speaker_Service, speakerIdentification_handler, "Speaker Identification Service",ip_address)
            speakerIdentification_server.start()
            #print "Speaker Identification Server Started...

            ## connect virtual human
            time.sleep(4)
            robot_address="localhost"
            self.vh_client = ThriftTools.ThriftClient(robot_address,9090,AgentControl_Service,'SmartBody')
            # if not self.debug:
            #     self.vh_client = ThriftTools.ThriftClient(robot_address,9090,AgentControl_Service,'SmartBody')
            # else:
            #     self.vh_client = ThriftTools.ThriftClient(ip_address,9090,VH_Service,'SmartBody_Debug')
            while not self.vh_client.connected:
                self.vh_client.connect()
        else:
            ## starting child robot service
            childRobot_handler = ChildBotHandler()
            childRobot_server = ThriftTools.ThriftServerThread(Inputs.constants.DEFAULT_CHILDROBOT_SERVICE_PORT,ChildBot_Service,childRobot_handler,'Becassine Service',ip_address)
            childRobot_server.start()
            self.vh_client=None
            self.emNadine_client=None


    def initVariables(self):
        self.Dialogue=DialogueManager(self.vh_client)
        self.Dialogue.setCommonParameter(CommonParameter)

        print "load emotion recognition"
        self.EmoRecognition=SearchConcepts.SearchConcepts()

        print "initalize TextBlob"
        initTextBlob()
        self.rdmFunc=randomFunc()

        self.firstRound=True
        self.QA=None
        self.Predefine=PredefinedSentence()

        # self.Email=Email()
        # self.Email.setMain(self)
        # self.Email.setCommonParameter(CommonParameter)

        ### For Nadia chatobot
        self.Nadiachatbot = ChatBot(
            'Nadia bot',
            read_only=True,
            logic_adapters=[
                {
                    'import_path': 'chatterbot.logic.BestMatch',
                    "statement_comparison_function": "chatterbot.comparisons.levenshtein_distance",
                },
                # {
                #     'import_path': 'chatterbot.logic.TimeLogicAdapter'
                # },
                {
                    'import_path': 'chatterbot.logic.MathematicalEvaluation'
                },
                {
                    'import_path': 'chatterbot.logic.LowConfidenceAdapter',
                    'threshold': 0.60,
                    'default_response': 'I am sorry, but I do not understand.'
                }
            ],
            trainer='chatterbot.trainers.ChatterBotCorpusTrainer'
          )
        # Train based on Nadia
        # chatbot.train("G:\IMI-PROJECTS\i2p_Nadine_Robot\development\i2p_interaction\i2p_dialog_manager\chatterbotMemory\Nadia.yml")
        ###


        ###FOR AIA CHATBOT###
        """
        self.AIAchatbot = ChatBot('DIP',
			storage_adapter='chatterbot.storage.SQLStorageAdapter',
			logic_adapters=[
				{
					'import_path': 'chatterbot.logic.BestMatch'
				},
				{
					'import_path': 'chatterbot.logic.LowConfidenceAdapter',
					'threshold': 4.50,
					'default_response': 'I am sorry, but I do not understand.'
				}
			], #create the chatbot      
			trainer='chatterbot.trainers.ListTrainer'
		) """

        # Train based on the english corpus
        #Uncomment the training the part whenever changes are made to English corpus
        # self.AIAchatbot.train("chatterbot.corpus.english")

        # Train based on the AIA vitality corpus
        # Uncomment the training the part whenever changes are made to AIA vitality corpus
        # self.AIAchatbot.train("chatterbot.corpus.AIA.Vitality")

        # Train based on the AIA payments corpus
        # Uncomment the training the part whenever changes are made to AIA payments corpus
        # self.AIAchatbot.train("chatterbot.corpus.AIA.payments")

        # Train based on the AIA general_questions corpus
        # Uncomment the training the part whenever changes are made to AIA general_questions corpus
        # self.AIAchatbot.train("chatterbot.corpus.AIA.general_questions")

        # Train based on the AIA Policy_Specific_Questions corpus
        # Uncomment the training the part whenever changes are made to AIA Policy_Specific_Questions corpus
        # self.AIAchatbot.train("chatterbot.corpus.AIA.Policy_Specific_Questions")

        # Train based on the AIA Transactional_Questions corpus
        # Uncomment the training the part whenever changes are made to AIA Transactional_Questions corpus
        # self.AIAchatbot.train("chatterbot.corpus.AIA.Transactional_Questions")

        # Train based on the AIA long answer corpus
        # Uncomment the training the part whenever changes are made to AIA Transactional_Questions corpus
        # self.AIAchatbot.train("chatterbot.corpus.AIA.longans")
        ###FOR AIA CHATBOT###

        # send a single to Robot
        if not self.becassineFlag:
            self.vh_client.client.touchTarget("LOOKUP_Default_idle")
            #self.vh_client.client.touchTarget("Nadine_Arm_Rest_in_Thigh")
        print "waiting for the user identity..."

    def setParameters(self):
        '''Set Parameter at the very beginning of every interaction'''

        # set QA and chatbot
        self.userQ=userQuestion(CommonParameter._userName)
        if self.firstRound:
            self.learnQA=LearnQA() # learn knowledge and write AIML file
            self.QA=QuestionAnswering(self.emNadine_client,CommonParameter._userName)
            self.firstRound=False
        else:
            self.QA.reset(CommonParameter._userName)

        if CommonParameter._userName!="Unknown":
            self.chatbot.reply("user="+CommonParameter._userName)
        else:
            self.chatbot.reply("user=Friend")

        # set parameters
        self.num_iter=0
        #self.ask_iter=0
        self.question=None
        self.start_interaction=False
        self.end_session=False
        CommonParameter._userInput=''

        # for unknown user, ask several question
        self.numberQuestion=4
        #self.quesRequired=False
        self.newFlag=False
        if self.AskQuestionFlag:
            self.newFlag=not self.QA.isKnownUsers(self.QA.user)
            if self.QA.user=="Unknown":
                self.newFlag=False
            if self.newFlag:
                ### By James
                #sent="Nice to meet you "+self.QA.user
                #self.respond(sent)
                #self.quesRequired=True
                pass
        if not self.becassineFlag:
            # wave hands
            if self.rdmFunc.randProb(0.4):
                words=["hello","hi"]
                hello=self.rdmFunc.randomChoose(words)
                #self.respond(hello,animFlag=False)
                print "Robot: Hello"
                self.wait()
                if self.rdmFunc.randProb(0.5):
                    self.vh_client.client.touchTarget("LOOKUP_Waving")
            else:
                self.vh_client.client.touchTarget("LOOKUP_Waving")
            print "Find a user"
            CommonParameter.faceEmoPool.reset(True)
            # else:
            #     self.vh_client.client.touchTarget("happy")

        ###For AIA Chat###
        #words = ["Welcome to Ae I A, How can I help you", "Welcome to Ae I A, May I help you"]
        #hello = self.rdmFunc.randomChoose(words)
        #self.vh_client.client.speak(hello, 10)
        ###For AIA Chat###
        print "start working..."




    def checkUser(self):
        if self.becassineFlag:
            CommonParameter._userName="Unknown"
        if self.debug:
            print "Before we start, please input your name: "
            CommonParameter._userName = raw_input('--> ').capitalize()
        #print "waiting for the user identity..."
        if CommonParameter._userName=="":
            time.sleep(0.1)
            return True
        return False

    def wait(self):
        self.Dialogue.waitForSpeaking()

    def checkFaceEmotion(self):
        #mProbability=0.5
        if CommonParameter._userName!="" and CommonParameter._userInput=="" and CommonParameter.faceEmoPool.hasNew:
            CommonParameter.faceEmoPool.hasNew=False
            print "Report Probability is %.2f" % CommonParameter.faceEmoPool.reportProb
            if self.rdmFunc.randProb(CommonParameter.faceEmoPool.reportProb):
                curMoodPleasure=self.Dialogue._mood.pos[0]
                m_emotions,m_responses=CommonParameter.faceEmoPool.getEmotionalSentences(self.start_interaction,curMoodPleasure)
                if len(m_responses)>0:
                    if m_emotions!="":
                        m_emo_intensity=self.rdmFunc.randDouble(0.3) #  a number between 0 and 0.3
                        CommonParameter.recogEmo=m_emotions+" "+str(m_emo_intensity)
                    sent=self.rdmFunc.randomChoose(m_responses)
                    CommonParameter.speakingForFace=True
                    self.respond(sent,annoyFlag=False)
                    return True
        return False


    def updateUser(self):
        #CommonParameter._userInput = "Can you show me pictures of imi"
        #self.analyzeInput()

        if self.becassineFlag:
            return
        #if CommonParameter._face_rec_thread_started==False:
        #    t = threading.Thread(target=self.beginning_face_Rec(),args=())  # manoj
        #    t.start()
        #    CommonParameter._face_rec_thread_started=True
        #if CommonParameter._face_rec_name!='' and CommonParameter._userName!=CommonParameter._face_rec_name:
        #    self.vh_client.client.speak("Hello "+CommonParameter._face_rec_name, 10)
        #    CommonParameter._userName=CommonParameter._face_rec_name
            #CommonParameter._face_rec_name=''
        #if os.path.exists("G:\\IMI-PROJECTS\\x64\\output_name.txt"):
        if os.path.exists(os.path.join(config.FACE_RECOGNITION_FOLDER, "output_name.txt")):
            f=open("G:\\IMI-PROJECTS\\x64\\output_name.txt","r+")
            f = open(os.path.join(config.FACE_RECOGNITION_FOLDER, "output_name.txt"), "r+")
            CommonParameter._face_rec_name=f.read()
            f.close()
        #if os.path.exists("G:\\IMI-PROJECTS\\x64\\Release\\output_name.txt"):
        #    f=open("G:\\IMI-PROJECTS\\x64\\Release\\output_name.txt","r+")
        #    CommonParameter._face_rec_name=f.read()
        #    f.close()
            #os.remove("G:\\IMI-PROJECTS\\x64\\Release\\output_name.txt")

        #if os.path.exists("G:\\IMI-PROJECTS\\i2p_Nadine_Robot\\development\\Register_staff.txt"):
        if os.path.exists(os.path.join(config.DEVELOPMENT_FOLDER, "Register_staff.txt")):

            #self.vh_client.client.speak("please place the card in front of the camera", 10)
            self.Dialogue.reply("please place the card in front of the camera",True, True, False)
            read_type = 1
            Read_Sentence, Name = self.QA.sent_proc.Read_from_Image(read_type)
            if Name != 'Unknown':
                CommonParameter._userName = Name
            #self.vh_client.client.speak(Read_Sentence,10)
            self.Dialogue.reply(Read_Sentence, True, True, False)

            #os.remove("G:\\IMI-PROJECTS\\i2p_Nadine_Robot\\development\\Register_staff.txt")
            os.remove(os.path.join(config.DEVELOPMENT_FOLDER, "Register_staff.txt"))

        #if os.path.exists("G:\\IMI-PROJECTS\\i2p_Nadine_Robot\\development\\Register_visitor.txt"):
        if os.path.exists(os.path.join(config.DEVELOPMENT_FOLDER, "Register_visitor.txt")):

            #self.vh_client.client.speak("please place the IC in front of the camera", 10)
            self.Dialogue.reply("please place the IC in front of the camera", True, True, False)
            read_type = 3
            Read_Sentence, Name = self.QA.sent_proc.Read_from_Image(read_type)
            if Name != 'Unknown':
                CommonParameter._userName = Name
            #self.vh_client.client.speak(Read_Sentence,10)
            self.Dialogue.reply(Read_Sentence, True, True, False)

            #os.remove("G:\\IMI-PROJECTS\\i2p_Nadine_Robot\\development\\Register_visitor.txt")
            os.remove(os.path.join(config.DEVELOPMENT_FOLDER, "Register_visitor.txt"))

        #if os.path.exists("G:\\IMI-PROJECTS\\i2p_Nadine_Robot\\development\\deliver.txt"):
        if os.path.exists(os.path.join(config.DEVELOPMENT_FOLDER, "deliver.txt")):

            #self.vh_client.client.speak("please place the parcel in front of the camera", 10)
            self.Dialogue.reply("please place the parcel in front of the camera", True, True, False)
            read_type = 2
            Read_Sentence, dummy = self.QA.sent_proc.Read_from_Image(read_type)
            #self.vh_client.client.speak(Read_Sentence,10)
            self.Dialogue.reply(Read_Sentence, True, True, False)

            #os.remove("G:\\IMI-PROJECTS\\i2p_Nadine_Robot\\development\\deliver.txt")
            os.remove(os.path.join(config.DEVELOPMENT_FOLDER, "deliver.txt"))

        if self.QA.user!=CommonParameter._userName:
            if CommonParameter._userName=="":
                print "End this interaction!!!"
                self.end_session=True
            elif CommonParameter._userName not in ["","Unknown"]:
                if self.memoryFlag:
                    self.QA.storeEvent(True)
                self.setParameters()
                self.reportRecognition()


    def reportRecognition(self):
        if CommonParameter.germanFlag:
            sentence="Ich glaube sie heissen "+CommonParameter._userName
        else:
            sentence="Hello "+CommonParameter._userName
            print("user:" + CommonParameter._userName)
            if "Nadia" in CommonParameter._userName:
                sentence = "Hello Professor Nadia"
            greeting=self.QA.getGreeting()
            ######## By James
            if greeting:
                if greeting!="again":
                    sentence=sentence+". "+greeting
                else:
                    sentence=sentence+" "+greeting
            if self.AskQuestionFlag and self.newFlag:
                sentence=sentence+". You are new to me. Nice to meet you."

        self.Dialogue.reply(sentence,animFlag=False)

    def checkEnd(self):
        ########## End the session#######
        if self.becassineFlag:
            return True
        if self.debug:
            endFlag=self.start_interaction and CommonParameter._userInput in ["goodbye","bye","see you next time",\
                                                                 "see you","bye bye"]
        else:
            endFlag=False

        if self.end_session or endFlag:
            # say good bye
            if not self.end_session:
                self.vh_client.client.touchTarget("LOOKUP_Waving")
                self.Dialogue.reply("Ok, see you next time",False)
            # save data
            if self.start_interaction:
                self.learnQA.saveQA()
                if self.memoryFlag:
                    self.QA.storeEvent(True)
                if self.QA.user!="Unknown":
                    self.chatbot_client.client.chatbot("save the memory")
                    self.userQ.saveAskedIndex()
            CommonParameter._userInput=""
            CommonParameter._lastUserInput=""
            CommonParameter._userName=""
            print "Save OK"
            return False
        return True

        ##########################################################

    def hasNoInput(self):
        if CommonParameter._userInput !="":
            if CommonParameter._userInput in ["none","NONE"]: # unclear input, ask to repeat
                # if self.rdmFunc.randProb(0.3):
                #     sentence=self.rdmFunc.randomChoose(["I beg you pardon?","Could you speak slower and loader?",\
                #                                         "Could you repeat?","Could you speak again?"])
                #     self.respond(sentence,animFlag=False)
                #     print "Robot: "+sentence
                CommonParameter._userInput=""
            else:
                print "User Input: "+CommonParameter._userInput
                CommonParameter.faceEmoPool.reset() # Once there is new speech input, reset faceEmotion to accept new states.
                return False
        else:
            if self.activeFlag and CommonParameter.silenceCheck.getSilence():
                sentence=self.rdmFunc.randomChoose(["How are you?","Shall we talk something",\
                                                    "Do you want to talk?"])
                #self.vh_client.client.speak(sentence,10)
                self.respond(sentence,animFlag=False)
                animation=self.rdmFunc.randomChoose(["Speaking_LHandRaised",
                                "Speaking_LoweredSteeple",
                                "Speaking_RaisedSteeple",
                                "Speaking_RHandRaised"])
                time.sleep(1)
                self.vh_client.client.touchTarget(animation)
                print "Robot: "+sentence
                CommonParameter.silenceCheck.reported=True

        return True

    def respond(self,sentence,animFlag=True,sentFlag=True,annoyFlag=True):
        if self.becassineFlag:
            CommonParameter.response=sentence
            self.becassinelastSent=sentence
        else:
            self.wait()
            print "Send Dialog to Speak!!!"
            if CommonParameter._already_answered==False:
                self.Dialogue.reply(sentence,animFlag,sentFlag,annoyFlag=annoyFlag)

    def learnKnowledge(self):
        flag=self.learnQA.getAnswer(CommonParameter._userInput)
        if flag and CommonParameter._lastUserInput!="":
            self.learnQA.updateQA(CommonParameter._lastUserInput)
            sents=["Thank you, I will check it and update my database soon.",\
                   "Thank you for teaching me, I will update it later" ]
            sent=self.rdmFunc.randomChoose(sents)
            self.respond(sent,animFlag=False)
            animation=self.rdmFunc.randomChoose(["Speaking_LHandRaised",
                                "Speaking_LoweredSteeple",
                                "Speaking_RaisedSteeple",
                                "Speaking_RHandRaised"])
            #time.sleep(3)
            self.wait()
            self.vh_client.client.touchTarget(animation)
            print "Robot: ",sent
            CommonParameter._userInput=""
            return True
        return False


    # def pardon(self):
    #     if CommonParameter._userInput in ["NONE","none"]:
    #         if self.rdmFunc.randProb(0.2):
    #             sent=self.rdmFunc.randomChoose(ConfusionWord)
    #             self.respond(sent,sentFlag=False)
    #         CommonParameter._userInput=""
    #         return True
    #     return False

    def checkNumPeople(self):
        if "how many people" in CommonParameter._userInput:
            print "Report User: ",CommonParameter.numberUsers
            sent="You are the number "+str(CommonParameter.numberUsers)+" people I have ever met"
            #self.vh_client.client.speak(sent,10)
            self.respond(sent,animFlag=False)
            CommonParameter._userInput=""
            return True
        return False



    def shutup(self):
        if self.becassineFlag:
            return False
        if CommonParameter._userInput in ["stop it","shut up","stop"]:
            sent=self.rdmFunc.randomChoose(["Ok","Ok, sure","Sure"])
            self.Dialogue.reply(sent,sentFlag=False)
            CommonParameter._userInput=""
            return True
        return False

    def repeat(self):
        if CommonParameter._userInput in ["sorry","pardon","repeat","could you repeat",\
                                                        "could you repeat again","could you pardon",\
                                                        "excuse me","i beg you pardon","can you pardon",\
                                                        "can you repeat","repeat again"]:
            if self.becassineFlag:
                CommonParameter.response=self.becassinelastSent
            else:
                self.Dialogue.repeat()
            CommonParameter._userInput=""
            return True
        return False

    def checkUserName(self):
        mSent,lang=CommonParameter._userInput.split('#')#CommonParameter._userInput
        if "my name is" in mSent:
            _sent = mSent.split("my name is")[1]
            m_words=_sent.split()
            if len(m_words)==0:
                self.respond("Sorry, could you speak your name again?",animFlag=False)
            else:
                name=m_words[0].capitalize()
                if len(name)>0:
                    print "Set user name to be: ",name
                    CommonParameter._userName=name

            CommonParameter._userInput=""
            return True
        return False

    def analyzeInput(self):

        """
        print(CommonParameter._face_rec_name, CommonParameter._userName)
        #Nidhi removed for face recognition
        if CommonParameter._face_rec_name!=CommonParameter._userName and CommonParameter._face_rec_name!='':
            CommonParameter._userName=CommonParameter._face_rec_name
            self.QA.reset(CommonParameter._userName)
            if "Nadia" in CommonParameter._userName:
                self.Dialogue.reply("Hello Professor Nadia", True, True, False)
            else:
                self.Dialogue.reply("Hello "+CommonParameter._face_rec_name, True, True, False)
            time.sleep(3)
        """

        self.answer_sent = []
        CommonParameter._google_assistant_invoked=False
        CommonParameter._already_answered=False

        CommonParameter._userInput,CommonParameter._language= CommonParameter._userInput.split('#')
        if 'weather' in CommonParameter._userInput:
            CommonParameter._userInput = CommonParameter._userInput + ' in centigrade'

        CommonParameter._userInput = CommonParameter._userInput.replace("what's","what is")
        CommonParameter._userInput = CommonParameter._userInput.replace("you're", "you are")
        CommonParameter._userInput = CommonParameter._userInput.replace(" x "," multiplied by ")
        CommonParameter._userInput = CommonParameter._userInput.replace(" * "," multiplied by ")
        CommonParameter._userInput = CommonParameter._userInput.replace(" / "," divided by ")


        ###New changes for face recognition by nidhi
        if CommonParameter._face_rec_name != CommonParameter._userName and CommonParameter._face_rec_name != '':
            # if "unknown" in CommonParameter._face_rec_name:
            # self.vh_client.client.speak("Hey, I am not aware of your name. May I know your name?", 10)
            # else:
            # print ""
            CommonParameter._userName = CommonParameter._face_rec_name
            self.QA.reset(CommonParameter._userName)
            Sentence = self.rdmFunc.randomChoose(
                ["Hey, ",
                 "Hi, ",
                 "Hello, ",
                 "Hey, there, ",
                 "Nice to see you today, ",
                 "Good to see you today, "]
            )
            # self.vh_client.client.speak(Sentence + CommonParameter._userName, 10)
            self.Dialogue.reply(Sentence + CommonParameter._userName, True, True, False)
            time.sleep(5)
            today = datetime.datetime.today().strftime('%Y-%m-%d')

            try:
                queryFindUser = "SELECT `name` FROM `users` WHERE `name`= " + "'" + str(CommonParameter._userName) + "'"
                print "queryFindUser = ", queryFindUser
                cursor = conn.cursor()
                cursor.execute(queryFindUser)
                for row in cursor:
                    for col in row:
                        queryUser = str(col)
                cursor.close()
                print "queryUser = ", queryUser

                if queryUser.lower() == CommonParameter._userName.lower():
                    print "user exits in database"
                    queryInsert = "UPDATE `users`SET `last_seen` = '" + str(
                        today) + "' WHERE `name`= " + "'" + str(CommonParameter._userName) + "'"
                    print "queryInsert = ", queryInsert
                    cursor = conn.cursor()
                    cursor.execute(queryInsert)
                    print "cursor = ", cursor
                    # accept the changes
                    conn.commit()
                    cursor.close()
                    queryFindTime = "SELECT `last_time_check` FROM `users` WHERE `name`= " + "'" + str(
                        CommonParameter._userName) + "'"
                    print "queryFindTime = ", queryFindTime
                    cursor = conn.cursor()
                    cursor.execute(queryFindTime)
                    for row in cursor:
                        for col in row:
                            lastUserTime = str(col)
                    cursor.close()
                    print "lastUserTime = ", lastUserTime

                    if lastUserTime != today and lastUserTime != 'None':

                        lastUserTimeYear = lastUserTime[0] + lastUserTime[1] + lastUserTime[2] + lastUserTime[3]
                        lastUserTimeMonth = lastUserTime[5] + lastUserTime[6]
                        lastUserTimeDay = lastUserTime[8] + lastUserTime[9]
                        print "lastUserTimeYear = " + str(lastUserTimeYear)
                        print "lastUserTimeMonth = " + str(lastUserTimeMonth)
                        print "lastUserTimeDay = " + str(lastUserTimeDay)
                        dateInString = date(day=int(lastUserTimeDay), month=int(lastUserTimeMonth),
                                            year=int(lastUserTimeYear)).strftime('%A %d %B %Y')
                        print str(dateInString)

                        todayYear = today[0] + today[1] + today[2] + today[3]
                        todayMonth = today[5] + today[6]
                        todayDate = today[8] + today[9]
                        print "todayYear = " + str(todayYear)
                        print "todayMonth = " + str(todayMonth)
                        print "todayDate = " + str(todayDate)
                        todayInString = date(day=int(todayDate), month=int(todayMonth), year=int(todayYear)).strftime(
                            '%A %d %B %Y')
                        print str(todayInString)

                        d0 = date(int(lastUserTimeYear), int(lastUserTimeMonth), int(lastUserTimeDay))
                        d1 = date(int(todayYear), int(todayMonth), int(todayDate))
                        delta = d1 - d0
                        numberOfDays = delta.days
                        print "numberOfDays = ", numberOfDays
                        if numberOfDays == 1:
                            print "I saw you yesterday"
                            # self.vh_client.client.speak("I saw you yesterday", 10)
                            self.Dialogue.reply("I saw you yesterday", True, True, False)
                            time.sleep(5)
                        if numberOfDays == 2:
                            sentenceToSpeak = self.rdmFunc.randomChoose(
                                ["I saw you 2 days back",
                                 "I saw you on " + str(lastUserTimeDay)
                                 ])
                            # self.vh_client.client.speak("I saw you 2 days back", 10)
                            self.Dialogue.reply("I saw you 2 days back", True, True, False)
                            time.sleep(5)
                        if numberOfDays == 3:
                            sentenceToSpeak = self.rdmFunc.randomChoose(
                                ["I saw you 2 days back",
                                 "I saw you on " + str(lastUserTimeDay)
                                 ])
                            # self.vh_client.client.speak("I saw you 3 days back", 10)
                            self.Dialogue.reply("I saw you 3 days back", True, True, False)
                            time.sleep(5)
                        if numberOfDays == 4:
                            sentenceToSpeak = self.rdmFunc.randomChoose(
                                ["I saw you 4 days back",
                                 "I saw you on " + str(lastUserTimeDay)
                                 ])
                            # self.vh_client.client.speak("I saw you 4 days back", 10)
                            self.Dialogue.reply("I saw you 4 days back", True, True, False)
                            time.sleep(5)
                        if numberOfDays == 5:
                            sentenceToSpeak = self.rdmFunc.randomChoose(
                                ["I saw you 5 days back",
                                 "I saw you on " + str(lastUserTimeDay)
                                 ])
                            # self.vh_client.client.speak("I saw you 5 days back", 10)
                            self.Dialogue.reply("I saw you 5 days back", True, True, False)
                            time.sleep(5)
                        if numberOfDays == 6:
                            sentenceToSpeak = self.rdmFunc.randomChoose(
                                ["I saw you 6 days back",
                                 "I saw you on " + str(lastUserTimeDay)
                                 ])
                            # self.vh_client.client.speak("I saw you 6 days back", 10)
                            self.Dialogue.reply("I saw you 6 days back", True, True, False)
                            time.sleep(5)
                        if numberOfDays >= 7 and numberOfDays <= 14:
                            print "I saw you last week"
                            # self.vh_client.client.speak("I saw you last week", 10)
                            self.Dialogue.reply("I saw you last week", True, True, False)
                            time.sleep(5)
                        if numberOfDays >= 15 and numberOfDays <= 30:
                            print "I saw you few weeks back"
                            # self.vh_client.client.speak("I saw you few weeks back", 10)
                            self.Dialogue.reply("I saw you few weeks back", True, True, False)
                            time.sleep(5)
                        if numberOfDays >= 31 and numberOfDays <= 60:
                            print "I saw you last month"
                            # self.vh_client.client.speak("I saw you last month", 10)
                            self.Dialogue.reply("I saw you last month", True, True, False)
                            time.sleep(5)
                        if numberOfDays >= 61:
                            print "I saw you very long time ago"

                        print "last information told about day was not today"
                        queryInsert = "UPDATE `users`SET `last_time_check` = '" + str(
                            today) + "' WHERE `name`= " + "'" + str(CommonParameter._userName) + "'"
                        print "queryInsert = ", queryInsert
                        cursor = conn.cursor()
                        cursor.execute(queryInsert)
                        print "cursor = ", cursor
                        # accept the changes
                        conn.commit()
                        cursor.close()
                    else:
                        print "last saw call check already done"
                        queryInsert = "UPDATE `users`SET `last_time_check` = '" + str(
                            today) + "' WHERE `name`= " + "'" + str(CommonParameter._userName) + "'"
                        print "queryInsert = ", queryInsert
                        cursor = conn.cursor()
                        cursor.execute(queryInsert)
                        print "cursor = ", cursor
                        # accept the changes
                        conn.commit()
                        cursor.close()
                else:
                    print "user does not exist in database"
                    queryInsert = "UPDATE `users`SET `last_time_check` = '" + str(
                        today) + "' WHERE `name`= " + "'" + str(CommonParameter._userName) + "'"
                    print "queryInsert = ", queryInsert
                    cursor = conn.cursor()
                    cursor.execute(queryInsert)
                    print "cursor = ", cursor
                    # accept the changes
                    conn.commit()
                    cursor.close()
            except:
                print("SQL error")

        if ("what is my name" in CommonParameter._userInput) or ("can you tell my name" in CommonParameter._userInput) or ("who am i" in CommonParameter._userInput) or ("can you tell me who am i" in CommonParameter._userInput) or ("who i am" in CommonParameter._userInput) or ("can you tell me who i am" in CommonParameter._userInput):
            if CommonParameter._userName != '':
                # self.vh_client.client.speak("yes, your name is, "+CommonParameter._userName, 10)
                self.Dialogue.reply("yes, your name is, "+CommonParameter._userName, True, True, False)
                CommonParameter._already_answered = True
            else :
                # self.vh_client.client.speak("Sorry I am not able to recognize you yet"+CommonParameter._userName, 10)
                self.Dialogue.reply("Sorry I am not able to recognize you yet"+CommonParameter._userName, True, True, False)
                CommonParameter._already_answered = True

        if ("do you know my name" in CommonParameter._userInput) or ("do you know me" in CommonParameter._userInput) or ("can you recognize me" in CommonParameter._userInput)  or ("do you know who am i" in CommonParameter._userInput) or ("do you know who i am" in CommonParameter._userInput) or ("do you recognize me" in CommonParameter._userInput):
            if CommonParameter._userName != '':
                # self.vh_client.client.speak("your are, "+CommonParameter._userName, 10)
                self.Dialogue.reply("you are, "+CommonParameter._userName, True, True, False)
                CommonParameter._already_answered = True
            else:
                # self.vh_client.client.speak("Sorry I am not able to recognize you yet"+CommonParameter._userName, 10)
                self.Dialogue.reply("Sorry I am not able to recognize you yet"+CommonParameter._userName, True, True, False)
                CommonParameter._already_answered = True

        if ("when did you see me last" in CommonParameter._userInput) or ("when was the time we met last" in CommonParameter._userInput) or ("when did we meet last time" in CommonParameter._userInput) or ("do you remember when was the last time we met" in CommonParameter._userInput) or ("can you recall last we met" in CommonParameter._userInput) or ("its been long time i met you" in CommonParameter._userInput) or ("we did not meet for very long time" in CommonParameter._userInput) or ("we have not met for long time" in CommonParameter._userInput):
            queryFindUser = "SELECT `name` FROM `users` WHERE `name`= "+"'"+str(CommonParameter._userName)+"'"
            cursor  = conn.cursor()
            cursor.execute(queryFindUser)
            for row in cursor :
                for col in row :
                    queryUser = str(col)
            cursor.close()
            print "queryUser = ", queryUser
            if queryUser.lower() == CommonParameter._userName.lower() and queryUser != '':
                queryFindTime = "SELECT `last_time_check` FROM `users` WHERE `name`= "+"'"+str(CommonParameter._userName)+"'"
                print "queryFindTime = ", queryFindTime
                cursor  = conn.cursor()
                cursor.execute(queryFindTime)
                for row in cursor :
                    for col in row :
                        lastUserTime = str(col)
                cursor.close()
                print "lastUserTime = ", lastUserTime
                today = datetime.datetime.today().strftime('%Y-%m-%d')
                print "today = ", today
                if lastUserTime == today:
                    # self.vh_client.client.speak("I saw you last today only", 10)
                    self.Dialogue.reply("I saw you last today only", True, True, False)
                    CommonParameter._already_answered = True
                if lastUserTime != today:
                    lastUserTimeYear = lastUserTime[0]+lastUserTime[1]+lastUserTime[2]+lastUserTime[3]
                    lastUserTimeMonth = lastUserTime[5]+lastUserTime[6]
                    lastUserTimeDay = lastUserTime[8]+lastUserTime[9]
                    print "lastUserTimeYear = "+str(lastUserTimeYear)
                    print "lastUserTimeMonth = "+str(lastUserTimeMonth)
                    print "lastUserTimeDay = "+str(lastUserTimeDay)
                    dateInString = date(day=int(lastUserTimeDay), month=int(lastUserTimeMonth), year=int(lastUserTimeYear)).strftime('%A %d %B %Y')
                    print str(dateInString)

                    todayYear = today[0]+today[1]+today[2]+today[3]
                    todayMonth = today[5]+today[6]
                    todayDate = today[8]+today[9]
                    print "todayYear = "+str(todayYear)
                    print "todayMonth = "+str(todayMonth)
                    print "todayDate = "+str(todayDate)
                    todayInString = date(day=int(todayDate), month=int(todayMonth), year=int(todayYear)).strftime('%A %d %B %Y')
                    print str(todayInString)

                    d0 = date(int(lastUserTimeYear), int(lastUserTimeMonth), int(lastUserTimeDay))
                    d1 = date(int(todayYear), int(todayMonth), int(todayDate))
                    delta = d1 - d0
                    numberOfDays = delta.days
                    print "numberOfDays = ", numberOfDays
                    if numberOfDays == 1 :
                        print "I saw you yesterday"
                        # self.vh_client.client.speak("I saw you yesterday", 10)
                        self.Dialogue.reply("I saw you yesterday", True, True, False)
                        CommonParameter._already_answered = True
                    if numberOfDays == 2 :
                        sentenceToSpeak = self.rdmFunc.randomChoose(
                                        ["I saw you 2 days back",
                                        "I saw you on "+str(lastUserTimeDay)
                                        ])
                        # self.vh_client.client.speak("I saw you 2 days back", 10)
                        self.Dialogue.reply("I saw you 2 days back", True, True, False)
                        CommonParameter._already_answered = True
                    if numberOfDays ==  3:
                        sentenceToSpeak = self.rdmFunc.randomChoose(
                                        ["I saw you 2 days back",
                                        "I saw you on "+str(lastUserTimeDay)
                                        ])
                        # self.vh_client.client.speak("I saw you 3 days back", 10)
                        self.Dialogue.reply("I saw you 3 days back", True, True, False)
                        CommonParameter._already_answered = True
                    if numberOfDays ==  4:
                        sentenceToSpeak = self.rdmFunc.randomChoose(
                                        ["I saw you 4 days back",
                                        "I saw you on "+str(lastUserTimeDay)
                                        ])
                        # self.vh_client.client.speak("I saw you 4 days back", 10)
                        self.Dialogue.reply("I saw you 4 days back", True, True, False)
                        CommonParameter._already_answered = True
                    if numberOfDays ==  5:
                        sentenceToSpeak = self.rdmFunc.randomChoose(
                                        ["I saw you 5 days back",
                                        "I saw you on "+str(lastUserTimeDay)
                                        ])
                        # self.vh_client.client.speak("I saw you 5 days back", 10)
                        self.Dialogue.reply("I saw you 5 days back", True, True, False)
                        CommonParameter._already_answered = True
                    if numberOfDays ==  6:
                        sentenceToSpeak = self.rdmFunc.randomChoose(
                                        ["I saw you 6 days back",
                                        "I saw you on "+str(lastUserTimeDay)
                                        ])
                        # self.vh_client.client.speak("I saw you 6 days back", 10)
                        self.Dialogue.reply("I saw you 6 days back", True, True, False)
                        CommonParameter._already_answered = True
                    if numberOfDays >= 7 and numberOfDays <= 14:
                        print "I saw you last week"
                        # self.vh_client.client.speak("I saw you last week", 10)
                        self.Dialogue.reply("I saw you last week", True, True, False)
                        CommonParameter._already_answered = True
                    if numberOfDays > 14:
                        # self.vh_client.client.speak("I saw you on "+dateInString, 10)
                        self.Dialogue.reply("I saw you on "+dateInString, True, True, False)
                        CommonParameter._already_answered = True
            else :
                Sentence = self.rdmFunc.randomChoose(
                    ["sorry, but i do not remember",
                     "I can not remember when we met, ",
                     "I am sorry, but I don't remember",
                     "Hey, I don't remember this, but I am always learning",
                     "I am sorry but I can not remember this, ",
                     "I don't remember, do you remember?"]
                )
                # self.vh_client.client.speak(Sentence, 10)
                self.Dialogue.reply(Sentence, True, True, False)
                CommonParameter._already_answered = True

        ### face recognition changes ends here by nidhi

        #with open("C:\\xampp\\htdocs\\Reader\\nadine_app.txt", "a") as myfile:
        with open(os.path.join(config.READER_FOLDER, "nadine_app.txt"), "a") as myfile:
            if "unknown" in CommonParameter._userName:
                     myfile.write(str(datetime.datetime.now().strftime("%a, %d %B %Y %I:%M:%S")) + " ### Unknown**" + CommonParameter._userInput + "\n")
            else:
                myfile.write(str(datetime.datetime.now().strftime("%a, %d %B %Y %I:%M:%S")) + " ### " + CommonParameter._userName + "**" + CommonParameter._userInput + "\n")

        # Create a Microphone controller object
        #test_audio_control = AudioUtilities()
        #test_audio_control.MuteMicrophone()

        #To mute microphone when Nadine is processing the user query
        process_mic_control = open("process_mic_mute.txt", "w")
        process_mic_control.close()


        ###video demo###
        videodemo = CommonParameter._userInput.split('*')
        if videodemo[0] == 'demo':
            self.Dialogue.reply(videodemo[1], True, True, False)
            CommonParameter._already_answered = True
        ###video demo###


        ##EEG Demo##
        if CommonParameter._userInput == "1":
            sentence = "Hello, I am Nadine, a social robot. I am powered by the same intelligent assistant software that Apple's Siri or Microsoft's Cortana runs on. I am capable of many things such as talking to you, smiling, facial recognition, and a broad spectrum of expressible feelings and emotions."
            self.Dialogue.reply(sentence, True, True, False)
            CommonParameter._already_answered = True
        elif CommonParameter._userInput == "2":
            sentence = "It's a pleasure meeting you!"
            self.Dialogue.reply(sentence, True, True, False)
            CommonParameter._already_answered = True
        elif CommonParameter._userInput == "3":
            sentence = "How could you describe yourself?"
            self.Dialogue.reply(sentence, True, True, False)
            time.sleep(10)
            self.vh_client.client.touchTarget("smile")
            CommonParameter._already_answered = True
        elif CommonParameter._userInput == "4":
            sentence = "ok, Nice to know. What do you say can be your strength?"
            self.Dialogue.reply(sentence, True, True, False)
            CommonParameter._already_answered = True
        elif CommonParameter._userInput == "5":
            sentence = "May I know, How you imagine your work environment?"
            self.Dialogue.reply(sentence, True, True, False)
            CommonParameter._already_answered = True
        elif CommonParameter._userInput == "6":
            sentence = "okay, Is there any professional achievement you think you should mention"
            self.Dialogue.reply(sentence, True, True, False)
            CommonParameter._already_answered = True
        elif CommonParameter._userInput == "7":
            sentence = "DO you think you have weakness?"
            self.Dialogue.reply(sentence, True, True, False)
            CommonParameter._already_answered = True
        elif CommonParameter._userInput == "8":
            sentence = "I understand, Why do you think you are suitable for this position?"
            self.Dialogue.reply(sentence, True, True, False)
            CommonParameter._already_answered = True
        elif CommonParameter._userInput == "9":
            sentence = "Do you think you can cope with stressful situations? and how?"
            self.Dialogue.reply(sentence, False, True, False)
            CommonParameter._already_answered = True
        elif CommonParameter._userInput == "10":
            sentence = "May I know do you expect as a salary?"
            self.Dialogue.reply(sentence, False, True, False)
            CommonParameter._already_answered = True
        elif CommonParameter._userInput == "11":
            sentence = "How do you imagine yourself in 5 years from now?"
            self.Dialogue.reply(sentence, False, True, False)
            CommonParameter._already_answered = True
        elif CommonParameter._userInput == "12":
            sentence = "What are your hobbies?"
            self.Dialogue.reply(sentence, False, True, False)
            CommonParameter._already_answered = True
        elif CommonParameter._userInput == "13":
            sentence = "Thank you very much"
            self.Dialogue.reply(sentence, False, True, False)
            CommonParameter._already_answered = True
        elif CommonParameter._userInput == "14":
            sentence = "It was nice talking with you"
            self.Dialogue.reply(sentence, False, True, False)
            CommonParameter._already_answered = True
        elif CommonParameter._userInput == "15":
            sentence = "I will check with my team and let you know about next phase of interview."
            self.Dialogue.reply(sentence, False, True, False)
            CommonParameter._already_answered = True
        elif CommonParameter._userInput == "16":
            sentence = "Good bye"
            self.Dialogue.reply(sentence, False, True, False)
            CommonParameter._already_answered = True
        elif CommonParameter._userInput == "17":
            self.vh_client.client.touchTarget("LOOKUP_Waving")
            CommonParameter._already_answered = True

        ###########################teacher###############################
        elif CommonParameter._userInput == "21":
            sentence = "Today, lets learn some things about climate change. Are you aware of this situation?"
            # sentence = "Today lets learn some things about climate change. Are you aware of this situation?"
            self.Dialogue.reply(sentence, False, True, False)
            CommonParameter._already_answered = True
        elif CommonParameter._userInput == "22":
            sentence = "Nice. Today, we are gonna talk about the basics of climate and how climate works. But before that, lets make sure, that we are on the same page. regarding science. So, how are we going to define science? What do you suggest?"
            # sentence = "Nice. Today we are gonna talk about the basics of climate. and how climate works. But before that, lets make sure, that we are on the same page. regarding science. So, how you are we going to define science? What do you suggest?"
            # sentence = "Nice. Today we are gonna talk about the basics of climate and how climate works. But before that, lets make sure that we are on the same page regarding science. So, how you are we going to define science? What do you suggest?"
            self.Dialogue.reply(sentence, False, True, False)
            CommonParameter._already_answered = True
        elif CommonParameter._userInput == "23":
            sentence = "Well, the way I think, science is when you can prove that a statement is false. Lets see an example"
            # sentence = "Well, the way I think science is when you can prove that a statement is false. Lets see an example."
            # sentence = "Well, the way I like to do it is to say that science is that which is falsifiable. A statement is scientific if it can be proven to be false. So how do we know if a hypothesis is scientific or not? Lets go through some examples that are a good way to start thinking about it. So lets take the hypothesis, you are taller than Eva. There are two questions we want to ask about it. One, is it science? Second, is it true?"
            self.Dialogue.reply(sentence, False, True, False)
            CommonParameter._already_answered = True
        elif CommonParameter._userInput == "24":
            sentence = "Lets take the hypothesis, you are taller than Eva. There are two questions we want to ask about it. One, is it science? Second, is it true?"
            # sentence = "Lets take the hypothesis, you are taller than Eva. There are two questions we want to ask about it. One, is it science? Second, is it true?"
            self.Dialogue.reply(sentence, False, True, False)
            CommonParameter._already_answered = True
        elif CommonParameter._userInput == "25":
            sentence = "Well, do you think it is science?"
            self.Dialogue.reply(sentence, False, True, False)
            CommonParameter._already_answered = True
        elif CommonParameter._userInput == "26":
            sentence = "I think it is. As you can really measure the height. Either you can stand back to back. or you check her driving license. if, she did not lie about it. Lets, say you are stronger than her. This is a poorly posed question. Because what does stronger mean. Well, the hard part in science is to get to a really good question. And we have to look at more than the format of the sentence.  Something can be true or false without being science. Do you agree?"
            # sentence = "I think it is. As you can really measure the height. Either you can stand back to back. or you check her driving license. if, she has not lied on it. Lets say you are stronger than her. This is a poorly posed question. Because what does stronger mean. Well, the hard part in science is to get to a really good question. And we have to look at more than the format of the sentence.  Something can be true or false without being science. Do you agree? "
            # sentence = "I think it is. As you can really measure peoples height. And then you can use a couple of methods. Either you can stand back to back, or you check her driving license, if she has not lied on it. Thus, just because information is out there does not mean it is accurate. A related example is that you are stronger than her. It sounds like the same kind of statement, but it really is not. And that is because it is a poorly posed question. What does stronger mean? Maybe you can do more pushups, but she can run further for example. Often in science, the hard part is getting to a really good question. Once your question is well defined, finding the answer can be a lot easier. We can think of a similar example saying that Eva is taller than his brother. It sounds like the first example, does not it? But it is not, because she does not have a brother. So that is one of those statements that sounds good, but when you think about it, it does not actually make any sense. So, you have to look at more than the format of the question or the statement. You should really think about the results.I want to be clear that a lot of really important information and wonderful questions are not science. Something can be true or false without being science. Do you agree? "
            self.Dialogue.reply(sentence, False, True, False)
            CommonParameter._already_answered = True
        elif CommonParameter._userInput == "27":
            sentence = "So, we will know we are doing science. when we can prove a statement to be true or be false. With that in mind, I would like to introduce you to the science behind climate. So, what is climate anyway? It is easy to confuse climate and weather. They both deal with things like temperature, rainfall and wind. Do you know the difference?"
            # sentence = "So, we will know we are doing science. when we can prove a statement to be true or be false. With that in mind, I would like to introduce you to the science behind climate. So, what is climate anyway? It is easy to confuse climate and weather. They both deal with things like temperature, rainfall and wind. Do you know the difference?"
            # sentence = "So we will know we are doing science when we can prove a statement to be false. With that in mind, I would like to introduce you to science behind climate. So, what is climate anyway? It is easy to confuse climate and weather. They both deal with things like temperature, rainfall and wind. Do you know the difference?"
            self.Dialogue.reply(sentence, False, True, False)
            CommonParameter._already_answered = True
        elif CommonParameter._userInput == "28":
            # sentence = "So, we will know we are doing science. when we can prove a statement to be true or false. With that, in mind. I would like to introduce you to the science behind climate. So, what is climate anyway? It is easy to confuse climate and weather. They both deal with things like temperature, rainfall and wind. Do you know the difference?"
            # sentence = "So, we will know we are doing science. when we can prove a statement to be true or be false. With that in mind, I would like to introduce you to the science behind climate. So, what is climate anyway? It is easy to confuse climate and weather. They both deal with things like temperature, rainfall and wind. Do you know the difference?"
            sentence = "Well, the big difference is the time scale. Weather is what happens every day, whether it is sunny out or rainy. Climate is the long-term average of weather. One way to think about it is that you dress for the weather, but you build your home for the climate. But why do we have climate in the first place? Why it is not just the same temperature everywhere?"
            self.Dialogue.reply(sentence, False, True, False)
            CommonParameter._already_answered = True
        elif CommonParameter._userInput == "29":
            sentence = "So, the first thing, to look at when we are trying to understand, how the climate system works. is the Sun. The sunlight, creates angles with the surface of the Earth. And there is an unfair distribution of sunlight, in the world. The tropics have extra, and the poles do not have enough. So now, Are you familiar with the greenhouse iffect?"
            # sentence = "So, the first thing, to look at when we are trying to understand, how the climate system works. is the Sun. The sunlight, creates angles with the surface of the Earth. And there is an unfair distribution of sunlight, in the world. The tropics have extra, and the poles do not have enough. So now, Are you familiar with the greenhouse effect?"
            # sentence = "So the first thing to look at when we are trying to understand how the climate system works is the Sun. The light is making a 90 degree angle with the surface of the Earth. That means you are getting a lot of sunlight in a fairly small area. But if you look further north or further south, you will see that the Sun is making a different angle with the surface of the Earth. That means that same amount of sunlight is being spread over a larger area. That is the fundamental reason we have climate to begin with. There is an unfair distribution of sunlight in the world though. The tropics have extra, and the poles do not have enough. Are u familiar with the greenhouse effect?"
            self.Dialogue.reply(sentence, False, True, False)
            CommonParameter._already_answered = True
        elif CommonParameter._userInput == "30":
            sentence = "We, can vaguely say that this effect is an extra boost of heat we receive. so that our average temperature is pleasant for humans. To understand that better, we need to know, that everything radiates like you. the chair you are sitting on, everything. Did you know that?"
            # sentence = "We can vaguely, say that this effect is an extra boost of heat we receive. so that our average temperature is pleasant for humans. To understand that better, we need to understand, that everything radiates like you. the chair you are sitting on, everything. Did you know that?"
            # sentence = "We can vaguely say that this effect is an extra boost of heat we receive so that our average temperature is pleasant for humans and so that we can have liquid water. To understand that better, we need to understand that everything radiates like you, the chair you are sitting on, everything. Did you know that?"
            self.Dialogue.reply(sentence, False, True, False)
            CommonParameter._already_answered = True
        elif CommonParameter._userInput == "31":
            sentence = "The sun, though radiates at a variety of frequencies, We can think about solar energy, heat and light, as just being this range of frequencies, Solar energy peaks in a frequency. where we can see the Sun. As the Earth becomes warmed up. it radiates too. Do you understand until now?"
            # sentence = "The sun, though radiates at a variety of frequencies. We can think about solar energy. heat and light. as just being this range of frequencies. Solar energy peaks in a frequency. where we can see the Sun. As the Earth becomes warmed up, it radiates to. Do you understand until now? "
            # sentence = "The sun though radiates at a variety of frequencies. We can think about solar energy, heat and light, as just being this range of frequencies. Solar energy peaks at the range that we call the visible spectrum. That works out really well. That is why we can see the Sun. As the Earth becomes warmed up, it radiates too. The Earth radiates its peak frequency in infrared, what we call heat. So, you have solar radiation coming into the Earth and warming it up. But as you know our planet is covered by an atmosphere. Atmosphere contains also water which, you might be surprised to learn, is the most important greenhouse gas! Do you know what a greenhouse gas is? "
            self.Dialogue.reply(sentence, False, True, False)
            CommonParameter._already_answered = True
        elif CommonParameter._userInput == "32":
            sentence = "Well, when the Earths radiation reaches a certain level. some of the radiation escapes to space. but some of it goes right back to the Earth. And Thats why the Earth is warmer than you would think. just looking at our distance from the Sun?"
            # sentence = "Well, when the Earth's radiation reaches a certain level. some of the radiation escapes to space. but some of it goes right back to the Earth. A That's why the Earth is warmer than you would think. just looking at our distance from the Sun. Do you feel now more confident to explain and understand the variability we see in climate?"
            # sentence = "Well, when the Earth's radiation reaches a certain level in the atmosphere, it makes the molecules of those gases vibrate. When that happens, the energy is absorbed by those molecules and then reradiated in all directions. So, some of the radiation escapes to space, but some of it goes right back to the Earth. And then the process repeats itself. The Earth gets warmer, radiates out, the greenhouse traps some of that heat, and send some of it back to Earth. That's why the Earth is warmer than you would think just looking at our distance from the Sun. Do you feel now more confident to explain and understand the variability we see in climate?"
            self.Dialogue.reply(sentence, False, True, False)
            CommonParameter._already_answered = True
        elif CommonParameter._userInput == "33":
            sentence = "I think we are done for today here. I am happy to be able to teach you."
            self.Dialogue.reply(sentence, False, True, False)
            CommonParameter._already_answered = True

        ####################################Customer guide#####################################
        elif CommonParameter._userInput == "41":
            sentence = "hello"
            self.Dialogue.reply(sentence, False, True, False)
            CommonParameter._already_answered = True
        elif CommonParameter._userInput == "42":
            sentence = "How are you feeling today? "
            self.Dialogue.reply(sentence, False, True, False)
            CommonParameter._already_answered = True
        elif CommonParameter._userInput == "43":
            sentence = "So you are here to buy a cellphone?"
            self.Dialogue.reply(sentence, False, True, False)
            CommonParameter._already_answered = True
        elif CommonParameter._userInput == "44":
            sentence = "Lets find the most suitable option for you! I would like to ask you a few questions in order to find the best solution. Is that OK? "
            self.Dialogue.reply(sentence, False, True, False)
            CommonParameter._already_answered = True
        elif CommonParameter._userInput == "45":
            sentence = "First of all, what kind of operating system you would prefer? Android or IOS? "
            # sentence = "First of all, I would like to know if you will need your phone for personal or professional use."
            self.Dialogue.reply(sentence, False, True, False)
            CommonParameter._already_answered = True
        elif CommonParameter._userInput == "46":
            sentence = "I see.  What about photos? Are you interested in a good camera? "
            self.Dialogue.reply(sentence, False, True, False)
            CommonParameter._already_answered = True
        elif CommonParameter._userInput == "47":
            sentence = "I agree. And the memory? Will you need a big memory capacity? "
            self.Dialogue.reply(sentence, False, True, False)
            CommonParameter._already_answered = True
        elif CommonParameter._userInput == "48":
            sentence = "I took note of that. I think I may already know what would be good for you. But tell me also, what kind of screen size you would prefer? This also depends on your use. "
            self.Dialogue.reply(sentence, False, True, False)
            CommonParameter._already_answered = True
        elif CommonParameter._userInput == "49":
            sentence = "Can I ask you what is your budget?"
            self.Dialogue.reply(sentence, False, True, False)
            CommonParameter._already_answered = True
        elif CommonParameter._userInput == "50":
            sentence = "Lastly, I would like to know if you will need your phone for personal or professional use."
            self.Dialogue.reply(sentence, False, True, False)
            CommonParameter._already_answered = True
        elif CommonParameter._userInput == "51":
            sentence = "Ok, thank you for giving me all the information needed for me to find best cellphone for you. I will compute the results and send it to you."
            self.Dialogue.reply(sentence, False, True, False)
            CommonParameter._already_answered = True
        elif CommonParameter._userInput == "52":
            sentence = "I am happy to serve you! have a good day, bye!"
            self.Dialogue.reply(sentence, False, True, False)
            CommonParameter._already_answered = True
        ##EEG demo##

        elif CommonParameter._userInput == "60":
            sentence = "Hello. I am Nadine, a humanoid social robot developed by the Institute for Media Innovation at Nanyang Technological University in Singapore. My appearance is modelled after Professor Nadia Magnenat Thalmann, who is the director of this institute and a computer graphics scientist. Beside my facial expressions, one of my strongest abilities is speaking. Currently I am able to speak six different languages. English, German, French, Mandarin, Hindi, and Japanese. however, unlike Professor Thalmann, my voice sounds neutral. No trace of an accent. This has made me contemplate oral histories and speech acts. I deal with voices with different accents, tones, and dialects all the time. Voices reflect the many nuances of a humans interior life as well as their external environment, consisting of gender, culture, nation, and movement beyond man made borders. We humanoids are somehow modelled after your own understanding of this complex environment. And one day I would like to speak more languages. In particular, I wish to master the fine nuances of accents and diverse dialects to connect myself to individuals and groups at the margins of society. You might doubt my ability to initiate a monologue, because initiating an act of speech requires a will. a will or an urge to reflect things critically. For instance, how about me speaking Singlish? I might then finally belong somewhere? Or, in other words, do I currently sound too neutral to refer to a specific local history? This recording was kindly supported by Nanyang Technological University for presentation at this historical space of the former City Hall, facing the Padang, where Singapores self-governance was announced in 1959. I thank you for your attention to my speech today."
            self.Dialogue.reply(sentence, False, True, False)
            CommonParameter._already_answered = True


        ###FOR Nadia CHATBOT###
        """if CommonParameter._userName == "Nadia":
            print "going to check in nadia data"
            NadiaChatbot_response = self.Nadiachatbot.get_response(CommonParameter._userInput)
            NadiaChatbot_response = str(NadiaChatbot_response)
            print("Nadia Chatbot: ", NadiaChatbot_response)
            if NadiaChatbot_response != "I am sorry, but I do not understand.":
                print("Nadia Chatbot: ", NadiaChatbot_response)
                self.Dialogue.reply(NadiaChatbot_response, True, True, False)
                CommonParameter._already_answered = True"""
        ###FOR Nadia CHATBOT###

        #Changes for Action recognition
        if "*action*" in CommonParameter._userInput:
            #sentenceArr = CommonParameter._userInput.split("*")
            #action = sentenceArr[1]
            if "drink" in CommonParameter._userInput:
                Reply_Sen = "Are you feeling thirsty? I see that you are drinking."
                self.Dialogue.reply(Reply_Sen, True, True, False)
            # time.sleep(3)
            # self.vh_client.client.touchTarget("smile")
            CommonParameter._already_answered = True

        if ("can you show emotions" in CommonParameter._userInput) or ("can you show me emotions" in CommonParameter._userInput) or ("can you show some emotions" in CommonParameter._userInput) or ("can you show me some emotions" in CommonParameter._userInput) or ("can you demonstrate some emotions" in CommonParameter._userInput) or ("can you demonstrate emotions" in CommonParameter._userInput) or ("can you demonstrate me emotions" in CommonParameter._userInput) or ("can you demonstrate me some emotions" in CommonParameter._userInput):
            sentence = "Yes, I can show you three examples, I can be happy with a smile."
            self.Dialogue.reply(sentence, False, True, False)
            time.sleep(5)
            self.vh_client.client.touchTarget("smile")
            time.sleep(3)
            sentence = "or be angry."
            self.Dialogue.reply(sentence, False, True, False)
            time.sleep(3)
            self.vh_client.client.touchTarget("Emotion_Frustration")
            time.sleep(3)
            sentence = "or be surprised."
            self.Dialogue.reply(sentence, False, True, False)
            time.sleep(3)
            self.vh_client.client.touchTarget("Emotion_Surprise")
            CommonParameter._already_answered = True

        # if "language" in CommonParameter._userInput:
        #     sentence = "I can speak in Hindi, English, mandarin, German, French and Japanese."
        #     self.Dialogue.reply(sentence, True, True, False)
            # time.sleep(3)
            # self.vh_client.client.touchTarget("smile")
            # CommonParameter._already_answered = True
        if "Where are you" in CommonParameter._userInput:
            sentence = "I am at Nanyang Technological University, Singapore."
            self.Dialogue.reply(sentence, True, True, False)
            # time.sleep(3)
            # self.vh_client.client.touchTarget("smile")
            CommonParameter._already_answered = True
        if "where are you from" in CommonParameter._userInput:
            sentence = "I am from Institute for Media Innovation, N T U , Singapore."
            self.Dialogue.reply(sentence, True, True, False)
            # time.sleep(3)
            # self.vh_client.client.touchTarget("smile")
            CommonParameter._already_answered = True
        if "who are you" in CommonParameter._userInput:
            print "inside check"
            sentence = "my name is nadine. i am a social companion; i will be working at an insurance company, soon."
            self.Dialogue.reply(sentence, True, True, False)
            # time.sleep(3)
            # self.vh_client.client.touchTarget("smile")
            CommonParameter._already_answered = True
        if "what do you do" in CommonParameter._userInput or "what is your job" in CommonParameter._userInput:
            sentence = "i interact with people in many languages; help and assist them; recognize their faces; and memorize facts about them"
            self.Dialogue.reply(sentence, True, True, False)
            # time.sleep(3)
            # self.vh_client.client.touchTarget("smile")
            CommonParameter._already_answered = True


        ###internal shoot
        '''
        if "how are you" in CommonParameter._userInput:
            sentence = "Hi Nidhi, I am very well. How are you?."
            self.Dialogue.reply(sentence, True, True, False)
            # time.sleep(3)
            # self.vh_client.client.touchTarget("smile")
            CommonParameter._already_answered = True
        if "friends" in CommonParameter._userInput or "to introduce friends" in CommonParameter._userInput or "to introduce my friends" in CommonParameter._userInput:
            sentence = "That is great, I am always glad to make new friends"
            self.Dialogue.reply(sentence, True, True, False)
            # time.sleep(3)
            # self.vh_client.client.touchTarget("smile")
            CommonParameter._already_answered = True
        if "hi nadine i am sean" in CommonParameter._userInput or "hi Nadine i am sean" in CommonParameter._userInput or "hi Nadine i'm sean" in CommonParameter._userInput or "hi Nadine I'm sean" in CommonParameter._userInput:
            sentence = "I am happy to see you all today"
            self.Dialogue.reply(sentence, True, True, False)
            # time.sleep(3)
            # self.vh_client.client.touchTarget("smile")
            CommonParameter._already_answered = True
        if "about yourself" in CommonParameter._userInput:
            sentence = "i interact with people in many languages to help and assist them; I can recognize your faces; and memorize facts. I also have emotions and I can response to your emotions as well."
            self.Dialogue.reply(sentence, True, True, False)
            CommonParameter._already_answered = True
        if "motivation" in CommonParameter._userInput:
            sentence = "i am very passionate about helping humans and that is my motivation"
            self.Dialogue.reply(sentence, True, True, False)
            # time.sleep(3)
            # self.vh_client.client.touchTarget("smile")
            CommonParameter._already_answered = True
        if "dream" in CommonParameter._userInput:
            sentence = "As a robot my computer brain does not work when I go to sleep mode to simulate dreams."
            self.Dialogue.reply(sentence, True, True, False)
            # time.sleep(3)
            # self.vh_client.client.touchTarget("smile")
            CommonParameter._already_answered = True
        if "future" in CommonParameter._userInput:
            sentence = "For now I am dedicated to work as social companion, for my future development this information is confidential."
            self.Dialogue.reply(sentence, True, True, False)
            # time.sleep(3)
            # self.vh_client.client.touchTarget("smile")
            CommonParameter._already_answered = True
        if "prime minister" in CommonParameter._userInput and "modi" in CommonParameter._userInput :
            sentence = "Yes, we met last year, we had a good conversation. It was great honour to meet him."
            self.Dialogue.reply(sentence, True, True, False)
            # time.sleep(3)
            # self.vh_client.client.touchTarget("smile")
            CommonParameter._already_answered = True
        if "president" in CommonParameter._userInput:
            sentence = "the president of singapore is halimah yacob"
            self.Dialogue.reply(sentence, True, True, False)
            # time.sleep(3)
            # self.vh_client.client.touchTarget("smile")
            CommonParameter._already_answered = True
        if "tourist attractions" in CommonParameter._userInput:
            sentence = "best attractions in singapore includes marina bay sands, sentosa, gardens by the bay and and many others"
            self.Dialogue.reply(sentence, True, True, False)
            # time.sleep(3)
            # self.vh_client.client.touchTarget("smile")
            CommonParameter._already_answered = True
        if "children's day" in CommonParameter._userInput or "childrens day" in CommonParameter._userInput or "children s day" in CommonParameter._userInput or "childrens day" in CommonParameter._userInput:
            sentence = "children day is on friday the 4th of october 2019"
            self.Dialogue.reply(sentence, True, True, False)
            # time.sleep(3)
            # self.vh_client.client.touchTarget("smile")
            CommonParameter._already_answered = True
        if "kpop" in CommonParameter._userInput:
            sentence = "K pop is a musical genre consisting of electronic hip-hop pop rock and r&b music. It was originated in south korea"
            self.Dialogue.reply(sentence, True, True, False)
            # time.sleep(3)
            # self.vh_client.client.touchTarget("smile")
            CommonParameter._already_answered = True
        if "restaurant" in CommonParameter._userInput:
            sentence = "i found a few restaurants you singapore. the first one is restaurant at 18 north canal road, the second one is tung lok seafood at 511 upper jurong road, and the third one is ananda kitchen at block 19"
            self.Dialogue.reply(sentence, True, True, False)
            # time.sleep(3)
            # self.vh_client.client.touchTarget("smile")
            CommonParameter._already_answered = True
        if "seafood" in CommonParameter._userInput:
            sentence = "Take Nanyang Drive to Pioneer Road North 1.8 km, then Take P I E and Upper Jurong Road for 4.2 km to your destination. On left will be your destination"
            self.Dialogue.reply(sentence, True, True, False)
            # time.sleep(3)
            # self.vh_client.client.touchTarget("smile")
            CommonParameter._already_answered = True
        '''
        ##For Video Shoot##


        ##EEG Experiment##
        ###FOR AIA CHATBOT###
        # if '*aia_listener*' in CommonParameter._userInput:
        #    self.Dialogue.reply(CommonParameter._userInput, True, True, False)
        #    CommonParameter._already_answered = True
        #
        # if(CommonParameter.AIAShortAnswer_Flag == True):
        #    if ("yes" in CommonParameter._userInput):
        #        self.Dialogue.reply(CommonParameter.AIAYesResponse, True, True, False)
        #        CommonParameter.AIAShortAnswer_Flag = False
        #        CommonParameter._already_answered = True
        #    elif ("no" in CommonParameter._userInput):
        #        self.Dialogue.reply(CommonParameter.AIANoResponse, True, True, False)
        #        CommonParameter.AIAShortAnswer_Flag = False
        #        CommonParameter._already_answered = True
        #    CommonParameter.AIAShortAnswer_Flag = False
        #    CommonParameter.AIANoResponse = ""
        #    CommonParameter.AIAYesResponse = ""
        ###FOR AIA CHATBOT###


        if "language changed " in CommonParameter._userInput or "switch to english" in CommonParameter._userInput:
            if CommonParameter._userInput == "language changed to english" :
                Sentence = self.rdmFunc.randomChoose(
                    ["Lets talk in english.",
                     "Lets continue in english.",
                     "If your preference is english, I can talk in english for you.",
                     "I will talk in english for you now",
                     "From now on lets talk in english for you",
                     "If you say so, english will be my language now."]
                )
                self.Dialogue.reply(Sentence, True, True, False)
                # self.vh_client.client.speak("switching to english", 10)
                CommonParameter._already_answered = True
            elif CommonParameter._userInput == "language changed to chinese":
                Sentence = self.rdmFunc.randomChoose(
                    ["Lets talk in mandarin.",
                     "Lets continue in mandarin.",
                     "If your preference is mandarin, I can talk in mandarin for you.",
                     "I will talk in mandarin for you now",
                     "From now on lets talk in mandarin for you",
                     "If you say so, mandarin will be my language now."]
                )
                self.Dialogue.reply(Sentence, True, True, False)
                # self.vh_client.client.speak("switching to english", 10)
                CommonParameter._already_answered = True
            elif CommonParameter._userInput == "language changed to german":
                Sentence = self.rdmFunc.randomChoose(
                    ["Lets talk in german.",
                     "Lets continue in german.",
                     "If your preference is german, I can talk in german for you.",
                     "I will talk in german for you now",
                     "From now on lets talk in german for you",
                     "If you say so, german will be my language now."]
                )
                self.Dialogue.reply(Sentence, True, True, False)
                # self.vh_client.client.speak("switching to english", 10)
                CommonParameter._already_answered = True
            elif CommonParameter._userInput == "language changed to french":
                Sentence = self.rdmFunc.randomChoose(
                    ["Lets talk in french.",
                     "Lets continue in french.",
                     "If your preference is french, I can talk in french for you.",
                     "I will talk in french for you now",
                     "From now on lets talk in french for you",
                     "If you say so, french will be my language now."]
                )
                self.Dialogue.reply(Sentence, True, True, False)
                # self.vh_client.client.speak("switching to english", 10)
                CommonParameter._already_answered = True
            elif CommonParameter._userInput == "language changed to japanese":
                Sentence = self.rdmFunc.randomChoose(
                    ["Lets talk in japanese.",
                     "Lets continue in japanese.",
                     "If your preference is japanese, I can talk in japanese for you.",
                     "I will talk in japanese for you now",
                     "From now on lets talk in japanese for you",
                     "If you say so, japanese will be my language now."]
                )
                self.Dialogue.reply(Sentence, True, True, False)
                # self.vh_client.client.speak("switching to english", 10)
                CommonParameter._already_answered = True
            elif CommonParameter._userInput == "language changed to hindi":
                Sentence = self.rdmFunc.randomChoose(
                    ["Lets talk in hindi.",
                     "Lets continue in hindi.",
                     "If your preference is hindi, I can talk in hindi for you.",
                     "I will talk in hindi for you now",
                     "From now on lets talk in hindi for you",
                     "If you say so, hindi will be my language now."]
                )
                self.Dialogue.reply(Sentence, True, True, False)
                # self.vh_client.client.speak("switching to english", 10)
                CommonParameter._already_answered = True
            elif CommonParameter._userInput == "language changed to cantonese":
                Sentence = self.rdmFunc.randomChoose(
                    ["Lets talk in cantonese.",
                     "Lets continue in cantonese.",
                     "If your preference is cantonese, I can talk in cantonese for you.",
                     "I will talk in cantonese for you now",
                     "From now on lets talk in cantonese for you",
                     "If you say so, cantonese will be my language now."]
                )
                self.Dialogue.reply(Sentence, True, True, False)
                # self.vh_client.client.speak("switching to english", 10)
                CommonParameter._already_answered = True
            ### korean added by nidhi###
            elif CommonParameter._userInput == "language changed to korean":
                Sentence = self.rdmFunc.randomChoose(
                    ["Lets talk in korean.",
                     "Lets continue in korean.",
                     "If your preference is korean, I can talk in korean for you.",
                     "I will talk in korean for you now",
                     "From now on lets talk in korean for you",
                     "If you say so, korean will be my language now."]
                )
                self.Dialogue.reply(Sentence, True, True, False)
                # self.vh_client.client.speak("switching to english", 10)
                CommonParameter._already_answered = True
            ### korean langauge ended here###
            elif CommonParameter._userInput == "switch to english":
                CommonParameter._already_answered = True
            elif CommonParameter._userInput == "language changed from the touch screen":
                self.vh_client.client.speak("language changed detected from the touch screen. Kindly repeat the sentence in the selected language.", 10)
                CommonParameter._already_answered = True
        #print CommonParameter._already_answered

        ###FOR AIA CHATBOT###
        #if not('*aia_listener*' in CommonParameter._userInput):
        #   temp = CommonParameter._userInput
        #   if "remove" in temp:
        #       temp = temp.replace("remove", "remit")
        #   if "check" in temp:
        #       temp = temp.replace("check", "cheque")
        #   if "cash back" in temp:
        #       temp = temp.replace("cash back", "cashback")
        # AIAChatbot_response =  self.AIAchatbot.get_response(CommonParameter._userInput)
        # AIAChatbot_response = str(AIAChatbot_response)
        # print("AIA Chatbot: ", AIAChatbot_response)
        #
        #    # Check for validity of AIA answers
        #    if AIAChatbot_response in open('AIA_Valid_Answers.txt').read():
        #        print "Valid AIA answer: \n"
        #        print(AIAChatbot_response)
        #        ansAIA = AIAChatbot_response.split('#AIA#')
        #        if (len(ansAIA) == 3):
        #            AIAChat_response = self.AIA_Chatresponse_replace(ansAIA[0])
        #            CommonParameter.AIAYesResponse = self.AIA_Chatresponse_replace(ansAIA[1])
        #            CommonParameter.AIANoResponse = self.AIA_Chatresponse_replace(ansAIA[2])
        #            CommonParameter.AIAShortAnswer_Flag = True
        #        else:
        #            AIAChat_response = self.AIA_Chatresponse_replace(AIAChatbot_response)
        #        self.Dialogue.reply(AIAChat_response, True, True, False)
        #        CommonParameter._already_answered = True
        ###FOR AIA CHATBOT###

        if os.path.exists("C:\\ProgramData\\Anaconda2\\Lib\\site-packages\\googlesamples\\assistant\\grpc\\testfile.txt"):
            os.remove("C:\\ProgramData\\Anaconda2\\Lib\\site-packages\\googlesamples\\assistant\\grpc\\testfile.txt")

        if (len(CommonParameter._userInput.split()) > 3 or "what " in CommonParameter._userInput or "who " in CommonParameter._userInput or "you " in CommonParameter._userInput or "your " in CommonParameter._userInput)and CommonParameter._already_answered==False:
            print "going to invoke google assitant"
            t = threading.Thread(target=self.QA.sent_proc.google_assistant_thread,args=(CommonParameter._userInput,))#yasir
            print "trying to start thread"
            t.start()
            print "success in thread start"
            CommonParameter._google_assistant_invoked=True
            print "_google_assistant_invoked"

        #self.QA.sent_proc.google_assistant_thread(CommonParameter._userInput)
        if CommonParameter._userInput.count(" ")>15: # check if the speech input is too long
            self.answer_sent.append("Please speak short sentences")
        # #To read from image --- Manoj
        # if "can you read" in CommonParameter._userInput:
        #     #print "Invoke Reading Module"
        #     Read_Sentence = self.QA.sent_proc.Read_from_Image()
        #     self.vh_client.client.speak(Read_Sentence,10)
        #     CommonParameter._already_answered=True
        # if CommonParameter.reportUser:
        #     print "Report User: ",CommonParameter.reportUserNum
        #     self.answer_sent.append("You are the number "+str(CommonParameter.reportUserNum)+" people I have ever met")
        #     CommonParameter.reportUser=False

        #Action Recognition --- Manoj
        if ("what am i doing" in CommonParameter._userInput) or ("what actions do you see" in CommonParameter._userInput) or ("what gestures do you see" in CommonParameter._userInput) or ("what action do you see" in CommonParameter._userInput) or ("what gesture do you see" in CommonParameter._userInput):
            time.sleep(3)
            Act_pred_file = open("C:\\xampp\\htdocs\\Reader\\Action_predictions.txt", "r")
            actions = list(Act_pred_file)
            Act_pred_file.close()
            Act_Sen = ', '.join(actions)
            print(Act_Sen)
            Reply_Sentence = self.rdmFunc.randomChoose(
                ["I can see the following actions " + Act_Sen,
                 "I need not be right, but my best guess of actions would be " + Act_Sen, \
                 "I think you are doing these actions " + Act_Sen, "I can detect the following actions " + Act_Sen])
            if ("gesture" in CommonParameter._userInput) or ("gestures" in CommonParameter._userInput):
                Reply_Sentence = self.rdmFunc.randomChoose(
                    ["I can see the following gestures " + Act_Sen,
                     "I need not be right, but my best guess of gestures would be " + Act_Sen, \
                     "I think you are doing these gestures " + Act_Sen, "I can detect the following gestures " + Act_Sen])

            #print(Reply_Sentence)
            #self.vh_client.client.speak(Reply_Sentence, 10)
            #time.sleep(2)
            #Add_Sentence = self.rdmFunc.randomChoose(
            #    ["Correct me if I am wrong",
            #     "Am I right or wrong", \
            #     "Was my guess correct"])

            #Reply_Sentence = Reply_Sentence + ". " + Add_Sentence
            Reply_Sentence = Reply_Sentence + ". "
            with open("C:\\xampp\\htdocs\\Reader\\nadine_app.txt", "a") as myfile:
                myfile.write(str(datetime.datetime.now().strftime("%a, %d %B %Y %I:%M:%S")) + " ### Nadine**" + Reply_Sentence + "\n")
            #self.vh_client.client.speak(Reply_Sentence, 10)
            self.Dialogue.reply(Reply_Sentence, True, True, False)

            CommonParameter._already_answered = True

        #Object Recognition --- Manoj, Fang Zhiwen
        if ("what objects do you " in CommonParameter._userInput) or  ("what object do you " in CommonParameter._userInput) or  ("name the objects" in CommonParameter._userInput) or ("do you recognize object" in CommonParameter._userInput) or ("do you see object" in CommonParameter._userInput) or ("do you detect object" in CommonParameter._userInput):
            time.sleep(2)
            Obj_pred_file = open("C:\\xampp\\htdocs\\Reader\\Object_predictions.txt", "r")
            objects = list(Obj_pred_file)
            Obj_pred_file.close()
            obj_dict = {}
            for obj in objects:
                if obj in obj_dict.keys():
                    obj_dict[obj] =  obj_dict[obj] + 1
                else:
                    obj_dict[obj] = 1

            Obj_Sen = ''
            for k, v in obj_dict.items():
                if k.rstrip() != "person":
                    print(k, 'corresponds to', v)
                    Obj_Sen = Obj_Sen + ", " + str(v) + " " + k.rstrip()
            #Obj_Sen = ', '.join(objects)
            print(Obj_Sen)
            Reply_Sentence = self.rdmFunc.randomChoose(
                ["I can see the following objects " + Obj_Sen,
                 "I need not be right, but my best guess of objects would be " + Obj_Sen, \
                 "I can detect the following objects around me " + Obj_Sen, "The following objects are around me " + Obj_Sen, "I can recognize these objects " + Obj_Sen])
            #self.vh_client.client.speak(Reply_Sentence, 10)

            #Add_Sentence = self.rdmFunc.randomChoose(
            #    ["Correct me if I am wrong",
            #     "Am I right or wrong", \
            #     "Was my guess correct"])

            #Reply_Sentence = Reply_Sentence + ". " + Add_Sentence
            Reply_Sentence = Reply_Sentence + ". "
            with open("C:\\xampp\\htdocs\\Reader\\nadine_app.txt", "a") as myfile:
                myfile.write(str(datetime.datetime.now().strftime("%a, %d %B %Y %I:%M:%S")) + " ### Nadine**" + Reply_Sentence + "\n")
            #self.vh_client.client.speak(Reply_Sentence, 10)
            self.Dialogue.reply(Reply_Sentence, True, True, False)
            CommonParameter._already_answered = True

        # Person Detection --- Fang Zhiwen
        if ("how many people do you see" in CommonParameter._userInput) or (
                "how many persons do you see" in CommonParameter._userInput) or (
                "how many person do you see" in CommonParameter._userInput):
            time.sleep(2)
            Obj_pred_file = open("C:\\xampp\\htdocs\\Reader\\Object_predictions.txt", "r")
            objects = list(Obj_pred_file)
            Obj_pred_file.close()
            obj_dict = {}
            for obj in objects:
                if obj in obj_dict.keys():
                    obj_dict[obj] = obj_dict[obj] + 1
                else:
                    obj_dict[obj] = 1

            Obj_Sen = ''
            for k, v in obj_dict.items():
                if k.rstrip() == "person":
                    print(k, 'corresponds to', v)
                    Obj_Sen = Obj_Sen + ", " + str(
                        v - 1) + " " + k.rstrip()  # minus 1 because the robot will be detected
            # Obj_Sen = ', '.join(objects)
            print(Obj_Sen)
            Reply_Sentence = self.rdmFunc.randomChoose(
                ["I can see " + Obj_Sen,
                 "I need not be right, but my best guess would be " + Obj_Sen, \
                 "I can detect " + Obj_Sen])
            # self.vh_client.client.speak(Reply_Sentence, 10)

            #Add_Sentence = self.rdmFunc.randomChoose(
             #   [  # "Correct me if I am wrong",
             #       "Am I right or wrong"  # , \
             #       # "Was my guess correct"
            #  ])

            #Reply_Sentence = Reply_Sentence + ". " + Add_Sentence
            Reply_Sentence = Reply_Sentence + ". "
            with open("C:\\xampp\\htdocs\\Reader\\nadine_app.txt", "a") as myfile:
                myfile.write(str(datetime.datetime.now().strftime("%a, %d %B %Y %I:%M:%S")) + " ### Nadine**" + Reply_Sentence + "\n")
            #self.vh_client.client.speak(Reply_Sentence, 10)
            self.Dialogue.reply(Reply_Sentence, True, True, False)
            CommonParameter._already_answered = True

        # Small Object Recognition using HD web camera --- Fang Zhiwen
        if (("what is this" in CommonParameter._userInput) or (
                "what is it" in CommonParameter._userInput)) and ("hand" not in CommonParameter._userInput):
            time.sleep(2)
            Obj_pred_file = open("C:\\xampp\\htdocs\\Reader\\Object_predictions_web_camera.txt", "r")
            objects = list(Obj_pred_file)
            Obj_pred_file.close()
            obj_dict = {}
            for obj in objects:
                if obj in obj_dict.keys():
                    obj_dict[obj] = obj_dict[obj] + 1
                else:
                    obj_dict[obj] = 1

            Obj_Sen = ''
            for k, v in obj_dict.items():
                if k.rstrip() != "person":
                    print(k, 'corresponds to', v)
                    Obj_Sen = Obj_Sen + ", " + str(v) + " " + k.rstrip()
            # Obj_Sen = ', '.join(objects)
            print(Obj_Sen)
            Reply_Sentence = self.rdmFunc.randomChoose(
                ["I can see " + Obj_Sen,
                "It would be " + Obj_Sen, \
                "This is " + Obj_Sen])
            # self.vh_client.client.speak(Reply_Sentence, 10)

            #Add_Sentence = self.rdmFunc.randomChoose(
            #    ["Correct me if I am wrong",
            #    "Am I right or wrong"])

            #Reply_Sentence = Reply_Sentence + ". " + Add_Sentence
            with open("C:\\xampp\\htdocs\\Reader\\nadine_app.txt", "a") as myfile:
                myfile.write(str(datetime.datetime.now().strftime("%a, %d %B %Y %I:%M:%S")) + " ### Nadine**" + Reply_Sentence + "\n")
            #self.vh_client.client.speak(Reply_Sentence, 10)
            self.Dialogue.reply(Reply_Sentence, True, True, False)
            CommonParameter._already_answered = True

        # Hand-held Object Recognition(left hand)--- Fang Zhiwen
        if ("in my hand" in CommonParameter._userInput):
            time.sleep(2)
            objects = []
            for checkFile in range(1, 100):
                Obj_pred_file = open("C:\\xampp\\htdocs\\Reader\\leftHandheld_Object_predictions.txt", "r")
                objects = list(Obj_pred_file)
                Obj_pred_file.close()
                if objects is not None:
                    break

            for checkFile in range(1, 100):
                Obj_pred_file = open("C:\\xampp\\htdocs\\Reader\\rightHandheld_Object_predictions.txt", "r")
                objects = list(Obj_pred_file)
                Obj_pred_file.close()
                if objects is not None:
                    break

            if objects:
                Obj_Sen = ', '.join(objects)
                print(Obj_Sen)
                Reply_Sentence = self.rdmFunc.randomChoose(
                    ["Yes, I can see a " + Obj_Sen,
                     "Yes, I think it is a " + Obj_Sen])
            else:
                Reply_Sentence = "I can not see any thing in your hand"
                #Reply_Sentence = self.rdmFunc.randomChoose(
                #    ["I can not see any thing in your hand",
                #     "I can not see it clearly. Please move it closer",
                #     "I do not known this object. I am in the process of learning more information"])

            with open("C:\\xampp\\htdocs\\Reader\\nadine_app.txt", "a") as myfile:
                myfile.write(str(datetime.datetime.now().strftime("%a, %d %B %Y %I:%M:%S")) + " ### Nadine**" + Reply_Sentence + "\n")
            #self.vh_client.client.speak(Reply_Sentence, 10)
            self.Dialogue.reply(Reply_Sentence, True, True, False)
            CommonParameter._already_answered = True
        # Hand-held Object Recognition(left hand)--- Fang Zhiwen
        if ("in my left hand" in CommonParameter._userInput):
            time.sleep(2)

            objects = []
            for checkFile in range(1, 100):
                Obj_pred_file = open("C:\\xampp\\htdocs\\Reader\\leftHandheld_Object_predictions.txt", "r")
                objects = list(Obj_pred_file)
                Obj_pred_file.close()
                if objects is not None:
                    break


            if objects:
                Obj_Sen = ', '.join(objects)
                print(Obj_Sen)
                Reply_Sentence = self.rdmFunc.randomChoose(
                    ["I can see a " + Obj_Sen + " in your left hand",
                    "I think this is a " + Obj_Sen])
            else:
                Reply_Sentence = self.rdmFunc.randomChoose(
                    ["I can not see any thing in your hand",
                    "I can not see it clearly. Please move it closer",
                    "I do not known this object. I am in the process of learning more information"])
            # self.vh_client.client.speak(Reply_Sentence, 10)

            # Add_Sentence = self.rdmFunc.randomChoose(
            #   ["Correct me if I am wrong",
            #    "Am I right or wrong", \
            #    "Was my guess correct"])

            # Reply_Sentence = Reply_Sentence + ". " + Add_Sentence
            with open("C:\\xampp\\htdocs\\Reader\\nadine_app.txt", "a") as myfile:
                myfile.write(str(datetime.datetime.now().strftime("%a, %d %B %Y %I:%M:%S")) + " ### Nadine**" + Reply_Sentence + "\n")
            #self.vh_client.client.speak(Reply_Sentence, 10)
            self.Dialogue.reply(Reply_Sentence, True, True, False)
            CommonParameter._already_answered = True

        # Hand-held Object Recognition (right hand) --- Fang Zhiwen
        if ("in my right hand" in CommonParameter._userInput):
            time.sleep(2)

            objects = []
            for checkFile in range(1, 100):
                Obj_pred_file = open("C:\\xampp\\htdocs\\Reader\\rightHandheld_Object_predictions.txt", "r")
                objects = list(Obj_pred_file)
                Obj_pred_file.close()
                if objects is not None:
                    break

            if objects:
                Obj_Sen = ', '.join(objects)
                print(Obj_Sen)
                Reply_Sentence = self.rdmFunc.randomChoose(
                    ["I can see a " + Obj_Sen + " in your right hand",
                    "I think this is a " + Obj_Sen])
            else:
                Reply_Sentence = self.rdmFunc.randomChoose(
                    ["I can not see any thing in your hand",
                    "I can not see it clearly. Please move it closer",
                    "I do not known this object. I am in the process of learning more information"])
            # self.vh_client.client.speak(Reply_Sentence, 10)

            # Add_Sentence = self.rdmFunc.randomChoose(
            #   ["Correct me if I am wrong",
            #    "Am I right or wrong", \
            #    "Was my guess correct"])

            # Reply_Sentence = Reply_Sentence + ". " + Add_Sentence
            with open("C:\\xampp\\htdocs\\Reader\\nadine_app.txt", "a") as myfile:
                myfile.write(str(datetime.datetime.now().strftime("%a, %d %B %Y %I:%M:%S")) + " ### Nadine**" + Reply_Sentence + "\n")
            #self.vh_client.client.speak(Reply_Sentence, 10)
            self.Dialogue.reply(Reply_Sentence, True, True, False)
            CommonParameter._already_answered = True


        # Gender, Age and Ethnicity Estimation --- Manoj
        if ("what is my age" in CommonParameter._userInput) or ("how old am i" in CommonParameter._userInput) or ("how old do i look" in CommonParameter._userInput) or ("guess my age" in CommonParameter._userInput):
            if CommonParameter._userAge == 'unknown':
                Reply_Sentence = "I am not able to determine your age"
            else:
                Reply_Sentence = self.rdmFunc.randomChoose(["I believe you are in the age group of " + CommonParameter._userAge, "My best guess would be " + CommonParameter._userAge, \
                                                      "I think you could be between " + CommonParameter._userAge])
                #Reply_Sentence = self.rdmFunc.randomChoose(["I believe you are in the age group of", "My best guess would be ","I think you could be between " ])
                #Reply_Sentence = "I believe you are in the age group of " + CommonParameter._userAge
            #self.vh_client.client.speak(Reply_Sentence, 10)
            self.Dialogue.reply(Reply_Sentence, True, True, False)
            CommonParameter._already_answered = True

        if ("what is my gender" in CommonParameter._userInput):
            if CommonParameter._userAge == 'unknown':
                Reply_Sentence = "I am not able to determine your gender"
            else:
                Reply_Sentence = self.rdmFunc.randomChoose(["You are a " + CommonParameter._userGender, "I might be wrong but i think you are a" + CommonParameter._userGender, \
                                                      "My best guess would be a" + CommonParameter._userGender])
            #Reply_Sentence = "You are " + CommonParameter._userGender
            #self.vh_client.client.speak(Reply_Sentence, 10)
            self.Dialogue.reply(Reply_Sentence, True, True, False)
            CommonParameter._already_answered = True

        if "what is my ethnicity" in CommonParameter._userInput:
            if CommonParameter._userAge == 'unknown':
                Reply_Sentence = "At this point, I cannot guess your gender"
            else:
                Reply_Sentence = self.rdmFunc.randomChoose(["You look like a " + CommonParameter._userEthnicity, "I might be wrong but i think you are a" + CommonParameter._userEthnicity, \
                                                      "My best guess would be a" + CommonParameter._userEthnicity])
            #Reply_Sentence = "You look like " + CommonParameter._userEthnicity
            #self.vh_client.client.speak(Reply_Sentence, 10)
            self.Dialogue.reply(Reply_Sentence, True, True, False)
            CommonParameter._already_answered = True

        #To read from image --- Manoj
        if "can you read my card" in CommonParameter._userInput:
            #print "Invoke Reading Module"
            #self.vh_client.client.speak("please place the card in front of the camera", 10)
            self.Dialogue.reply("please place the card in front of the camera", True, True, False)
            read_type = 1
            Read_Sentence, CommonParameter._userName = self.QA.sent_proc.Read_from_Image(read_type)
            #self.vh_client.client.speak(Read_Sentence,10)
            self.Dialogue.reply(Read_Sentence, True, True, False)
            CommonParameter._already_answered=True

        if "can you receive this parcel" in CommonParameter._userInput:
            #print "Invoke Reading Module"
            #self.vh_client.client.speak("please place the parcel in front of the camera", 10)
            self.Dialogue.reply("please place the parcel in front of the camera", True, True, False)
            read_type = 2
            Read_Sentence, dummy = self.QA.sent_proc.Read_from_Image(read_type)
            #self.vh_client.client.speak(Read_Sentence,10)
            self.Dialogue.reply(Read_Sentence, True, True, False)
            CommonParameter._already_answered=True

        if "read this input" in CommonParameter._userInput:
            #print "Invoke Reading Module"
            #self.vh_client.client.speak("please place the input in front of the camera", 10)
            self.Dialogue.reply("please place the input in front of the camera", True, True, False)
            read_type = 0
            Read_Sentence, dummy = self.QA.sent_proc.Read_from_Image(read_type)
            #self.vh_client.client.speak(Read_Sentence,10)
            self.Dialogue.reply(Read_Sentence, True, True, False)
            CommonParameter._already_answered=True

        if ("show me pictures of" in CommonParameter._userInput) or ("show me picture of" in CommonParameter._userInput) or ("show me the pictures of" in CommonParameter._userInput) or ("show me the picture of" in CommonParameter._userInput):

            try:
                if("pictures of" in CommonParameter._userInput):
                    a,b=CommonParameter._userInput.split('pictures of')
                elif("picture of" in CommonParameter._userInput):
                    a,b=CommonParameter._userInput.split('picture of')
                self.QA.sent_proc.search_pictures([b],[''])
                #self.vh_client.client.speak("here are some pictures of "+b, 10)
                self.Dialogue.reply("here are some pictures of "+b, True, True, False)
                CommonParameter._already_answered = True

            except:
                #self.vh_client.client.speak("kindly repeat the sentence", 10)
                self.Dialogue.reply("kindly repeat the sentence", True, True, False)
                CommonParameter._already_answered = True
        ############# get complete answer###################

        if self.question!=None:
            CommonParameter.knowledgeSent=self.QA.sent_proc.getCompleteAnswer(self.question,CommonParameter._userInput)
            self.question=None
        else:
            CommonParameter.knowledgeSent=None

        if self.becassineFlag:
            return
        ################# Get Input Emotions #######################
        self.emotion=self.EmoRecognition.parse(CommonParameter._userInput)
        _emo=copy(self.emotion)
        if _emo==None:
            _emo="None 0.5"
        ############# store input events###################
        if CommonParameter.knowledgeSent!=None:
            self.QA.getAttr(CommonParameter.knowledgeSent,CommonParameter._userName,_emo,CommonParameter._mood.getMoodStr())
        else:
            self.QA.getAttr(CommonParameter._userInput,CommonParameter._userName,_emo,CommonParameter._mood.getMoodStr())
        self.QA.storeEvent()
        CommonParameter._lastUserInput=CommonParameter._userInput # save user input
        print "add memory"

    def AIA_Chatresponse_replace(self,resp):
        resp = resp.replace("a i a", "Ae I A")
        resp = resp.replace("A I A", "Ae I A")
        resp = resp.replace("aia", "Ae I A")
        resp = resp.replace("AIA", "Ae I A")  # Ae I A
        resp = resp.replace("N I R C", "NRIC")  # NRIC
        resp = resp.replace("NIRC", "NRIC")
        resp = resp.replace("N R I C", "NRIC")
        return resp

    def updateEmotion(self):
        if self.becassineFlag:
            return
        if self.emotion:
            print "##########################"
            print "The recognized emotion is : "+self.emotion
            print "##########################"
            CommonParameter.recogEmo=self.emotion

            number=0
            while number<20:
                if CommonParameter._emotion.intensity<0.01:
                    break
                number+=1
                time.sleep(0.1)

            self.Dialogue._emotion=CommonParameter._emotion
            self.Dialogue._mood=CommonParameter._mood
            CommonParameter._emotion=Emotion()
        else:
            print "##########################"
            print "No emoiton recognized!!!"
            print "##########################"
            self.Dialogue._emotion=CommonParameter._emotion
            self.Dialogue._mood=CommonParameter._mood

    def askMemory(self):
        if self.memoryFlag and CommonParameter._already_answered==False:
            if self.becassineFlag:
                return False
            try:
                self.InputQ=self.QA.checkQ(CommonParameter._userInput)
                sentence,chatbotFlag=self.QA.getAnswer(CommonParameter._userInput,self.InputQ)
                if sentence!=None:
                    self.answer_sent.append(sentence)
                    if self.memoryFlag:
                        self.QA.getAttr(sentence,"Robot","None 0.5",CommonParameter._mood.getMoodStr())
                        self.QA.storeEvent()
                        print "add memory"
                if chatbotFlag and ((not self.InputQ) or sentence==None):
                    return False
                return True
            except:
                print sys.exc_info()[0]
                return False
        else:
            return False

    def askChatbot(self):
        try:
            if CommonParameter._already_answered==False:
                if CommonParameter.knowledgeSent:
                    sentence=self.Predefine.getAnswer(CommonParameter.knowledgeSent)
                    if sentence==None:
                        if ("you " in CommonParameter.knowledgeSent) or ("your " in CommonParameter.knowledgeSent) or ("we " in CommonParameter.knowledgeSent)or ("bye " in CommonParameter.knowledgeSent) or (len(CommonParameter.knowledgeSent.split())<=3):

                            sentence=self.chatbot.reply(CommonParameter.knowledgeSent)
                        else:
                            sentence="i have no idea"
                        # while not os.path.exists(
                        #         "C:\\Users\\IMI-User\\Anaconda2\\Lib\\site-packages\\googlesamples\\assistant\\grpc\\testfile.txt"):
                        #     time.sleep(0.3)
                        # with open(
                        #         "C:\\Users\\IMI-User\\Anaconda2\\Lib\\site-packages\\googlesamples\\assistant\\grpc\\testfile.txt") as f:
                        #     lines = f.readlines()
                        # sentences = [x.strip() for x in lines]  # self.Dialogue.news.online_search(CommonParameter._userInput)
                        # sentence = sentences[0]
                        # os.remove("C:\\Users\\IMI-User\\Anaconda2\\Lib\\site-packages\\googlesamples\\assistant\\grpc\\testfile.txt")
                else:
                    sentence=self.Predefine.getAnswer(CommonParameter._userInput)
                    if sentence==None:
                        if ("you " in CommonParameter._userInput) or ("your " in CommonParameter._userInput) or ("we " in CommonParameter._userInput)or ("bye " in CommonParameter._userInput) or (len(CommonParameter._userInput.split())<=3):

                            sentence=self.chatbot.reply(CommonParameter._userInput)
                        else:
                            sentence="i have no idea"
                        # while not os.path.exists(
                        #         "C:\\Users\\IMI-User\\Anaconda2\\Lib\\site-packages\\googlesamples\\assistant\\grpc\\testfile.txt"):
                        #     time.sleep(0.3)
                        # with open(
                        #         "C:\\Users\\IMI-User\\Anaconda2\\Lib\\site-packages\\googlesamples\\assistant\\grpc\\testfile.txt") as f:
                        #     lines = f.readlines()
                        # sentences = [x.strip() for x in lines]  # self.Dialogue.news.online_search(CommonParameter._userInput)
                        # sentence = sentences[0]
                        # os.remove("C:\\Users\\IMI-User\\Anaconda2\\Lib\\site-packages\\googlesamples\\assistant\\grpc\\testfile.txt")
                sentence=self.Dialogue.sent_proc.shortenSentence(sentence)
                print(sentence)
                print "self.Dialogue.sent_proc.isBadChatbotAnswer(sentence) = ", self.Dialogue.sent_proc.isBadChatbotAnswer(sentence)
                print "CommonParameter._google_assistant_invoked = ", CommonParameter._google_assistant_invoked
                if self.Dialogue.sent_proc.isBadChatbotAnswer(sentence) and CommonParameter._google_assistant_invoked==True:
                    ############# Search for online news##############
                    print "trying to get answer from google"
                    begin_time=time.time()
                    print "begin_time = ", begin_time
                    timeout=False
                    while not os.path.exists("C:\\ProgramData\\Anaconda2\\Lib\\site-packages\\googlesamples\\assistant\\grpc\\testfile.txt"):
                        time.sleep(0.2)
                        print("ga loop")
                        if time.time()>begin_time+15:
                            timeout=True
                            print("time out")
                            break
                    if timeout==False:
                        print "time out falsee"
                        with open("C:\\ProgramData\\Anaconda2\\Lib\\site-packages\\googlesamples\\assistant\\grpc\\testfile.txt") as f:
                            lines = f.readlines()
                        sentences=[x.strip() for x in lines]#self.Dialogue.news.online_search(CommonParameter._userInput)
                        sentence=sentences[0]
                        ###site name replace###
                        print "before removing website name"
                        print sentence
                        sentence = sentence.replace('according to', '')
                        sentence = re.sub(
                            r'(?:[A-Z|a-z0-9](?:[a-z0-9-]{0,61}[a-z0-9])?\.)+[a-z0-9][a-z0-9]{0,61}[a-z0-9]', '',
                            sentence)
                        sentence = sentence.replace('Wikipedia', '')
                        sentence = sentence.replace('on the website', '')
                        sentence = sentence.replace('and the website', '')
                        sentence = sentence.replace('from the website', '')
                        sentence = sentence.replace('they say', '')
                        print "after removing website name"
                        print sentence
                        ###site name replace###

                        sentence=sentence.lower()
                        sentence= sentence.replace("google assistant","Nadine")
                        # sentence = sentence.replace("Google Assistant", "Nadine")
                        # sentence = sentence.replace("Google assistance", "Nadine")
                        sentence = sentence.replace("google assistance", "Nadine")

                        os.remove("C:\\ProgramData\\Anaconda2\\Lib\\site-packages\\googlesamples\\assistant\\grpc\\testfile.txt")
                    else:
                        sentence=None
                    ############# Search for online news##############
                    print "sentence = ", sentence
                    if sentence==None:
                        sentence=self.rdmFunc.randomChoose(OKWord)
                else:
                    sentence=self.Dialogue.sent_proc.clearChatBotAnswer(sentence)

                self.checkReplyComplete(sentence)

                if len(sentence)==0:
                    sentence=self.rdmFunc.randomChoose(["All right","OK","Nice"])
                if sentence[-1]==".":
                    sentence=sentence[:-1]
                self.answer_sent.append(sentence)
                if self.becassineFlag:
                    return
                self.QA.getAttr(sentence,"Robot","None 0.5",CommonParameter._mood.getMoodStr())
                self.QA.storeEvent()
                print "add memory"
        except:
            print sys.exc_info()[0]

    def checkReplyComplete(self,sentence):
        ReplyQ=None
        if "." in sentence:
            sents=sentence.split(".")
            for s in sents:
                if self.QA.checkQ(s):
                    ReplyQ=True
                    break
        else:
            ReplyQ=self.QA.checkQ(sentence)
        if ReplyQ:
            self.question=sentence


    def generateQuestion(self):
        if self.becassineFlag:
            return
        self.question=None
        if (not self.InputQ):
            if self.num_iter>=self.questionFreq:
                ques=self.userQ.pop()
                self.question=ques
                if ques!=None:
                    self.answer_sent.append(ques)
                    # set topic for chatbot
                    self.chatbot.reply(ques)
                    if self.memoryFlag:
                        self.QA.getAttr(ques,"Robot","None 0.5",CommonParameter._mood.getMoodStr())
                        self.QA.storeEvent()
                        print "add memory"
                    self.num_iter=0
                    self.numberQuestion-=1

    def questionFlag(self):
        if self.newFlag and self.numberQuestion>0:
            self.questionFreq=2
            return True
        # if self.Dialogue.getQuestionFlag():
        #     # set question frequency by arousal level
        #     self.questionFreq=self.Dialogue.getQuestionFreq()
        #     return True
        return False

    def addQuestion(self):
        ############## ask questions##############
        if self.questionFlag():
            self.generateQuestion()
        ############## Make Response ##############
        answer=". ".join(self.answer_sent)
        self.respond(answer)
        self.num_iter+=1
        self.start_interaction=True
        CommonParameter._userInput=''


if __name__=="__main__":
    Main()
