__author__ = 'Zhang Juzheng'

import cPickle as pickle
import os
from loadFolder import *
class readData:
    def __init__(self):
        return

    def readFile(self,filename):
        file = open(filename)
        while True:
            line = file.readline()
            if len(line)!=0:
                attr=line.split()
                if len(attr)==1:
                    attr=attr[0]
                yield attr
            else:
                break

    def readFileSentence(self,filename):
        file = open(filename)
        while True:
            line = file.readline()
            if len(line)!=0:
                yield line
            else:
                break

    def loadQuestion(self):
        self.questions={}
        path=os.getcwd()+"\\Questions\\ESL"
        if os.path.exists(path):
            filePaths=getPath(path)
            for _p in filePaths:
                name=_p.split("\\")[-1].split(".")[0].lower()
                self.questions[name]=[]
                File=self.readFileSentence(_p)
                while True:
                    try:
                        word=File.next()
                        self.questions[name].append(word[:-1])
                    except StopIteration:
                        break



    def loadStopwords(self):
        self.stopwords=[]
        File=self.readFile("D:\\BTC_VH\\SOURCE\\EM_NLP\\stop-words.txt")
        while True:
            try:
                word=File.next()
                self.stopwords.append(word)
            except StopIteration:
                break

    def loadStopverbs(self):
        self.stopverbs=[]
        File=self.readFile("D:\\BTC_VH\\SOURCE\\EM_NLP\\useless_verb.txt")
        while True:
            try:
                word=File.next()
                self.stopverbs.append(word)
            except StopIteration:
                break


    def loadUselessWords(self):
        self.useless=[]
        File=self.readFile("D:\\BTC_VH\\SOURCE\\EM_NLP\\useless_words.txt")
        while True:
            try:
                word=File.next()
                self.useless.append(word)
            except StopIteration:
                break

    def loadNames(self):
        self.names=[]
        File=self.readFile("D:\\BTC_VH\\SOURCE\\EM_NLP\\name.txt")
        while True:
            try:
                word=File.next()
                self.names.append(word.lower())
            except StopIteration:
                break

    def loadData(self):
        self.Data={}
        wordFile=self.readFile("D:\\BTC_VH\\SOURCE\\EM_NLP\\words.txt")
        coordFile=self.readFile("D:\\BTC_VH\\SOURCE\\EM_NLP\\lsaModel")
        while True:
            try:
                word=wordFile.next()
                coord=coordFile.next()
                self.Data[word]=coord
            except StopIteration:
                break



if __name__=="__main__":
    # p = pickle.Unpickler(open("LSA.pickle", "rb"))
    # data=p.load()
    # print len(data)

    read=readData()
    read.loadQuestion()
    file1= open('questions.pickle', 'wb')
    pickle.dump(read.questions,file1)
    file1.close()

    # read.loadNames()
    # file1= open('names.pickle', 'wb')
    # pickle.dump(read.names,file1)
    # file1.close()
	
    # read.loadStopverbs()
    # file1= open('stop_verbs.pickle', 'wb')
    # pickle.dump(read.stopverbs,file1)
    # file1.close()

    #read.loadStopwords()
    #read.loadUselessWords()
    #stop=set(read.stopwords)
    #useless=set(read.useless)
    #res=stop | useless
    #res=list(res)
    #file2= open('stop_words.pickle', 'wb')
    #pickle.dump(res,file2)
    #file2.close()
    #
    # read.loadData()
    # p = pickle.Pickler(open("LSA.pickle","wb"))
    # p.fast = True
    # p.dump(read.Data)


