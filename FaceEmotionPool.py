__author__ = 'IMI-User'
from dataStructure import PriorityQueue
import FaceResponses
import time
import random

class FaceEmotion:
    def __init__(self,label,numFrames):
        self.label=label
        self.numFrames=numFrames
        self.values=[]

    def getAverage(self):
        if len(self.values)<self.numFrames:
            return 0
        val=sum(self.values)/float(len(self.values))
        return val

    def update(self,val,winEmo=None):
        if winEmo!=None and self.label!=winEmo:
            val=0
        while len(self.values)>=self.numFrames:
            self.values.pop(0)
        self.values.append(val)


class FaceEmotionPool:
    def __init__(self,numPreviousFrames,threshold,coolTime):
        self.numPreviousFrames=numPreviousFrames # check previous frames to confirm an emotion
        self.threshold=threshold # threshold for emotion activation
        self.coolTime=coolTime
        self.reset(True)
        self.probDiscount=0
        self.initialization()

    def reset(self,flag=False):
        print "Reset Face Emotion Detection!!!\n"
        self.activeEmo=None
        self.hasNew=False
        self.start=time.time()
        if flag:
            self.lastActiveEmo=None
            self.reportProb=1


    def initialization(self):
        self.gender="Unknown"
        self.emoPool=[]
        self.emoPool.append(FaceEmotion("Joy",self.numPreviousFrames))
        self.emoPool.append(FaceEmotion("Fear",self.numPreviousFrames))
        #self.emoPool.append(FaceEmotion("Disgust",self.numPreviousFrames))
        self.emoPool.append(FaceEmotion("Sadness",self.numPreviousFrames))
        self.emoPool.append(FaceEmotion("Anger",self.numPreviousFrames))
        #self.emoPool.append(FaceEmotion("Surprise",self.numPreviousFrames))
        #self.emoPool.append(FaceEmotion("Contempt",self.numPreviousFrames))
        # self.emoPool.append(FaceEmotion("Smile",self.numPreviousFrames))
        # self.emoPool.append(FaceEmotion("Valence",self.numPreviousFrames))
        # self.emoPool.append(FaceEmotion("Engagement",self.numPreviousFrames))

    def compete(self,userFaceEmotion):
        queue=PriorityQueue()
        inputs={"Joy":userFaceEmotion.joy,
                "Fear":userFaceEmotion.fear,
                #"Disgust":userFaceEmotion.disgust,
                "Sadness":userFaceEmotion.sadness,
                "Anger": userFaceEmotion.anger,
                #"Surprise":userFaceEmotion.surprise,
                #"Contempt":userFaceEmotion.contempt
                }
        for emo, intensity in inputs.items():
            queue.push(emo,-intensity)
        winEmo=queue.pop()
        return winEmo


    def update(self,userFaceEmotion):
        self.gender=userFaceEmotion.gender
        # update emotion activity
        activityQueue=PriorityQueue()
        winEmo=self.compete(userFaceEmotion) # only update the intensity of the emotion that wins
        for emo in self.emoPool:
            if emo.label=="Joy":
                emo.update(userFaceEmotion.joy,winEmo)
                activityQueue.push(emo.label,-emo.getAverage())
            elif emo.label=="Fear":
                emo.update(userFaceEmotion.fear,winEmo)
                activityQueue.push(emo.label,-emo.getAverage())
            # elif emo.label=="Disgust":
            #     emo.update(userFaceEmotion.disgust,winEmo)
            #     activityQueue.push(emo.label,-emo.getAverage())
            elif emo.label=="Sadness":
                emo.update(userFaceEmotion.sadness,winEmo)
                activityQueue.push(emo.label,-emo.getAverage())
            elif emo.label=="Anger":
                emo.update(userFaceEmotion.anger,winEmo)
                activityQueue.push(emo.label,-emo.getAverage())
            # elif emo.label=="Surprise":
            #     emo.update(userFaceEmotion.surprise,winEmo)
            #     activityQueue.push(emo.label,-emo.getAverage())
            # elif emo.label=="Contempt":
            #     emo.update(userFaceEmotion.contempt,winEmo)
            #     activityQueue.push(emo.label,-emo.getAverage())

        # find active emotion
        while not activityQueue.isEmpty():
            win_label,win_activity=activityQueue.pop_full()
            win_activity=-win_activity
            if win_activity > self.threshold:
                passedTime=time.time()-self.start
                if win_label!=self.activeEmo and passedTime>self.coolTime:
                    self.activeEmo=win_label
                    if self.activeEmo!=self.lastActiveEmo:
                        self.reportProb=1
                    else:
                        self.reportProb=self.probDiscount*self.reportProb
                    self.lastActiveEmo=self.activeEmo
                    self.hasNew=True
                    print "Get Dominant Face Emotion: %s\n" %win_label
                    self.start=time.time()
                    break
            break

    def process(self,userFaceEmotion):
        if self.checkStopMsg(userFaceEmotion):
            self.initialization()
        else:
            self.update(userFaceEmotion)


    def checkStopMsg(self,userFaceEmotion):
        if userFaceEmotion.joy<-1:
            return True
        return False

    def replyToGender(self):
        if self.activeEmo=="Joy":
            if self.gender=="Male":
                return ["You look like a happy man"]
            elif self.gender=="Female":
                return ["You look like a happy lady"]
        return None

    def getEmotionalSentences(self,startInteractFlag,curMood):
        _interaction="beforeInteraction"
        if startInteractFlag:
            _interaction="duringInteraction"
        _mood="goodMood"
        if curMood<-0.4:
            _mood="badMood"

        mEmotion=FaceResponses.FaceEmotionResponse[self.activeEmo][_mood]
        # just added for gender
        if self.activeEmo=="Joy":
            mSentences=self.replyToGender()
            if mSentences!=None:
                return mEmotion,mSentences
        # normal reactions
        if _interaction=="beforeInteraction":
            mSentences=FaceResponses.FaceSentenceResponses[self.activeEmo][_interaction]
        else:
            mSentences=FaceResponses.FaceSentenceResponses[self.activeEmo][_interaction][_mood]
        return mEmotion,mSentences