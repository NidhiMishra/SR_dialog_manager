__author__ = 'Zhang Juzheng'

from enum import Enum
from nltk import word_tokenize
from textblob import TextBlob

class QPattern(Enum):
    REMEMBER=1
    SUMMERY=2
    USER=3
    USER_DATE=4
    USER_TIME=5
    RECENT=6
    DAY_USERS=7
    WHAT_IS=8
    RELATION=9




class checkQPattern:
    def __init__(self,users,curUser):
        self._build()
        self.users=users
        self.curUser=curUser

    def _build(self):
        self.otherQuestion={QPattern.REMEMBER:["do you remember","do you know","could you tell me"],
          QPattern.SUMMERY: ["what we talked last time","what did we talk last time"],
          QPattern.RECENT:["how are you recently"],
          QPattern.DAY_USERS:["who did you meet","who have you seen","whom did you meet"]
        }
        self.userQuestion={
          QPattern.USER:["do you know","who is","do you remember"],
          QPattern.USER_DATE:["have you seen","did you meet","did you see"],
          QPattern.USER_TIME:["when did you meet","what time did you meet","when did you see","what time did you see"]
          }

    def transferFirstPerson(self,tokens):
        first=["i","me"]
        for word in first:
            if word in tokens:
                idx=tokens.index(word)
                tokens[idx]=self.curUser
        
    def hasUser(self,sentence):
        sent=sentence.lower()
        tokens=word_tokenize(sent)
        self.transferFirstPerson(tokens)    
        for user in self.users:
            if user in tokens:
                return True,user
        return False,None

    def checkWhatIs(self,sentence):
        words=word_tokenize(sentence.lower())
        self.transferFirstPerson(words)
        q_word=["who","what"]
        be_word=["am","is","are","was","were"]
        if len(words)<3:
            return None
        elif len(words)==3 and (words[1] in be_word):
            if (words[2] in q_word) and (words[0] not in q_word):
                return words[0]
            elif (words[0] in q_word) and (words[2] not in q_word):
                res=[words[2]]
                return res
            else:
                return None
        elif len(words)>3:
            if words[0] in q_word and words[1] in be_word:
                return words
            else:
                return None

    def checkRelation(self,sentence):
        sentence=sentence.lower()
        starts=["what is the relation","what's the relation"]
        if sentence.startswith(starts[0]) or sentence.startswith(starts[1]):
            words=word_tokenize(sentence.lower())
            self.transferFirstPerson(words)
            idx1=self.getWordIdx(["of","between","among"],words)
            if idx1:
                idx2=self.getWordIdx(["and"],words)
                if idx2:
                    arg1=words[idx1+1:idx2]
                    arg2=words[idx2+1:]
                    if len(arg1)>0 and len(arg2)>0:
                        arg1=" ".join(arg1)
                        arg2=" ".join(arg2)
                        return [arg1,arg2]
        return None

    def checkKnowledge(self,sentence):
        query=self.checkRelation(sentence)
        if query:
            return (QPattern.RELATION,query)
        query=self.checkWhatIs(sentence)
        if query:
            return (QPattern.WHAT_IS,query)
        return None

    def getWordIdx(self,word_list,tokens):
        for word in tokens:
            if word in word_list:
                res=tokens.index(word)
                return res
        return None




    def checkQPattern(self,sentence):
        userFlag,userName=self.hasUser(sentence)
        if userFlag:
            Sentence=self.userQuestion
            for (pattern,sList) in Sentence.items():
                for sent in sList:
                    if sentence.startswith(sent):
                        remainWord=sentence.split(sent)[1][1:]
                        remainWords=remainWord.split()
                        if self.isContain(remainWords,[userName.lower(),"me","i"]):
                            if pattern!=QPattern.USER:
                                return pattern
                            elif not self.isContain(remainWords,["mother","father","husband","daughter","mom","dad"]):
                                return pattern
        else:
            Sentence=self.otherQuestion
            for (pattern,sList) in Sentence.items():
                for sent in sList:
                    if sentence.startswith(sent):
                        return pattern
        return None

    def isContain(self,wordList,candidates):
        for word in candidates:
            if word in wordList:
                return True
        return False



