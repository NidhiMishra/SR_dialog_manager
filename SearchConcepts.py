#! /usr/bin/env python

import cPickle as pickle
import networkx as nx
from nltk.stem.porter import PorterStemmer
import enchant
from textblob import TextBlob
from nltk import word_tokenize, pos_tag
import sys


class SearchConcepts:
    def __init__(self):
        self.G = nx.read_gpickle( "test.gpickle" )
        self.stemmer=PorterStemmer()
        self.dic = enchant.Dict("en_US")
        self.threshold=0
        self.polarityDict=pickle.load(open('polarityDict.pickle','rb'))
        self.polarityDict["dummy"]=-1
        self.polarityDict["silly"]=-1



    def stem(self,word):
        try:
            str = self.stemmer.stem(word)
            str=str.encode('ascii')

            if self.dic.check(str):
                return str
            else:
                if str.endswith("i"):
                    guess=str[0:-1]+"y"
                    if self.dic.check(guess):
                        #print str+" -->  ",
                        str=guess
                        #print str
                        return str
                if str.endswith("l"):
                    guess=str+"l"
                    if self.dic.check(guess):
                        #print str+" -->  ",
                        str=guess
                        #print str
                        return str
                guess=str+"e"
                if self.dic.check(guess):
                    #print str+" -->  ",
                    str=guess
                    #print str
                    return str

            return word

        except:
            return word

    def checkQuestion(self,TaggedSentence):
        try:
            firstTag=TaggedSentence[0][1]
            firstWord=TaggedSentence[0][0]
            secondTag=TaggedSentence[1][1]
            questionWord=["did","does","how","who","when","what","is","are","was","were",\
                          "had","will","would","shall","should","can","could","may","might"]
            if firstWord in questionWord:
                return True
            elif firstWord in ["do","have"] and (secondTag =="PRP" or secondTag.startswith("NN")):  # do you
                return True
            elif firstWord in ["which","what","how"]: # how nice you are
                if secondTag not in ["JJ","DT"]:
                    return True
                else:
                    return False
            else:
                return False
        except:
            print sys.exc_info()
            return False


    def parse(self, sentence):
        bigrams = []
        sent=TextBlob(sentence)
        words = sent.tokens
        #words=word_tokenize(sentence)

        list_concepts = []
        conc = []
        to_add = ""
        referToAgent=False
        referToSelf=False
        reverse=False
        question=False
        
        if len(words)>1:
            TaggedSentence=sent.tags
            #TaggedSentence=pos_tag(words)
            question=self.checkQuestion(TaggedSentence)
        


        for word in words:
            if word in ["not","n't","never","hardly"]:
                reverse=not reverse
            if word in ["you","your"]:
                referToAgent=True
            if word in ["i","me","my"]:
                referToSelf=True
            if ( word in self.G or word in ["dummy"]):
              conc.append(word)
              to_add = to_add+ word+" "
              #print to_add

            else:
                stemWord=self.stem(word)
                if stemWord in self.G or stemWord in ["dummy"]:
                    conc.append(stemWord)
                    to_add = to_add+ stemWord+" "
                else:
                    if( to_add != "" ):
                        list_concepts.append(to_add[:-1])
                        to_add = ""


        if( to_add != "" ):
           list_concepts.append(to_add[:-1])


        list_concept = list_concepts

        list_concept = filter(bool, list_concept)

        list_concept = set(list(list_concepts))


        to_search = []


        for phrase in list_concepts:
           concepts = phrase.split()
           to_search = to_search + concepts
##           for i in range(len(concepts) - 1):
##              for j in range(i+1, len(concepts)):
##                 try:
##                    k = nx.dijkstra_path(self.G,concepts[i], concepts[j])
##                    #print k
##                    if( len(k) == j-i+1 and k == concepts[i:j+1] ):
##                       to_search = list( set(to_search) - set(k) )
##                       word_to_add = "_".join(k)
##                       to_search.append( word_to_add )
##
##                 except:
##                    continue



        to_search = list( set(  to_search ) )


        #print to_search

        totalPolarity=0
        for concept in to_search:
            if concept in self.polarityDict.keys():
                totalPolarity+=self.polarityDict[concept]


        if reverse:
            totalPolarity=-totalPolarity
        if totalPolarity>1:
            totalPolarity=1
        elif totalPolarity<-1:
            totalPolarity=-1


        if totalPolarity>self.threshold:
            totalPolarity=2*totalPolarity
            if not question:
                if referToAgent:
                    return "GRATITUDE "+str(totalPolarity)
                elif referToSelf:
                    return ("HAPPYFOR "+str(totalPolarity))
                else:
                    return "JOY "+str(totalPolarity)
                
        elif totalPolarity< -self.threshold:
            totalPolarity=2*totalPolarity
            if not question:
                if referToAgent:
                    return "ANGER "+str(-totalPolarity)
                elif referToSelf:
                    return "PITY "+str(-totalPolarity)
                else:
                    return "DISTRESS "+str(-totalPolarity)
        
        return None



if __name__=="__main__":
    search=SearchConcepts()
    while True:
        sentence = raw_input("Enter your search sentence ===>> " ).lower()
        print search.parse(sentence)
