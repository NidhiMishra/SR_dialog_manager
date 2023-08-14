__author__ = 'IMI-User'
from AIMLWritter import AIMLWriter

class LearnQA:
    def __init__(self):
        self.learnCue=["you should say", "you should answer"]
        self.answer=""
        self.QADict={}
        self.aimlWriter=AIMLWriter()

    def getAnswer(self,sentence):
        matchedCue=None
        for cue in self.learnCue:
            if cue in sentence:
                matchedCue=cue
                break
        if matchedCue==None:
            return False # continue
        midx=sentence.find(matchedCue)+len(matchedCue)+1
        self.answer=sentence[midx:]
        if len(self.answer)==0: # no answer is given
            return False
        return True

    def updateQA(self,question):
        if self.answer!="":
            self.QADict[question]=[self.answer]
            self.answer=""

    def saveQA(self):
        if len(self.QADict)>0:
            self.aimlWriter.writeAIMLFile(self.QADict)
            self.QADict.clear()