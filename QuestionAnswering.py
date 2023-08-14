__author__ = 'Zhang Juzheng'
from utils import *
from QPattern import *
from textblob import TextBlob
from copy import copy
import context
from thrift.transport.TTransport import TTransportException
import sys
from predefinedSentence import *
from NadiaAnswer import NadiaAnswer

class QuestionAnswering:
    def __init__(self,memory_client,userName):
        self.time_proc=timeUtils()
        self.sent_proc=sentenceUtils()
        self.user=userName
        if memory_client!=None:
            self.memory_client=memory_client
            self.getKnownUsers()
            self.qPattern=checkQPattern(self.knownUsers,self.user.lower())
        else:
            self.knownUsers=[]
            self.memory_client=None
        self.attrs=[]
        self.randomfunc=randomFunc()
        self.context=context.Context()
        self.context.user=userName
        self.userReplyDb=[]
        self.peerReplyDb=[]
        self.nadiaAnswerTool=PredefinedSentence(loadAIML=False)
        self.nadiaAnswerTool.QAdict=NadiaAnswer

    def reset(self,userName):
        self.time_proc.updateCurrentTime()
        if self.memory_client!=None:
            self.getKnownUsers()
        self.user=userName
        self.context.user=userName
        self.qPattern=checkQPattern(self.knownUsers,self.user.lower())
        # if userName!="Unknown":
        #     self.memory_client.client.updateUser(userName)



    def getAttr(self,*args):
        self.attrs=[]
        attr_class=["sentence=","subject=","emotion=","mood="]
        args=list(args)
        _,args[0]=self.getSentenceUser(args[0])
        for i in range(len(args)):
            if args[i]:
                self.attrs.append(attr_class[i]+args[i])
            else:
                self.attrs.append(attr_class[i]+"None")
        self.attrs.append("eventState="+self.sent_proc.getSentenceState(args[0]))
        self.attrs.append("user="+self.user)
        self.attrs.append("weekday="+self.time_proc.weekday)
        self.attrs.append("socialTime="+self.time_proc.socialTime)
        self.questionS=self.sent_proc.checkInput(self.attrs)
        #return self.attrs

    def checkQ(self,userInput):
        if "?" in userInput:
            return True
        text=TextBlob(userInput.lower())
        tags=text.tags
        question=self.sent_proc.checkQuestion(tags)
        return question[0]

    def removeQ(self,sentence):
        sent=sentence.split(".")
        res=[]
        for s in sent:
            if not self.checkQ(s):
                res.append(s)
        if len(res)==0:
            return None
        else:
            return ".".join(res)

    def getLastTime(self):
        date=self.memory_client.client.getLastDate("user="+self.user)
        if date==None:
            return None
        date_str=self.time_proc.timeAnalyser.getSocialTime(date)
        if date_str:
            answer="I saw you "+date_str+"."
        else:
            answer=""
            #answer="I haven't seen you for a long time."
        return answer


    def getGreeting(self):
        try:
            if self.user=="Unknown":
                return "Hello"
                #return "Hello, nice to meet you"
            date=self.time_proc.getStringDate("today")
            if date==None:
                return None
            if not self.isKnownUsers(self.user):
                return None

            userList=self.memory_client.client.getUsersDate(date)
            num=userList.count(self.user)
            answer=None
            if num==0:
                #answer="It's the first time I see you today. You can ask me questions about our last conversation."
                lastTime=self.getLastTime()
                answer=lastTime+ " How are you going?"

            else:
                #answer="Nice to meet you again today. You can ask me questions about our last conversation."
                #answer="Nice to meet you again today."
                ### By James Today
                answer="again"
            # report=self.getReport()
            # if report:
            #     answer=answer+". "+report
            return answer
        except TTransportException:
            print TTransportException.message
            return None
        except:
            print "Unexpected error:", sys.exc_info()[0]
            return None

    def get_greeting(self,user):
        try:
            res=self.memory_client.client.getGreetings(user)
            if len(res)==1:
                return self.sent_proc.changeToSecondPerson(res[0])
            elif len(res)>1:
                answer=", ".join(res[:-1])+" and "+res[-1]
                return self.sent_proc.changeToSecondPerson(answer)
        except TTransportException:
            print TTransportException.message
            return None
        except:
            print "Unexpected error:", sys.exc_info()[0]
            return None

    def getUserInfo(self,user):
        try:
            res=self.memory_client.client.getGreetings("user="+user)
            if len(res)==1:
                return self.sent_proc.changeToThirdPerson(res[0],user)
            elif len(res)>1:
                answer=", ".join(res[:-1])+" and "+res[-1]
                return self.sent_proc.changeToThirdPerson(answer,user)
            else:
                return None
        except TTransportException:
            print TTransportException.message
            return None
        except:
            print "Unexpected error:", sys.exc_info()[0]
            return None




    def get_knowledge(self,sentence,user=None):
        if len(sentence)==0:
            res=self.memory_client.client.getKnowledge([],user)
            if len(res)==1:
                return self.sent_proc.changeToSecondPerson(res[0])
            elif len(res)>1:
                answer=", ".join(res[:-1])+" and "+res[-1]
                return self.sent_proc.changeToSecondPerson(answer)

        knowledge=self.qPattern.checkKnowledge(sentence)
        if knowledge:
            query=knowledge[1]
            res=self.memory_client.client.getKnowledge(query,user)
            #if len(res)==0:
                #return "Sorry, I have no idea"
            if len(res)==1:
                return self.sent_proc.changeToSecondPerson(res[0])
            elif len(res)>1:
                answer=", ".join(res[:-1])+" and "+res[-1]
                return self.sent_proc.changeToSecondPerson(answer)
        return None

    def answerQ(self,sentence):
        try:
            pattern=self.qPattern.checkQPattern(sentence)

            if pattern==QPattern.SUMMERY:
                keyWords=self.memory_client.client.getEpisodeSummery(None,"user="+self.user)
                if len(keyWords)==0:
                    return "Sorry, I guess we haven't talked with each other before."
                sent=", ".join(keyWords)
                return "We have talked about "+sent

            elif pattern==QPattern.RECENT:
                userDict=self.memory_client.client.getRecentUsers()
                dateList=userDict.keys()
                if len(dateList)==0:
                    return "Recently I am lonely because no friend comes to me."
                dateList=self.time_proc.timeAnalyser.reorderTimefromString(dateList)
                answer=""
                for date in dateList:
                    date_str=self.time_proc.timeAnalyser.getSocialTime(date)
                    users=userDict[date]
                    users=list(set(users))
                    if self.user in users:
                        users.remove(self.user)
                        if len(users)>0:
                            _str= date_str+ " I talked with "+", ".join(users)+" and you"
                        else:
                            _str= date_str+" I talked with you"
                    else:
                        if len(users)==1:
                            _str= date_str+" I talked with "+users[0]
                        elif len(users)>1:
                            _str= date_str+" I talked with "+", ".join(users[:-1])+" and "+users[-1]
                    answer+=self.sent_proc.transferThirdtoSecondPerson(_str,self.user)+". "
                return answer

            elif pattern==QPattern.USER:
                user,sentence=self.getSentenceUser(sentence)
                if sentence.endswith(user.lower()) or sentence.endswith("me"):
                    if user!=self.user:
                        answer=self.getUserInfo(user)
                        return answer
                    else:
                        answer=self.getUserInfo(user)
                        if answer!=None:
                            return self.sent_proc.transferThirdtoSecondPerson(answer,self.user)
                        else:
                            return None


            elif pattern==QPattern.USER_DATE:
                date=self.time_proc.getStringDate(sentence)
                user, sentence=self.getSentenceUser(sentence)
                if date==None:
                    return "No required time information is found in your question"
                seen=self.memory_client.client.isSeenUser("user="+user,date)
                if len(seen)>0:
                    freq_str=self.getFreqStr(seen)
                    answer="Yes, I saw "+user+" "+freq_str
                    return self.sent_proc.transferThirdtoSecondPerson(answer,self.user)
                else:
                    answer= "No, I didn't see "+user+"."
                    return self.sent_proc.transferThirdtoSecondPerson(answer,self.user)

            elif pattern==QPattern.USER_TIME:
                user,sentence=self.getSentenceUser(sentence)
                date=self.memory_client.client.getLastDate("user="+user)
                if date==None:
                    answer= "I didn't see "+user+" before."
                    return self.sent_proc.transferThirdtoSecondPerson(answer,self.user)
                print "date: "+date
                date_str=self.time_proc.timeAnalyser.getSocialTime(date)
                if date_str:
                    print "date: "+date_str
                    answer="I saw "+user+" "+date_str+"."
                else:
                    answer="I haven't seen "+user+" for a long time."

                return self.sent_proc.transferThirdtoSecondPerson(answer,self.user)

            elif pattern==QPattern.DAY_USERS:
                date=self.time_proc.getStringDate(sentence)
                if date==None:
                    return "No required time information is found in your question"
                date_str=self.time_proc.timeAnalyser.getSocialTime(date)
                userList=self.memory_client.client.getUsersDate(date)
                userList=list(set(userList))
                if len(userList)==0:
                    return "Sorry, I didn't see anyone "+date_str
                else:
                    if self.user in userList:
                        userList.remove(self.user)
                        if len(userList)>0:
                            answer= "I talked with "+", ".join(userList)+" and you"
                            return answer
                        else:
                            answer= "I only talked with you"
                            return answer
                    else:
                        if len(userList)==1:
                            answer= "I only talked with "+userList[-1]
                            return answer
                        elif len(userList)>1:
                            answer= "I talked with "+", ".join(userList[:-1])+" and "+userList[-1]
                            return answer
            return None
        except TTransportException:
            print TTransportException.message
            return None
        except:
            print "Unexpected error:", sys.exc_info()[0]
            return None

    def getReport(self):
        knowledge=self.get_greeting("user="+self.user)
        if knowledge==None:
            return None
        answer=knowledge
        return answer



    def getAnswer(self,cue,inputQ):
        attrs=copy(self.attrs)
        if cue!=None:
            attrs[0]="sentence="+cue
        userInput=attrs[0].split("=")[1]
        sentence=userInput.lower()
        sentence=processSentence(sentence)

        sentUser,sentence=self.getSentenceUser(sentence)
        if sentUser!=None and sentUser!="Robot":
            print "sentUser: "+sentUser
        else:
            print "sentUser: None"

        ################### Add for Nadia #############
        if self.user=="Nadia":
            reply=self.nadiaAnswerTool.getAnswer(sentence)
            if reply!=None:
                return (reply,False)
        ############################################
        nouns=self.sent_proc.getNouns(sentence,sentUser)

        if sentUser!=None and sentUser!="Robot" and sentUser!=self.user:
            self.context.lastSearchUser=sentUser
            print "search user: "+sentUser
            if nouns==None or len(nouns)==0:
                nouns=self.context.lastSearchTerm


        question=self.checkQ(userInput)
        if question:
            answer=self.answerQ(sentence)
            if answer:
                return (answer,False) # We don't add chatbot answer for this kind of questions

        if sentUser=="Robot":
            return (None,True)
        if nouns==None or nouns==[]:
            return (None,True)
        print "Search Words: "+nouns

        self.context.lastSearchTerm=nouns
        attrs[0]="sentence="+nouns
        # general retrieval
        if sentUser!=None and sentUser!=self.user:
            return self.giveMemoryAnswer(attrs,nouns,inputQ,question,user=sentUser,thirdPersonFlag=True)
        else:
            return self.giveMemoryAnswer(attrs,nouns,inputQ,question,user=self.user)


    def giveMemoryAnswer(self,attrs,nouns,inputQ,question,user,thirdPersonFlag=False):
        userReply=self.findSimilarEvent(attrs,user)
        peerReply=None
        # if thirdPersonFlag:
        #     prob=0.8
        # else:
        #     prob=0.5
        # if self.randomfunc.randProb(prob):
        #     # have half chance to retrieve event from others
        #     peerReply=self.findPeerEvent(attrs,user)
        if peerReply!=None and userReply==None:
            if question:
                answer=self.getPeerAnswer(peerReply,nouns,inputQ,False)
                return (answer,True)
            else:
                answer=self.getPeerAnswer(peerReply,nouns,inputQ)
                return (answer,True)
        elif userReply!=None and peerReply==None:
            if thirdPersonFlag:
                userAnswer=self.getThirdPersonAnswer(userReply,user,inputQ)
            else:
                userAnswer=self.getUserAnswer(userReply,inputQ)
            return (userAnswer,True)
        elif userReply!=None and peerReply!=None:
            if thirdPersonFlag:
                userAnswer=self.getThirdPersonAnswer(userReply,user,inputQ)
            else:
                userAnswer=self.getUserAnswer(userReply,inputQ)
            peerAnswer=self.getPeerAnswer(peerReply,nouns,inputQ)
            if peerAnswer!=None and userAnswer!=None:
                connection=self.randomfunc.randomChoose(["and","in addition","what's more"])
                answer=userAnswer + ". "+connection+", "+peerAnswer
                return answer,True
            return peerAnswer,True
        else:
            return None,True

    # def giveMemoryAnswer(self,attrs,nouns,inputQ,question,user,thirdPersonFlag=False):
    #     userReply=self.findSimilarEvent(attrs,user)
    #     peerReply=None
    #     if thirdPersonFlag:
    #         prob=0.8
    #     else:
    #         prob=0.5
    #     if self.randomfunc.randProb(prob):
    #         # have half chance to retrieve event from others
    #         peerReply=self.findPeerEvent(attrs,user)
    #     if peerReply!=None and userReply==None:
    #         if question:
    #             answer=self.getPeerAnswer(peerReply,nouns,inputQ,False)
    #             return (answer,True)
    #         else:
    #             answer=self.getPeerAnswer(peerReply,nouns,inputQ)
    #             return (answer,True)
    #     elif userReply!=None and peerReply==None:
    #         if thirdPersonFlag:
    #             userAnswer=self.getThirdPersonAnswer(userReply,user,inputQ)
    #         else:
    #             userAnswer=self.getUserAnswer(userReply,inputQ)
    #         return (userAnswer,True)
    #     elif userReply!=None and peerReply!=None:
    #         if thirdPersonFlag:
    #             userAnswer=self.getThirdPersonAnswer(userReply,user,inputQ)
    #         else:
    #             userAnswer=self.getUserAnswer(userReply,inputQ)
    #         peerAnswer=self.getPeerAnswer(peerReply,nouns,inputQ)
    #         if peerAnswer!=None and userAnswer!=None:
    #             connection=self.randomfunc.randomChoose(["and","in addition","what's more"])
    #             answer=userAnswer + ". "+connection+", "+peerAnswer
    #             return answer,True
    #         return peerAnswer,True
    #     else:
    #         return None,True

    def getThirdPersonAnswer(self,userReply,sentUser,inputQ=False):
        flag=self.checkRepeatFlag(userReply,inputQ)
        if not flag:
            answer=self.sent_proc.changeToThirdPerson(userReply,sentUser)
            addSent=[sentUser+" told me that ",sentUser+" said that "]
            add=self.randomfunc.randomChoose(addSent)
            answer=add+answer
            return answer
        print "User Repeat"
        return None


    def checkRepeatFlag(self,reply,inputQ):
        flag=False
        if not inputQ:
            repeatFlag=self.isRepeatUserReply(reply)
            if repeatFlag:
                flag=True
        else:
            self.isRepeatUserReply(reply)
        return flag

    def getPeerAnswer(self,peerReply,que_nouns,inputQ=False,also_flg=True):
        answers=[]

        flag=self.checkRepeatFlag(peerReply[0],inputQ)
        # flag=self.isRepeatPeerReply(peerReply)
        if not flag:
            if peerReply[1]==self.user:
                sentence=self.sent_proc.changeToSecondPerson(peerReply[0])
            else:
                sentence=self.sent_proc.changeToThirdPerson(peerReply[0],peerReply[1])
            if also_flg and que_nouns not in [None,""]:
                ans_nouns=self.sent_proc.getNouns(sentence,peerReply[1])
                if ans_nouns not in [None,""]:
                    q_nouns=set(que_nouns.split())
                    a_nouns=set(ans_nouns.split())
                    if q_nouns==a_nouns:
                        if peerReply[1]==self.user:
                            answers.append(sentence)
                            #answers.append("you also said that "+sentence)
                        else:
                            answers.append(peerReply[1]+" also said that "+sentence)
                            #answers.append(peerReply[1]+" also said that "+sentence)
            if len(answers)==0:
                if peerReply[1]==self.user:
                    answers.append(sentence)
                    #answers.append("you said that "+sentence)
                else:
                    #answers.append("I remember "+peerReply[1]+" said that "+sentence)
                    answers.append(peerReply[1]+" said that "+sentence)

            answer=self.randomfunc.randomChoose(answers)
            return answer
        print "Peer Repeat"
        return None

    def getUserAnswer(self,userReply,inputQ=False):
        answers=[]
        flag=self.checkRepeatFlag(userReply,inputQ)
        if not flag:
            sentence=self.sent_proc.changeToSecondPerson(userReply)
            #answers.append("I remember you said that "+sentence)
            answers.append(sentence)
            #answers.append(sentence)
            answer=self.randomfunc.randomChoose(answers)
            return answer
        print "User Repeat"
        return None

    def isRepeatUserReply(self,userReply):
        res=True
        if userReply not in self.userReplyDb:
            self.userReplyDb.append(userReply)
            res=False
        while len(self.userReplyDb)>2:
            self.userReplyDb.pop(0)
        return res

    def isRepeatPeerReply(self,peerReply):
        res=False
        for reply in self.peerReplyDb:
            if peerReply[0]==reply[0] and peerReply[1]==reply[1]:
                res=True
                break
        if not res:
            self.peerReplyDb.append(peerReply)
        while len(self.peerReplyDb)>2:
            self.peerReplyDb.pop(0)
        return res


    def getFreqStr(self,timeList):
        freq={}
        for str in timeList:
            if str not in freq:
                freq[str]=0
            freq[str]+=1
        res=""
        for str,num in freq.items():
            if num==1:
                num_str="1 time"
            else:
                num_str=str(num)+" times"
            res+=num_str+" in the "+str.lower()+", "
        return res

    def findSimilarEvent(self,attrs,user,th=0.5,date=None):
        try:
            event=self.memory_client.client.getSimilarEvent(attrs,date,"user="+user)
            if len(event)==0:
                return None
            sentence=event[0]
            return sentence
        except TTransportException:
            print TTransportException.message
            return None
        except:
            print "Unexpected error:", sys.exc_info()[0]
            return None

    def findPeerEvent(self,attrs,user,th=0.5,date=None):
        try:
            if user!=self.user:
                event=self.memory_client.client.getSimilarEvent(attrs,date,"user="+self.user)
                if len(event)==0:
                    event=self.memory_client.client.getPeerEvent(attrs,date,"user="+user)
                    if len(event)==0: return None
            else:
                event=self.memory_client.client.getPeerEvent(attrs,date,"user="+user)
                if len(event)==0: return None
            sentence=event[0]
            who=event[1]
            confidence=float(event[-1])
            #if confidence>=th:
            return (sentence,who)
        except TTransportException:
            print TTransportException.message
            return None
        except:
            print "Unexpected error:", sys.exc_info()[0]
            return None


    def storeEvent(self,End=False):
        try:
            attrs=self.attrs
            date=self.time_proc.date
            self.memory_client.client.storeEvent(attrs,End,date)
            #self.memory_client.client.closeMemory(self.user,None,End)
        except TTransportException:
            print TTransportException.message
        except:
            print "Unexpected error:", sys.exc_info()[0]
            return None



    def storeKnowledge(self,sentence):
        try:
            print "Store Knowledge: "+sentence
            attrs=self.attrs
            attrs[0]="sentence="+sentence
            attrs[1]="subject="+self.user
            self.memory_client.client.storeKnowledge(attrs)
        except TTransportException:
            print TTransportException.message
            return None
        except:
            print "Unexpected error:", sys.exc_info()[0]
            return None



    def getKnownUsers(self):
        try:
            knownUsers=self.memory_client.client.getKnownUsers()
            self.knownUsers=[user.lower() for user in knownUsers]
        except TTransportException:
            print TTransportException.message
            return None
        except:
            print "Unexpected error:", sys.exc_info()[0]
            return None

    def isKnownUsers(self,user):
        user=user.lower()
        if user in self.knownUsers:
            return True
        else:
            return False

    def getSentenceUser(self,sentence):
        sent=TextBlob(sentence)
        tokens=sent.tokens

        for user in self.knownUsers:
            if user in tokens:
                return user.capitalize(), sentence

        curUserFlag,myIdx,_=self.sent_proc.isContain(tokens,["i","me","my"])
        referUserFlag,heIdx,heWord=self.sent_proc.isContain(tokens,["he","his","him","she","her"])
        objectUserFlag,youIdx,_=self.sent_proc.isContain(tokens,["you","your"])
        if curUserFlag:
            x1=(not referUserFlag) and (not objectUserFlag)
            x2=referUserFlag and heIdx<myIdx
            x3=objectUserFlag and youIdx<myIdx
            if x1 or x2 or x3:
                self.context.lastSearchUser=None
                return self.user, sentence

        if referUserFlag and self.context.lastSearchUser!=None:
            sentence=self.sent_proc.substitute(sentence,heWord,self.context.lastSearchUser.lower())
            return self.context.lastSearchUser, sentence

        if objectUserFlag:
            self.context.lastSearchUser=None
            return "Robot", sentence

        return None, sentence




