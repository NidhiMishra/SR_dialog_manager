__author__ = 'IMI-Demo'

from nltk import edit_distance
import heapq
from AIMLReader import AIMLReader
import os
from utils import randomFunc


class PriorityQueue:
    """
      Implements a priority queue data structure. Each inserted item
      has a priority associated with it and the client is usually interested
      in quick retrieval of the lowest-priority item in the queue. This
      data structure allows O(1) access to the lowest-priority item.

      Note that this PriorityQueue does not allow you to change the priority
      of an item.  However, you may insert the same item multiple times with
      different priorities.
    """
    def  __init__(self):
        self.heap = []
        self.count = 0

    def push(self, item, priority):
        # FIXME: restored old behaviour to check against old results better
        # FIXED: restored to stable behaviour
        entry = (priority, self.count, item)
        # entry = (priority, item)
        heapq.heappush(self.heap, entry)
        self.count += 1

    def pop(self):
        (score,_,item) = heapq.heappop(self.heap)
        #  (_, item) = heapq.heappop(self.heap)
        return (score,item)

    def isEmpty(self):
        return len(self.heap) == 0

class PredefinedSentence:
    def __init__(self,loadAIML=True):
        self.filter=["who is the president of turkey"]
        self.randomTool=randomFunc()
        if loadAIML:
            self.reader=AIMLReader()
            self.QAdict=self.reader.read(os.getcwd()+"\\AIML\\z_predefined.aiml")
            print "Loaded predefined sentences"
        else:
            self.QAdict={}

    def getScore(self,s1,s):
        length=len(s)
        dist=edit_distance(s1,s)
        score=dist/float(length)
        return score


    def getAnswer(self,sentence,th=0.9):
        sentence=sentence.lower()
        if sentence in self.filter:
            return None
        pq=PriorityQueue()
        for que,ans in self.QAdict.items():
            score=self.getScore(sentence,que)
            pq.push(ans,score)
        (score,res)=pq.pop()
        conf=max(1-score,0)
        print "confidence: ",round(conf*100,2),"%"
        if conf<th:
            return None
        res=self.randomTool.randomChoose(res)
        print "Answer: "+res
        return res





# class PredefinedSentence:
#     def __init__(self):
#         self.hash=Simhash()
#         self.hash.init_load_sentence(QAdict.keys())
#
#
#     def getAnswer(self,sentence,th=0.8):
#         idx,conf = self.hash.search_top(sentence)
#         print "confidence: ",round(conf*100,2),"%"
#         if conf<th:
#             return None
#         res=QAdict.values()[idx]
#         print "Answer: "+res
#         return res

if __name__=="__main__":
    # from AIMLWritter import AIMLWriter
    # writer=AIMLWriter()
    # writer.writeAIMLFile(QAdict)

    pre=PredefinedSentence()
    while True:
        sent=raw_input("Your input: ")
        pre.getAnswer(sent)
