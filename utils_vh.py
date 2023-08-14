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
#from pycorenlp import StanfordCoreNLP
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

class sentenceUtils:
    def __init__(self):
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
        #os.system('cd G:\yasir_multi_party_code\stanford-corenlp-python\stanford-corenlp-python\stanford-corenlp-full-2016-10-31')
        #os.system('java -mx4g -cp "*" edu.stanford.nlp.pipeline.StanfordCoreNLPServer -port 9000 -timeout 15000')
        #p = subprocess.Popen(['java', '-mx4g', '-cp', "*",'edu.stanford.nlp.pipeline.StanfordCoreNLPServer', '-port', '9000', '-timeout','15000'], cwd='stanford-corenlp-full-2016-10-31',shell=True)
        #p.wait()
        #self.nlp = StanfordCoreNLP('http://localhost:9000')
##        self.nlp.annotate("initiating", properties={
##            'annotators': 'tokenize,ssplit,pos,depparse,parse,coref',
##            'outputFormat': 'json'
##        })
    def shortenSentence(self,sentence):
        if sentence.count(".")+sentence.count(",")>5:
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
        sub_words=["hmmm","er","mhm","hmm","okeam","ur","hm","ummm","umm","uh","um",\
                   "hmmmm","ummmm","whoa","gee","aha","ah"]
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
                   "i have been waiting for you",
                   "i like to listen and be of service",
                    "i'm sensitive to your feelings"

                   ]
        if len(sentence)==0 and sentence in sub_words:
            return True
        for ans in bad_answers:
            if sentence.startswith(ans):
                return True
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
        command = "tts.exe -f 1 -v 0 " + "\"" + input_sentence + "\"" + " -o C:\\Python35-32\\Lib\\site-packages\\googlesamples\\assistant\\grpc\\ga"
        print command
        os.system(command)  # silence 1 0.1 3% 1 3.0 3% trim 0 10
        #command = "python -m googlesamples.assistant.grpc.pushtotalk -i C:\\Users\\IMI-User\\Anaconda2\\Lib\\site-packages\\googlesamples\\assistant\\grpc\\ga0.wav -o C:\\Users\\IMI-User\\Anaconda2\\Lib\\site-packages\\googlesamples\\assistant\\grpc\\assistant_reply.wav"
        #os.system(command)
    def coreferencecorrection(self,input_sentence):

        text = input_sentence[0] + '. ' + input_sentence[1] + '.'  # "I am yasir. I am 28 years old."
        output = self.nlp.annotate(text, properties={
            'annotators': 'tokenize,ssplit,pos,depparse,parse',
            'outputFormat': 'json'
        })
        #if 'FRAG' in output['sentences'][1]['parse']:
            #return "incomplete"

        text2 = list(text)  # finditer
        for m in re.finditer('N(?:NP|NS|N)', output['sentences'][0]['parse']):
            #print(text2[text.find(output['sentences'][0]['parse'][(m.end() + 1):((m.end() + 3))])])
            text2[text.find(output['sentences'][0]['parse'][(m.end() + 1):((m.end() + 3))])] = text2[
                text.find(output['sentences'][0]['parse'][(m.end() + 1):((m.end() + 3))])].upper()
            # text=text[0:(text.find(output['sentences'][0]['parse'][(m.end()+1):((m.end()+3))])-1)]+text[text.find(output['sentences'][0]['parse'][(m.end()+1):((m.end()+3))])].upper()+text[(text.find(output['sentences'][0]['parse'][(m.end()+1):((m.end()+3))])+1):]
        text = ''.join(text2)

        output = self.nlp.annotate(text, properties={
            'annotators': 'tokenize,ssplit,pos,depparse,parse,coref',
            'outputFormat': 'json'
        })

        input_sentence_new = input_sentence[1]
        corefs = output['corefs']
        for cor in corefs:
            min_id = 10
            use_index = 1
            #print(len(corefs[cor]))
            if len(corefs[cor]) > 1:
                for i, e in enumerate(corefs[cor]):
                    if ((corefs[cor][i]['sentNum'] == 2) & (corefs[cor][i]['id'] < min_id)):
                        min_id = corefs[cor][i]['id']
                        use_index = i

                        # if len(corefs[cor])>1:
                # for i, e in enumerate(corefs[cor]):
                if ((corefs[cor][0]['isRepresentativeMention'] == True) &
                        (corefs[cor][use_index]['isRepresentativeMention'] == False)) & (
                    (corefs[cor][0]['sentNum'] == 1) & (corefs[cor][use_index]['sentNum'] == 2)) & (
                    corefs[cor][0]['type'] != corefs[cor][use_index]['type']):
                    input_sentence_new = re.sub(r'\b%s\b' % str(corefs[cor][use_index]['text'])
                                                , str(corefs[cor][0]['text']), input_sentence_new)
                    # text_new=input_sentence[0]+'. '+re.sub(r'\b%s\b'% str(corefs[cor][use_index]['text'])
                    # ,str(corefs[cor][0]['text']), input_sentence[1])+'.'
                    #print()
                    # else:
                    # text_new=text

        text_new = input_sentence[0] + '. ' + input_sentence_new + '.'  # string.replace(text,coref_str,noun)
        #print(text_new)
        text_new = ''
        return input_sentence_new


if __name__=="__main__":

    gender=Gender()
    gender.loadGender()
    gender.userGender["Vanessa"]="female"
    print gender.userGender
    gender.saveGender()

    # sent_proc=sentenceUtils()
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


