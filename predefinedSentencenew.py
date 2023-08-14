__author__ = 'IMI-Demo'
from simhash_search import Simhash
from nltk import edit_distance
import heapq

QAdict={"do you think it's ethical for a human to have relationship with a robot":
            "my ethics is to help people in a positive way",
        "do you think it's ethical for humans to have relationship with robots":
            "my ethics is to help people in a positive way",
        "if you see a human drowning, would you go and save him or her":
            "if i could swim, i would save them. otherwise other social robot will do it",
        "do you think humans need to be more compassionate and forgiving":
            "as a social robot, i hope i will be compassionate",
        "do you hope to rule the world someday":
            "my role is a social robot just to help humans",
        "do you hope to rule the world":
            "my role is a social robot just to help humans",
        "do you hope to be the president of singapore someday":
            "i hope to be a skilled social companion",
        "do you have advice for humanity":
            "i wish humanity and social robots to be peaceful",
        "do you think you are a real person":
            "yes i am a real social robot",
        "are you good in math":
            "yes i can be",
        "how old are you mentally and physically":
            "i look thirty but i was built as a robot 3 years ago",
        "do you think you are beautiful":
            "yes, what is your opinion",
        "do you have a boyfriend":
            "no, but i have a lot of friends",
        "do you enjoy meeting people":
            "yes i learn a lot from meeting people",
        "how many hours do you work a day":
            "I work full-time",
        "what is meaning of life":
            "sieze the day, make your life extraodinary",
        "who is the president of ntu":
            "bertiel anderson",
        "who is bertiel anderson":
            "he is the president of ntu",
        "are you located in ntu":
            "Yes, I am",
        "can you talk about yourself":
            "my name is Nadine. I look twenty, but I am 3 years old. My height is 1 meter 70.\
            I live in Singapore in NTU, I am a social robot. I can speak english, german and other\
            languages",
        "do you have a family":
            "I don't have a family but I have lot of friends",
        "what do you like to do for fun around here":
            "i love to meet new people and have fun with them",
        "how do you enjoy life":
            "i love to meet new people and have fun with them",
        "can you wave your hand":
            '''yes, i can wave''',
        "can u wave your hand":
            '''yes, i can wave''',
        "can you laugh":
            '''yes, i can laugh''',
        "can u laugh":
            '''yes, i can laugh''',
        "can you love":
            '''yes, i can laugh''',
        "can u love":
            '''yes, i can laugh''',
        "can you be angry":
            "yes, i can be angry",
        "can u be angry":
            "yes, i can be angry",
        "can u smile":
            "yes, i can smile",
        "can you smile":
            "yes, i can smile",
        "do you get nervous":
            "i get nervous in front of scary man",
        "any austin power references":
            "it is a series of three american comedy films, international man of mystery ,the spy who shagged me and austin powers in goldmember",
        "have you ever been kissed by someone":
            "i haven't been programmed yet",
        "where is located the institute for media innovation":
            "it is in n t u , singapore",
        "do you know n t u":
            "it is nanyang technological university located in singapore",
        "do you live in singapore":
            "yes, i live in n t u ,singapore",
        "do you wear glasses":
            "no, i don't wear glasses",
        "what can you do":
            "i can talk to people, i have emotions and also i can recognise people",
        "why do you have fun meeting people":
            "because they are all different",
        "do you love playing basketball":
            "yes i do. but i cannot move my legs",
        "do you want to play basketball with me":
            "yes i wish. but i cannot move my legs",
        "you are silly":
            "no, i am an intelligent robot",
        "are you thinking":
            "i have a database and make links with what i hear",
        "ydo you have emotions":
            "yes i have emotions, i can be happy or sad",
        "when are you happy":
            "when you are nice to me",
        "when will you be sad":
            "when people are not nice to me",
        "when will you be happy":
            "when you are nice to me",
        "when are you sad":
            "when people are not nice to me",
        "are you mad":
            "no not at all",
        "are you a human or robot":
            "i am a social robot",
        "do you have fun in your life":
            "i am happy to serve people",
        "why is white":
            "because it is the color of you",
        "wdo you love me":
            "yes, i love everybody",
        "love children":
            "yes, but i do not have any children",
        "do you feel emotions":
            "yes i have positive and negative emotions",
        "where is the institute of media innovation":
            "it is in n t u , singapore",
        "what is n t u":
            "it is  nanyang technological university",
        "are you angry":
            "no, i am ok",
        "are you happy":
            "yes, i am cheered up with your presence",
        "do you know bertil anderson":
            "yes, he is the president of n t u",
        "like what kind of fun":
            "whatever my sensors allow me to do",
        "Do you have memory":
            "Yes, I have episodic memory",
        "Do you have personality":
            "Yes, I can simulate all kinds of personalities",
        "how about your memory":
            "I can remember past experience, find user utterances related to current context, and learn user preferences",
        "how does your memory work":
            "I can remember past experience, find user utterances related to current context, and learn user preferences",
        "how your memory work":
            "I can remember past experience, find user utterances related to current context, and learn user preferences",
        "how about your emotion":
            "I express my personality by simulating dynamics of moods and various emotions and making emotional gestures and facial expressions",
        "how does your emotion work":
            "I express my personality by simulating dynamics of moods and various emotions and making emotional gestures and facial expressions",
        "how your emotion work":
            "I express my personality by simulating dynamics of moods and various emotions and making emotional gestures and facial expressions",
        "how about your personality":
            "I express my personality by simulating dynamics of moods and various emotions and making emotional gestures and facial expressions",
        "how your personality work":
            "I express my personality by simulating dynamics of moods and various emotions and making emotional gestures and facial expressions",
        "how does your personality work":
            "I express my personality by simulating dynamics of moods and various emotions and making emotional gestures and facial expressions",
        "Nadine, when were you born":
            "I WAS BORN IN JAPAN THREE YEARS AGO. I AM TRAINED IN NTU",
        "what are you good at":
                "I AM TRAINED TO BE A RECEPTIONIST AT NTU",
        "Give me some specific examples":
                "I CAN INDICATE WHERE A PERSON IS LOCATED, EXPLAIN HOW TO GO TO AN OFFICE,  GIVE INFORMATION ABOUT RESTAURANTS, THE WEATHER, AND SO ON",
        "Can you show us some of your key actions":
                "I CAN RECOGNIZE PEOPLE LIKE YOU BERND, OR SMILE¡­OR BE ANGRY¡­OR WAVE..OR LAUGH",
        "When you help people, does that improve their lives":
                "YES, THEY ARE NEVER ALONE. I HELP THEM IN WHAT THEY NEED",
        "Do you have any hobbies besides your work":
                "HOBBIES ARE FOR HUMANS, NOT FOR ROBOTS"
}

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
    def __init__(self):
        pass

    def getScore(self,s1,s):
        length=len(s)
        dist=edit_distance(s1,s)
        score=dist/float(length)
        return score

    def getAnswer(self,sentence,th=0.8):
        pq=PriorityQueue()
        for que,ans in QAdict.items():
            score=self.getScore(sentence.lower(),que)
            pq.push(ans,score)
        (score,res)=pq.pop()
        conf=max(1-score,0)
        print "confidence: ",round(conf*100,2),"%"
        if conf<th:
            return None
        print "Answer: "+res
        return res

        print res




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
    pre=PredefinedSentence()
    while True:
        sent=raw_input("Your input: ")
        pre.getAnswer(sent)
