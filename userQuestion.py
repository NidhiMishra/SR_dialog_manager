__author__ = 'Zhang Juzheng'
from dataStructure import Queue
import cPickle as pickle
import random
import os
from loadFolder import *
from copy import copy

class userQuestion:
    def __init__(self,userName=None):
        self.queue=Queue()
        self.questions=pickle.load(open('questions.pickle','rb'))
        # res=[]
        # res.append(self.questions["standard"][0])
        # res.append(self.questions["standard"][1])
        # res.append(self.questions["standard"][3])
        # self.questions["standard"]=res
        # pickle.dump(self.questions,open('questions.pickle','wb'))
        self.topics=self.questions.keys()
        self.topics.remove("standard")
        self.getUserName(userName)
        self.loadAskedIndex()
        self.standardFlag=True

    def getUserName(self,userName):
        basepath=os.getcwd()+"\\"+"userData"
        if not os.path.exists(basepath):
            os.makedirs(basepath)

        if userName!="":
            self.user=userName
        else:
            self.user="Unknown"


    def saveAskedIndex(self):
        filename=os.getcwd()+"\\userData\\"+self.user+".pickle"
        file=open(filename,'wb')
        pickle.dump(self.askedIndex,file)
        file.close()

    def loadAskedIndex(self):
        if self.user!=None:
            path=os.getcwd()+"\\userData\\"+self.user+".pickle"
            if os.path.isfile(path):
                self.askedIndex=pickle.load(open(path, "rb"))
            elif self.user=="Unknown":
                self.askedIndex={}
                self.askedIndex["standard"]=[0,1,2]
            else:
                self.askedIndex={}
        else:
            self.askedIndex={}

    def randomChoose(self,List):
        '''randomly choose an element in a list'''
        if not List:
            return None
        length=len(List)
        rand=random.randint(0,length-1)
        return List[rand]

    def filterIdx(self,topic):
        L1=self.questions[topic]
        L2=[]
        if topic in self.askedIndex.keys():
            L2=self.askedIndex[topic]
        res=[]
        for i in range(len(L1)):
            if i not in L2:
                res.append(i)
        if len(res)>0:
            return res
        else:
            return None


    def getRandomQuestion(self,topicList):
        topic=self.randomChoose(topicList)
        if topic==None:
            return None
        quesIdx=self.filterIdx(topic)
        if quesIdx:
            resIdx=self.randomChoose(quesIdx)
            res=self.questions[topic][resIdx]
            if topic not in self.askedIndex.keys():
                self.askedIndex[topic]=[]
            self.askedIndex[topic].append(resIdx)
            return res
        elif len(topicList)==0:
            return None
        else:
            topicList.remove(topic)
            self.getRandomQuestion(topicList)

    def getStandardQuestion(self):
        topic="standard"
        quesIdx=self.filterIdx(topic)
        if quesIdx:
            #resIdx=self.randomChoose(quesIdx)
            resIdx=quesIdx[0]
            res=self.questions[topic][resIdx]
            if topic not in self.askedIndex.keys():
                self.askedIndex[topic]=[]
            self.askedIndex[topic].append(resIdx)
            return res
        else:
            return None






    def push(self,question):
        self.queue.push(question)

    def pop(self):
        question=None
        if self.standardFlag:
            question=self.getStandardQuestion()
            if question==None:
                self.standardFlag=False
                question=self.getRandomQuestion(copy(self.topics))
        else:
            question=self.getRandomQuestion(copy(self.topics))
        if question:
            self.push(question)
        if not self.queue.isEmpty():
            res=self.queue.pop()
            return res
        return None


if __name__=="__main__":
    userQ=userQuestion()
    i=0
    while i<40:
        print userQ.pop()
        i+=1