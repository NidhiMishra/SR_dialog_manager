__author__ = 'Zhang Juzheng'
from utils import *
from QPattern import *
from MemoryCollection import MemoryCollection
from textblob import TextBlob
from copy import copy
from nltk import word_tokenize
import context

class QuestionAnswering:
    def __init__(self,memory_client,userName):
        self.memory_client=memory_client
        self.time_proc=timeUtils()
        self.sent_proc=sentenceUtils()
        self.getKnownUsers()
        self.user=userName
        self.qPattern=checkQPattern(self.knownUsers,self.user.lower())
        self.attrs=[]
        self.randomfunc=randomFunc()
        self.context=context.Context()
        self.context.user=userName
        self.userReplyDb=[]
        self.peerReplyDb=[]


    def reset(self,userName):
        self.time_proc.updateCurrentTime()
        self.getKnownUsers()
        self.user=userName
        self.context.user=userName
        self.qPattern=checkQPattern(self.knownUsers,self.user.lower())



    def getAttr(self,*args):
        self.attrs=[]
        attr_class=["sentence=","subject=","emotion=","mood="]
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
        return question

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




    def getGreeting(self):
        date=self.time_proc.getStringDate("today")
        if date==None:
            return None
        if not self.isKnownUsers(self.user):
            return "You are a new user to me. May I ask you a few questions?"

        userList=self.memory_client.client.getUsersDate(date)
        num=userList.count(self.user)
        answer=None
        if num==0:
            #answer="It's the first time I see you today. You can ask me questions about our last conversation."
            answer="It's the first time I see you today."
        else:
            #answer="Nice to meet you again today. You can ask me questions about our last conversation."
            answer="Nice to meet you again today."
        # report=self.getReport()
        # if report:
        #     answer=answer+". "+report
        return answer

    def get_greeting(self,user):
        res=self.memory_client.client.getGreetings(user)
        if len(res)==1:
            return self.sent_proc.changeToSecondPerson(res[0])
        elif len(res)>1:
            answer=", ".join(res[:-1])+" and "+res[-1]
            return self.sent_proc.changeToSecondPerson(answer)

    def getUserInfo(self,user):
        res=self.memory_client.client.getGreetings(user)
        if len(res)==1:
            return self.sent_proc.changeToThirdPerson(res[0])
        elif len(res)>1:
            answer=", ".join(res[:-1])+" and "+res[-1]
            return self.sent_proc.changeToThirdPerson(answer)

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



    def getReport(self):
        knowledge=self.get_greeting("user="+self.user)
        if knowledge==None:
            return None
        answer="I remember that "+ knowledge
        return answer

    def getAnswer(self,cue=None):
        attrs=copy(self.attrs)
        if cue!=None:
            attrs[0]="sentence="+cue
        userInput=attrs[0].split("=")[1]
        sentence=userInput.lower()

        sentUser=self.getSentenceUser(sentence)
        if sentUser!=None and sentUser!="Robot":
            print "sentUser: "+sentUser
        else:
            print "sentUser: None"


        nouns=self.sent_proc.getNouns(sentence,sentUser)

        if sentUser!=None and sentUser!="Robot" and sentUser!=self.user:
            self.context.lastSearchUser=sentUser
            print "search user: "+sentUser
            if nouns==None or len(nouns)==0:
                sentence=self.context.lastSearchTerm


        question=self.checkQ(userInput)
        if question:
            #duplicate=self.memory_client.client.isDuplicateQuestion(self.user, attrs)
            duplicate=None
            if duplicate:
                answer=self.user+", you asked that question before."
                return answer

            knowledge=self.get_knowledge(sentence,self.user)
            if knowledge:
                return knowledge

            pattern=self.qPattern.checkQPattern(sentence)
            # if not pattern:
            #     return None


            if pattern==QPattern.SUMMERY:
                keyWords=self.memory_client.client.getEpisodeSummery(None,"user="+self.user)
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
                user=self.getSentenceUser(sentence)
                if user!=self.user:
                    answer=self.getUserInfo("user="+user)
                    return answer


            elif pattern==QPattern.USER_DATE:
                date=self.time_proc.getStringDate(sentence)
                user=self.getSentenceUser(sentence)
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
                user=self.getSentenceUser(sentence)
                date=self.memory_client.client.getLastDate("user="+user)
                if date==None:
                    answer= "I remember I didn't see "+user+" before."
                    return self.sent_proc.transferThirdtoSecondPerson(answer,self.user)
                print "date: "+date
                date_str=self.time_proc.timeAnalyser.getSocialTime(date)
                print "date: "+date_str
                answer="I saw "+user+" "+date_str+"."
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




        if sentUser=="Robot":
            return None
        if sentence==None:
            return None

        self.context.lastSearchTerm=sentence
        attrs[0]="sentence="+sentence
        # general retrieval
        if sentUser!=None and sentUser!=self.user:
            userReply=self.findSimilarEvent(attrs,"user="+sentUser)
            if userReply!=None:
                answer=self.sent_proc.changeToThirdPerson(userReply)
                return answer
        else:
            peerReply=self.findPeerEvent(attrs,"user="+self.user)
            userReply=self.findSimilarEvent(attrs,"user="+self.user)
            if peerReply!=None and userReply==None:
                if question:
                    answer=self.getPeerAnswer(peerReply,nouns,False)
                    return answer
                else:
                    answer=self.getPeerAnswer(peerReply,nouns)
                    return answer
            elif userReply!=None and peerReply==None:
                answer=self.getUserAnswer(userReply)
                return answer
            elif userReply!=None and peerReply!=None:
                userAnswer=self.getUserAnswer(userReply)
                if self.randomfunc.randProb(0.7):
                    peerAnswer=self.getPeerAnswer(peerReply,nouns)
                    if peerAnswer!=None and userAnswer!=None:
                        connection=self.randomfunc.randomChoose(["and","in addition","what's more"])
                        answer=userAnswer + ". "+connection+", "+peerAnswer
                        return answer
                    return peerAnswer
                else:
                    return userAnswer

        return None

    def getPeerAnswer(self,peerReply,que_nouns,also_flg=True):
        answers=[]
        repeatFlag=self.isRepeatPeerReply(peerReply[:1])
        sentFlag=peerReply[2]
        userFlag=peerReply[3]
        #repeatFlag=False
        if not repeatFlag:
            sentence=self.sent_proc.changeToThirdPerson(peerReply[0])
            if also_flg:
                ans_nouns=self.sent_proc.getNouns(sentence,peerReply[1])
                if que_nouns!=None and ans_nouns!=None:
                    common=set(ans_nouns) & set(que_nouns)
                    flag1=common==set(ans_nouns)
                    flag2=common==set(que_nouns)
                    if flag1 and flag2:
                        if sentFlag:
                            answers.append("I roughly remember somebody also said that "+sentence+". But I am not sure")
                            answers.append("I remember some guy also said that "+sentence)
                            answers.append("Some guy also said that "+sentence)
                        else:
                            answers.append("I remember "+peerReply[1]+" also said that "+sentence)
                            answers.append(peerReply[1]+" also said that "+sentence)
                        answer=self.randomfunc.randomChoose(answers)
                        return answer
            else:
                if sentFlag:
                    answers.append("I roughly remember somebody said that "+sentence+". But I am not sure")
                    answers.append("I remember some guy said that "+sentence)
                    answers.append("Some guy said that "+sentence)
                else:
                    answers.append("I remember "+peerReply[1]+" said that "+sentence)
                    answers.append(peerReply[1]+" said that "+sentence)
                # repSent=self.sent_proc.replaceName(sentence,peerReply[1])
                # if repSent:
                #     answers.append(repSent)
                answer=self.randomfunc.randomChoose(answers)
                return answer
        return None

    def getUserAnswer(self,userReply):
        answers=[]
        repeatFlag=self.isRepeatUserReply(userReply[0])
        sentFlag=bool(userReply[1])
        if not repeatFlag:
            sentence=self.sent_proc.changeToSecondPerson(userReply[0])
            if sentFlag:
                add_sent=self.randomfunc.randomChoose(["I'm not quite sure, maybe ",\
                                                       "I almost forget, maybe ","I guess "])
            else:
                add_sent=self.randomfunc.randomChoose(["I remember you said that ",\
                                                       "you said that ","you told me "])
            answer=add_sent+sentence
            return answer
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
        event=self.memory_client.client.getSimilarEvent(attrs,date,user)
        if len(event)==0:
            return None
        sentence=event[0]
        sentFlag=bool(event[2])
        #confidence=float(event[-1])
        #if confidence>=th:
        return (sentence,sentFlag)

    def findPeerEvent(self,attrs,user,th=0.5,date=None):
        event=self.memory_client.client.getPeerEvent(attrs,date,user)
        if len(event)==0:
            return None
        sentence=event[0]
        who=event[1]
        sentFlag=bool(event[3])
        whoFlag=bool(event[4])
        # confidence=float(event[-1])
        #if confidence>=th:
        return (sentence,who,sentFlag,whoFlag)


    def storeEvent(self,End=False):
        attrs=self.attrs
        date=self.time_proc.date
        # if End:
        #     self.memory.saveEpisodes(date)
        # else:
        #     self.memory.pushEvents(attrs)
        self.memory_client.client.storeEvent(attrs,End,date)
        self.memory_client.client.closeMemory(self.user,None,End)

    def storeKnowledge(self,sentence):
        print "Store Knowledge: "+sentence
        attrs=self.attrs
        attrs[0]="sentence="+sentence
        attrs[1]="subject="+self.user
        self.memory_client.client.storeKnowledge(attrs)



    def getKnownUsers(self):
        knownUsers=self.memory_client.client.getKnownUsers()
        self.knownUsers=[user.lower() for user in knownUsers]

    def isKnownUsers(self,user):
        user=user.lower()
        if user in self.knownUsers:
            return True
        else:
            return False

    def getSentenceUser(self,sentence):
        sent=sentence
        tokens=word_tokenize(sent)
        curUserFlag,myIdx=self.sent_proc.isContain(tokens,["i","me","my"])
        referUserFlag,heIdx=self.sent_proc.isContain(tokens,["he","his","him","she","her"])
        objectUserFlag,youIdx=self.sent_proc.isContain(tokens,["you","your"])
        if curUserFlag:
            x1=(not referUserFlag) and (not objectUserFlag)
            x2=referUserFlag and heIdx<myIdx
            x3=objectUserFlag and youIdx<myIdx
            if x1 or x2 or x3:
                self.context.lastSearchUser=None
                return self.user

        if referUserFlag and self.context.lastSearchUser!=None:
            return self.context.lastSearchUser

        if objectUserFlag:
            self.context.lastSearchUser=None
            return "Robot"

        for user in self.knownUsers:
            if user in tokens:
                return user.capitalize()
        return None




