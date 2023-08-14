__author__ = 'Zhang Juzheng'
import findTime
import time
from datetime import datetime
import re
import os
#import nltk
from textblob import TextBlob,Word
import enchant
import cPickle as pickle
import random
#-----------------------------------------------
#Add required modules for reading from images
#-----------------------------------------------
import numpy as np
import cv2
from google.cloud import vision
from google.cloud.vision import types
import io
import smtplib
import sys
import csv
import subprocess
# UserGender={"Aryel":"male",
#             "Cindy":"female",
#             "Daniel":"male",
#             "James":"male",
#             "Jason":"male",
#             "Mariko":"female",
#             "Nadia":"female"}



def processSentence(sentence):
    sentence=re.sub(r"'ve"," have",sentence)
    sentence=re.sub(r"'m"," am",sentence)
    sentence=re.sub(r"'d"," would",sentence)
    sentence=re.sub(r"'s","",sentence)
    sentence=re.sub(r"'t"," not",sentence)
    sentence=re.sub(r"'re"," are",sentence)
    sentence=re.sub(r"danielle","daniel",sentence)
    sentence=re.sub(r"daniel thalmann","daniel",sentence)
    sentence=re.sub(r"daniel thalman","daniel",sentence)
    sentence=re.sub(r"nadia thalmann","nadia",sentence)
    sentence=re.sub(r"nadia thalman","nadia",sentence)
    sentence=re.sub(r"jams","james",sentence)
    sentence=re.sub(r"gems","james",sentence)
    sentence=re.sub(r"aruba","rubha",sentence)
    sentence=re.sub(r"booba","rubha",sentence)
    sentence=re.sub(r"ruba","rubha",sentence)
    sentence=re.sub(r"rupa","rubha",sentence)
    sentence=re.sub(r"venassa","vanessa",sentence)
    sentence=re.sub(r"parents","mother and father",sentence)
    sentence=re.sub(r"parent","mother and father",sentence)
    sentence=re.sub(r'''[,\.;!"\(\)\{\}\+~/\?&\[\]\$\|\\]+''',"",sentence)

    #sentence=re.sub(r'''[,\.;!\(\)\{\}\+~/\?&\[\]\$\|]+''',"",sentence)
    return sentence

class Gender:
    def __init__(self):
        self.loadGender()

    def loadGender(self):
        file=open("gender.pickle","rb")
        self.userGender=pickle.load(file)
        file.close()

    def saveGender(self):
        file=open("gender.pickle","wb")
        pickle.dump(self.userGender,file)
        file.close()

UserGender=Gender()


class randomFunc:
    def __init__(self):
        pass

    def randomChoose(self,List):
        '''randomly choose an element in a list'''
        length=len(List)
        if length>0:
            rand=random.randint(0,length-1)
            return List[rand]
        return None

    def randProb(self,prob):
        '''prob should be larger than 0 and smaller than 1'''
        rand=random.random()
        if rand<=prob:
            return True
        return False

    def randDouble(self,upperLimit):
        '''generate random double between 0 and the upperLimit'''
        if upperLimit<0 or upperLimit>1:
            raise Exception("The range for random number should be between 0 and 1")
        rand=random.random()
        return round(rand*upperLimit,2)


class timeUtils:
    def __init__(self):
        self.timeAnalyser=findTime.findTime()
        self.updateCurrentTime()

    def updateCurrentTime(self):
        now=datetime.today()
        now=time.asctime(now.timetuple())
        tags=now.split()
        self.date="-".join([tags[2],tags[1],tags[4]])
        self.weekday=tags[0]
        self.socialTime=self.getSocialTime(tags[3].split(":")[0])

    def getStringDate(self,datestr):
        now=self.timeAnalyser.getQueryDayTime(datestr)
        if now==None:
            return None
        tags=now.split()
        date="-".join([tags[2],tags[1],tags[4]])
        return date



    def getSocialTime(self,hour):
        hour=int(hour)
        if hour>0 and hour<=12:
            return "Morning"
        elif hour>12 and hour<=18:
            return "Afternoon"
        else:
            return "Night"

    def getSentenceTime(self,sentence):
        if sentence=="":
            return "None"
        sentence=sentence.lower()
        sentence=processSentence(sentence)
        gottime=self.timeAnalyser.getQueryDayTime(sentence)
        tags=gottime.split()
        weekday=tags[0]
        socialTime="None"
        return (weekday,socialTime)

def Employee_Dictionary():
    Dict = []
    with open('G:\\IMI-PROJECTS\\i2p_Nadine_Robot\\development\\i2p_interaction\\i2p_dialog_manager\\Employee_Database.csv', 'rb') as f:
        reader = csv.reader(f)
        for row in reader:
            Dict.append(row)
            #print row
    return Dict

class sentenceUtils:
    def __init__(self):
        self._Emp_Dict = Employee_Dictionary()
        self.stopverbs=pickle.load(open('stop_verbs.pickle','rb'))
        self.stopwords=pickle.load(open('stop_words.pickle','rb'))
        #self.initTextBlob()
        self._random=randomFunc()
        self.dic = enchant.Dict("en_US")
        self.changeDict={"second":{"i":"you",
                                     "am":"are",
                                     "was":"were",
                                     "my":"your"},
                         "third":{"male":{"i":"he",
                                   "am":"is",
                                   "my":"his",
                                   "have":"has"},
                                  "female":{"i":"she",
                                   "am":"is",
                                   "my":"her",
                                   "have":"has"}
                                  },
                         "second_to_first":{"you":"i",
                                            "are":"am",
                                            "were":"was",
                                            "your":"my"}}



    def shortenSentence(self,sentence):
        if sentence.count(".")+sentence.count(",")>10:
            if "." in sentence:
                res=sentence.split(".")[0]
                return res
            elif "?" in sentence:
                res=sentence.split("?")[0]
                return res
        if sentence.lower() in ["too much recursion in aiml"]:
            sentence="Could you tell me more?"
        return sentence

    def changeForSpeaking(self,sentence):
        sent=TextBlob(sentence)
        words=sent.tokens
        if "ntu" in words:
            sentence=self.substitute(sentence,"ntu","n t u")
        if "imi" in words:
            sentence=self.substitute(sentence,"imi","i m i")
        if "0" in words:
            sentence=self.substitute(sentence,"0","zero")



        return sentence



    def isBadChatbotAnswer(self,sentence):
        sentence=processSentence(sentence.lower())
        # sub_words=["hmmm","er","mhm","hmm","okeam","ur","hm","ummm","umm","uh","um",\
        #            "hmmmm","ummmm","whoa","gee","aha","ah"]
        bad_answers=[
                   "i will try my web search",
                   "tell me more",
                   "what else",
                   "really",
                   "it sounds interesting",
                   "could you tell me more about that",
                   "now you can ask me",
                   "do you think I would like",
                   "what do you like best about",
                   "it was at time index",
                   "i don not know that about you",
                   "i don't know that about you",
                   "i don't know the answer",
                   "i don not know the answer",
                   "i have no idea",
                   "i am giving you my full attention",
                   "i am working for you",
                   "i have been waiting for you"
                   ]
        # if len(sentence)==0 and sentence in sub_words:
        #     return True
        if any(sentence.startswith(ans) for ans in bad_answers):
            return True
        # for ans in bad_answers:
        #     if sentence.startswith(ans):
        #         return True
        return False

    def clearChatBotAnswer(self,sentence):
        sentence=sentence.lower()
        sent=TextBlob(sentence)
        sents=[word.string for word in sent.tokens]
        sub_words=["hmmm","er","mhm","hmm","okeam","ur","hm","ummm","umm","uh","um",\
                   "hmmmm","ummmm","whoa","gee","aha","ah"]
        common=list(set(sub_words) & set(sents))
        if len(common)>0:
            to_word=self._random.randomChoose(["okea","alright","nice","well"])
            sentence=self.substitute(sentence,common[0],to_word)
        return sentence


    # def getNouns(self,sentence,sentUser=None):
    #     sent=TextBlob(sentence)
    #     tags=sent.tags
    #     #ner_dict=self.getner(sentence)
    #     res=[]
    #     for w,_tag in tags:
    #         if w not in self.stopwords:
    #             if _tag in ("NN", "NNS", "NNP", "NNPS"):
    #                 res.append(w)
    #             elif _tag in ("VB", "VBD", "VBG", "VBN", "VBP", "VBZ"):
    #                 verb=self.lemmatize(w,_tag)
    #                 if verb not in self.stopverbs:
    #                     res.append(w)
    #             # else:
    #             #     res.append(w)
    #     if sentUser!=None:
    #         user=sentUser.lower()
    #         if user in res:
    #             res.remove(user)
    #     if len(res)>0:
    #         result=" ".join(res)
    #         print "search cue is: "+result
    #         return result
    #     else:
    #         return None

    def getNouns(self,sentence,sentUser=None):
        sent=TextBlob(sentence.lower())
        tags=sent.tags
        #ner_dict=self.getner(sentence)
        res=[]
        filterWords=["weather","nadine","singapore","president","japan","china","'","swiss",
                     "s","thalmann","don","date","tokyo","usa","united states"]
        for w,_tag in tags:
            if (w not in self.stopwords) and (w not in filterWords):
                res.append(w)
        if sentUser!=None:
            user=sentUser.lower()
            if user in res:
                res.remove(user)
        if ("work" in res or "job" in res) and "current" not in "res":
            res.append("current")
        if len(res)>0:
            return " ".join(res)
        else:
            return None

    def lemmatize(self,word,tag):
        w=Word(word,tag)
        return w.lemma

    # def getner(self,userInput):
    #     ner=None
    #     if self.ner_client.connected:
    #         ner=self.ner_client.client.getNER(userInput)
    #     if len(ner)>0:
    #         return ner
    #     else:
    #         return None

    def substituteWord(self,word,newWord,str):
        if word in str:
            idx=str.find(word)
            idx2=idx+len(word)
            res=str[:idx]+newWord+str[idx2:]
            #print "res: "+res
            return res
        else:
            return str

    def removeWord(self,sentence):
        sent=TextBlob(sentence.lower())
        sents=[word.string for word in sent.tokens]
        remove_words=["yes","no"]
        for word in remove_words:
            if word==sents[0]:
                sentence=self.substitute(sentence,word,"")
        return sentence

    def checkInput(self,attrs):
        # do spell correction
        # userInput=userInput.lower()
        userInput=attrs[0].split("=")[1].lower()
        subwords=["jams","ngu","an tu"]
        userInput=self.substituteWord("jams","james",userInput)
        userInput=self.substituteWord("ngu","ntu",userInput)
        userInput=self.substituteWord("an tu","ntu",userInput)
        userInput=processSentence(userInput)
        attrs[0]="sentence="+userInput
        return userInput
        #self.blob_text=TextBlob(userInput)
        #ner_dict=self.getner(userInput)
        # tags=self.blob_text.tags
        # res=[]
        # for (w,_tag) in tags:
        #     w_res=w.string
        #     if _tag not in ("NN", "NNS", "NNP", "NNPS","PRP","PRP$"):
        #         if not self.dic.check(w_res):
        #             w_res=w.correct()
        #     res.append(w_res)
        #
        # res=" ".join(res)
        # attrs[0]="sentence="+res
        # return res


    def getSentenceState(self,sentence):
        if sentence=="":
            return "None"
        sentence=sentence.lower()
        sentence=processSentence(sentence)
        sent=TextBlob(sentence)
        tags=sent.tags
        if "going to" in sentence:
            tokens=[word.string for word in sent.tokens]
            pos1=tokens.index("going")-1
            pos2=tokens.index("to")+1
            former=tags[pos1][0]
            latter=tags[pos2][1]
            if former in ["be","am","is","was","are","were","been"] and latter=="VB":
                return "Future"
        for tag in tags:
            if tag == ('will', 'MD'):
                return "Future"
            elif tag[1] in ["VBD","VBN"]:
                return "Past"
            else:
                return "Present"


    def checkQuestion(self,TaggedSentence):
        #firstTag=TaggedSentence[0][1]
        if len(TaggedSentence)==0:
            return False,None
        firstWord=TaggedSentence[0][0]
        if len(TaggedSentence)>1:
            secondWord=TaggedSentence[1][0]
            secondTag=TaggedSentence[1][1]
        else:
            secondWord=""
            secondTag=""
        questionWord=["did","does","which","who","whom","when","where","is","are","was","were",\
                      "had","will","would","shall","should","can","could","may","might"]
        if firstWord in questionWord:
            #print "Q: ",sent
            return True,firstWord
        elif firstWord in ["do","have"] and (secondTag =="PRP" or secondTag.startswith("NN")):  # do you
            #print "Q: ",sent
            return True,firstWord
        elif firstWord in ["what"]: # how nice you are
            if secondTag not in ["JJ","DT","PRP"] and secondWord not in ["if"]:
                #print "Q: ",sent
                return True,firstWord
            else:
                return False,None
        elif firstWord in ["how"]: # how nice you are
            if secondTag not in ["JJ","DT","PRP"] or secondWord in ["much","many"]:
                #print "Q: ",sent
                return True,firstWord
            else:
                return False,None
        else:
            return False,None

    def isContain(self,wordList,candidates):
        idx=-1
        for word in candidates:
            if word in wordList:
                if idx==-1: idx=wordList.index(word)
                return (True,idx,word)
        return (False,-1,None)

    def isCompleteSentence(self,sentence):
        sentence=processSentence(sentence.lower())
        sent=TextBlob(sentence)
        tags=sent.tags
        subject=False
        verb=False
        sub_idx=-1
        verb_idx=-1
        idx=0
        for tag in tags:
            if tag[1] in ["NN", "NNS", "NNP", "NNPS","PRP"]:
                subject=True
                if sub_idx==-1: sub_idx=idx
            if tag[1] in ["VB", "VBD", "VBG", "VBN", "VBP", "VBZ"]:
                verb=True
                if verb_idx==-1: verb_idx=idx
            idx+=1
        if subject and verb:
            if sub_idx<verb_idx:
                return True
        return False

    def getCompleteAnswer(self,question,answer):
        beVerb=["be","am","is","was","are","were"]
        question=processSentence(question.lower())
        answer=processSentence(answer.lower())
        ques=TextBlob(question)
        quesWord=[word.string for word in ques.tokens]
        if len(quesWord)<2:
            return answer
        x1=quesWord[0] in ["what","who"]
        x2=quesWord[1] in beVerb
        if x1 and x2:
            flag=self.isCompleteSentence(answer)
            if not flag:
                resWord=quesWord[2:]
                resWord.append(quesWord[1])
                resWord.append(answer)
                resSent=" ".join(resWord)
                res=self.changeSecondToFirstPerson(resSent)
                return res

        x3=quesWord[0] in ["do","did","is","was","are","were","will","would","shall","should","can","could"]
        x4=quesWord[1] in ["you","your"]
        if x3 and x4:
            answerFlag=self.getSentOpinion(answer)
            if answerFlag!=None:
                resWord=[]
                resWord.append(quesWord[1])
                if (quesWord[0] not in ["do","did"]) or (not answerFlag):
                    resWord.append(quesWord[0])
                    if not answerFlag:
                        resWord.append("not")
                resWord.extend(quesWord[2:])
                resSent=" ".join(resWord)
                res=self.changeSecondToFirstPerson(resSent)
                return res

        return answer



    def changeToSecondPerson(self,sentence):
        sent=TextBlob(sentence.lower())
        tokens=[word.string for word in sent.tokens]
        res=[]
        for word in tokens:
            if word in self.changeDict["second"].keys():
                res.append(self.changeDict["second"][word])
            else:
                res.append(word)
        str=" ".join(res)
        return str

    def changeSecondToFirstPerson(self,sentence):
        sent=TextBlob(sentence.lower())
        tokens=[word.string for word in sent.tokens]
        res=[]
        for word in tokens:
            if word in self.changeDict["second_to_first"].keys():
                res.append(self.changeDict["second_to_first"][word])
            else:
                res.append(word)
        str=" ".join(res)
        return str

    def changeToThirdPerson(self,sentence,user):
        gender="male"
        if user in UserGender.userGender.keys():
            gender=UserGender.userGender[user]
        sent=TextBlob(sentence.lower())
        tokens=[word.string for word in sent.tokens]
        res=[]
        for word in tokens:
            if word in self.changeDict["third"][gender].keys():
                res.append(self.changeDict["third"][gender][word])
            else:
                res.append(word)
        str=" ".join(res)
        return str

    def transferThirdtoSecondPerson(self,sentence,userName):
        sent=TextBlob(sentence.lower())
        words=[word.string for word in sent.tokens]
        user=userName.lower()
        #print "sentence: "+sentence
        #print "user: " +user
        idx=0
        while user in words[idx:]:
            if idx==0:
                idx=words.index(user)
            else:
                idx=words.index(user,idx)
            words[idx]="you"
            if idx<len(words)-1 and words[idx+1] in ["is","was"]:
                words[idx+1]="are"

        for i in range(len(words)):
            word=words[i]
            if word in ["he","him","she"]:
                words[i]="you"
                if i<len(words)-1 and words[i+1] in ["is","was"]:
                    words[i+1]="are"
            elif word in ["his","her"]:
                words[i]="your"
            elif word in ["himself","herself"]:
                words[i]="yourself"

        res=" ".join(words)
        return res

    # def transferFirstPerson(self,tokens,userName):
    #     first=["i","me","my"]
    #     user=userName.lower()
    #     for word in first:
    #         if word in tokens:
    #             idx=tokens.index(word)
    #             tokens[idx]=user

    def getSentOpinion(self,sentence):
        _sent=TextBlob(sentence.lower())
        sent=[word.string for word in _sent.tokens]
        agree=["yes","ok","okea","nice","sure","of course","go ahead"]
        disagree=["no","not"]
        for word in disagree:
            if word in sent:
                return False
        for word in agree:
            if word in sent:
                return True
        return None


    def getOpinion(self,sentence,pleasure):
        opn=self.getSentOpinion(sentence)
        if opn==True:
            return True
        elif opn==False:
            return False
        if pleasure>=0:
            return True
        else:
            return False

    def replaceName(self,sentence,name,order=3):
        sent=TextBlob(sentence.lower())
        sentWords=[word.string for word in sent.tokens]
        if order==3:
            if "he" in sentWords:
                idx=sentWords.index("he")
                sentWords[idx]=name
                res=" ".join(sentWords)
                return res
        return None

    def substitute(self,sentence,from_word,to_word):
        if from_word in sentence:
            idx=sentence.find(from_word)
            length=len(from_word)
            res=sentence[:idx]+to_word+sentence[idx+length:]
            return res
        return sentence
    def google_assistant_thread(self,input_sentence):
        if os.path.exists("C:\\ProgramData\\Anaconda2\\Lib\\site-packages\\googlesamples\\assistant\\grpc\\ga0.wav"):
            os.remove("C:\\ProgramData\\Anaconda2\\Lib\\site-packages\\googlesamples\\assistant\\grpc\\ga0.wav")
        command = "tts.exe -f 1 -v 0 " + "\"" + input_sentence + "\"" + " -o C:\\ProgramData\\Anaconda2\\Lib\\site-packages\\googlesamples\\assistant\\grpc\\ga"
        print command
        os.system(command)  # silence 1 0.1 3% 1 3.0 3% trim 0 10
        #command = "python -m googlesamples.assistant.grpc.pushtotalk -i C:\\Users\\IMI-User\\Anaconda2\\Lib\\site-packages\\googlesamples\\assistant\\grpc\\ga0.wav -o C:\\Users\\IMI-User\\Anaconda2\\Lib\\site-packages\\googlesamples\\assistant\\grpc\\assistant_reply.wav"
        #os.system(command)

    #Function for Reading from images - Manoj
    def Read_from_Image(self,read_type):
        try:
            #Get read camera index from text file
            #read_file = open("C:\\Users\\IMI-User\\Downloads\\python-capture-device-list-master\\read_camera.txt", "r")
            image_name = os.path.abspath('.')
            read_file = open(os.path.join(image_name,'read_camera.txt'), "r")
            read_camera_index = read_file.read()
            read_file.close()
            read_camera_index = int(read_camera_index)
            print "In Reading Module"
            UserName = 'Unknown'
            #while (True):
            #   for i in range(3):
            #       print i
            #       cap = cv2.VideoCapture(i)
            #       if cap: break
            #   if cap: break
            init_time = time.time()
            Init = True
            while (True):
                #cap = cv2.VideoCapture(0)
                cap = cv2.VideoCapture(read_camera_index)
                if cap:
                    break
                #if time.time() > init_time + 5:
                #    if cap:
                #        print "Init True"
                #        Init = True
                #    else:
                #        print "Init False"
                #        Init = False
                #    break
            print "Init"
            print Init
            image_name = os.path.join(image_name,'frame.jpg')
            if Init:

                read_begin_time = time.time()
                while (True):
                    # Capture frame-by-frame
                    ret, frame = cap.read()
                    if (cap.get(3) > 0) and (cap.get(4) > 0) and (ret == True):
                        cv2.imshow('frame', frame)
                        cv2.waitKey(1)
                        if time.time()>read_begin_time+10:
                            print "Capturing Image"
                            ##cv2.imwrite(
                            ##    "C:\\Users\\IMI-User\\Anaconda2\\Lib\\site-packages\\googlesamples\\assistant\\grpc\\frame.jpg",
                            ##    frame) #np.fliplr(frame)
                            cv2.imwrite(image_name,frame) #np.fliplr(frame)
                            break
                        #if cv2.waitKey(1) & 0xFF == ord('q'):
                        #    cv2.imwrite(
                        #        "C:\\Users\\IMI-User\\Anaconda2\\Lib\\site-packages\\googlesamples\\assistant\\grpc\\frame.jpg",
                        #        np.fliplr(frame))
                        #    break
                if os.path.exists(image_name):
                ##if os.path.exists("C:\\Users\\IMI-User\\Anaconda2\\Lib\\site-packages\\googlesamples\\assistant\\grpc\\frame.jpg"):
                    # To detect text in captured frame
                    # Get Google Vision API client
                    client = vision.ImageAnnotatorClient()
                    with io.open(image_name,'rb') as image_file:
                    ##with io.open("C:\\Users\\IMI-User\\Anaconda2\\Lib\\site-packages\\googlesamples\\assistant\\grpc\\frame.jpg",
                    ##             'rb') as image_file:
                        content = image_file.read()

                    image = types.Image(content=content)
                    # detect text
                    response = client.text_detection(image=image)
                    texts = response.text_annotations
                    log = False
                    Address = ""
                    print('Texts:')
                    FIN = ''
                    for text in texts:
                        print('\n"{}"'.format(text.description))
                        if read_type == 1:
                            dummy = re.findall('(\d+)',text.description)
                            if len(dummy):
                                if (len(dummy[0]) == 7):
                                    FIN = text.description
                        elif read_type == 2:
                            if log:
                                Address = Address + " " + text.description
                            if "To" in text.description:
                                log = True

                            if "From" in text.description:
                                log = False
                        elif read_type == 3:
                            dummy = re.findall('(\d+)',text.description)
                            if len(dummy):
                                if (len(dummy[0]) == 7):
                                    FIN = text.description
                        else:
                            #Use cases can be added later - Normal version of read - for all inputs
                            print("Nothing to do")
                        #self.vh_client.client.speak(text.description, 10)

                    if (len(texts)):
                        reply = texts[0].description
                        if read_type == 1:
                            if FIN:
                                print('FIN:', FIN)
                                Emp_info = [D for D in self._Emp_Dict if FIN in D]
                                if Emp_info:
                                    reply = "I know you " + Emp_info[0][0] + ", you are a " + Emp_info[0][2] + " at I M I, N T U"
                                    UserName = Emp_info[0][0]
                                else:
                                    FIN = FIN.replace(""," ")
                                    reply = "I've identified this FIN number " + FIN + " in the card. I do not have a corresponding entry in my database."
                            else:
                                reply = "I cannot identify a clear FIN number to match with my database"
                            #if "G1120008M" in texts[0].description:
                            #    reply = "I know you Yasir, you are a researcher at IMI, NTU"
                            #else:
                            #    print("FIN",FIN)
                            #    if FIN:
                            #        FIN = FIN.replace(""," ")
                            #        reply = "I've identified this FIN number" + FIN + "in the card. I do not have a corresponding entry in my database."
                            #        #reply = "I've identified this FIN number G 1 1 7 1 1 5 6 T in the card. I do not have a corresponding entry in my database."
                            #    else:
                            #        reply = "I cannot identify a clear FIN number to match with my database"
                        elif read_type == 2:
                            Address = Address.lower()
                            Emp_info = [D for D in self._Emp_Dict if D[0] in Address]
                            if Emp_info:

                            #if "Yasir" in Address:
                                gmail_user = 'nadine.imi.ntu@gmail.com'
                                gmail_password = 'nadine@ntuimi'


                                sent_from = gmail_user
                                #to = ['yassertahir@gmail.com']
                                to = [Emp_info[0][3]]
                                subject = 'parcel for you'
                                body = texts[0].description

                                email_text = """\  "\r\n".join([
                                From: %s
                                To: %s
                                Subject: %s

                                %s
                                """ % (sent_from, ", ".join(to), subject, body)

                                try:
                                    server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
                                    server.ehlo()
                                    server.login(gmail_user, gmail_password)
                                    server.sendmail(sent_from, to, email_text)
                                    server.close()

                                    print 'Email sent!'
                                    #reply = "I have received a mail for Yasir and an email has been sent to him."
                                    reply = "I have received a mail for "+ Emp_info[0][0] + " and an email has been sent."
                                except:
                                    print 'Something went wrong..'
                                    #reply = "I have received a mail for Yasir but the email could not be sent at this time."
                                    reply = "I have received a mail for "+ Emp_info[0][0] + " but the email could not be sent at this time."
                        elif read_type == 3:
                            a = texts[0].description.split('\n')
                            upper_count = 0
                            VisitorName = ''
                            for line in a:
                                if line.isupper():
                                    upper_count += 1
                                if upper_count == 2:
                                    VisitorName = line
                                    break
                                print line
                                print("V", VisitorName)
                            UserName = VisitorName
                            #if texts[2].description == 'Name':
                            #    VisitorName = texts[3].description
                            #else:
                            #    VisitorName = texts[2].description

                            if FIN:
                                FIN = FIN.replace(""," ")
                                reply = "Welcome " + VisitorName + "to I M I, N T U. your FIN is identified as " + FIN
                            else:
                                reply = "Welcome " + VisitorName + "to I M I, N T U. How can I help you?"
                        else:
                            #Dummy use case - all content read will be spoken out
                            print("Normal reply")



                    else:
                        reply = "Nothing to read"
                    # When everything done, release the capture
                    cap.release()
                    cv2.destroyAllWindows()

                    #Remove the frame used for reading the text
                    #os.remove("C:\\Users\\IMI-User\\Anaconda2\\Lib\\site-packages\\googlesamples\\assistant\\grpc\\frame.jpg")
                    os.remove(image_name)
            else:
                print "No Camera detected "
                reply = "Nothing to read"
        except:
               reply = "Nothing to read"
        return reply, UserName

    def search_pictures(self,search_keyword,keywords):
        i = 0
        while i < len(search_keyword):
            items = []
            iteration = "Item no.: " + str(i + 1) + " -->" + " Item name = " + str(search_keyword[i])
            print (iteration)
            print ("Evaluating...")
            search_keywords = search_keyword[i]
            search = search_keywords.replace(' ', '%20')

            # make a search keyword  directory
            # try:
            #     os.makedirs(search_keywords)
            # except OSError, e:
            #     if e.errno != 17:
            #         raise
            #         # time.sleep might help here
            #     pass

            j = 0
            while j < len(keywords):
                pure_keyword = keywords[j].replace(' ', '%20')
                url = 'https://www.google.com/search?q=' + search + pure_keyword + '&espv=2&biw=1366&bih=667&site=webhp&source=lnms&tbm=isch&sa=X&ei=XosDVaCXD8TasATItgE&ved=0CAcQ_AUoAg'
                raw_html = (self.download_page(url))
                time.sleep(0.1)
                items = items + (self._images_get_all_items(raw_html))
                j = j + 1
            # print ("Image Links = "+str(items))
            print ("Total Image Links = " + str(len(items)))
            print ("\n")

            # This allows you to write all the links into a test file. This text file will be created in the same directory as your code. You can comment out the below 3 lines to stop writing the output to the text file.
            # info = open('output.txt', 'a')  # Open the text file called database.txt
            # info.write(str(i) + ': ' + str(search_keyword[i - 1]) + ": " + str(items) + "\n\n\n")  # Write the title of the page
            # info.close()  # Cl
            with open("C:\\xampp\\htdocs\\Reader\\nadine_app.txt", "a") as myfile:
                for item in items:
                    myfile.write(str(datetime.now().strftime("%a, %d %B %Y %I:%M:%S")) + " ### " + "Nadine" + "** PicturePath[" + str(item.replace("'", "")) + "]\n")
            i=i+1
    def download_page(self,url):
        version = (3, 0)
        cur_version = sys.version_info
        if cur_version >= version:  # If the Current Version of Python is 3.0 or above
            import urllib.request  # urllib library for Extracting web pages
            try:
                headers = {}
                headers[
                    'User-Agent'] = "Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2228.0 Safari/537.36"
                req = urllib.request.Request(url, headers=headers)
                resp = urllib.request.urlopen(req)
                respData = str(resp.read())
                return respData
            except Exception as e:
                print(str(e))
        else:  # If the Current Version of Python is 2.x
            import urllib2
            try:
                headers = {}
                headers[
                    'User-Agent'] = "Mozilla/5.0 (X11; Linux i686) AppleWebKit/537.17 (KHTML, like Gecko) Chrome/24.0.1312.27 Safari/537.17"
                req = urllib2.Request(url, headers=headers)
                response = urllib2.urlopen(req)
                page = response.read()
                return page
            except:
                return "Page Not found"

                # Finding 'Next Image' from the given raw page
    def _images_get_next_item(self,s):
        start_line = s.find('rg_di')
        if start_line == -1:  # If no links are found then give an error!
            end_quote = 0
            link = "no_links"
            return link, end_quote
        else:
            start_line = s.find('"class="rg_meta"')
            start_content = s.find('"ou"', start_line + 1)
            end_content = s.find(',"ow"', start_content + 1)
            content_raw = str(s[start_content + 6:end_content - 1])
            return content_raw, end_content

    # Getting all links with the help of '_images_get_next_image'
    def _images_get_all_items(self,page):
        items = []
        count=0
        while count<5:
            item, end_content = self._images_get_next_item(page)
            if item == "no_links":
                break
            else:
                items.append(item)  # Append all the links in the list named 'Links'
                time.sleep(0.1)  # Timer could be used to slow down the request for image downloads
                page = page[end_content:]
            count=count+1
        return items
    def face_rec(self):
        i=0
        while i<12:
            f=open("G:\\IMI-PROJECTS\\x64\\Release\\1.txt","w+")
            f.close()
            i=i+1
            time.sleep(5)

    def emotion_rec(self):
        i=0
        while i<12:
            f=open("G:\\IMI-PROJECTS\\x64\\Release\\2.txt","w+")
            f.close()
            i=i+1
            time.sleep(5)
if __name__=="__main__":

    # gender=Gender()
    # gender.loadGender()
    # gender.userGender["Vanessa"]="female"
    # print gender.userGender
    # gender.saveGender()

    sent_proc=sentenceUtils()
    print sent_proc.clearChatBotAnswer("hmmm, I don't know")
    # print sent_proc.substitute("I am ntu student","ntu","n t u")
    #
    #
    # question="Can you play basketball"
    # answer1="Yes, I can"
    # answer2="I like it very much"
    # sent="It's a private question"
    # sent_proc=sentenceUtils()
    # print sent_proc.isCompleteSentence(sent)
    # print sent_proc.getCompleteAnswer(question,answer1)
    # print sent_proc.getCompleteAnswer(question,answer2)


