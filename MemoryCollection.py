__author__ = 'Zhang Juzheng'

import os
import Definition
from utils import *
import cPickle as pickle

class MemoryCollection:
    def __init__(self,userName):
        self.episodes=[]
        self.episode=Definition.Episode()
        #self.time_proc=timeUtils()
        #self.sent_proc=sentenceUtils()
        self.getUserName(userName)


    def getUserName(self,userName):
        basepath=os.getcwd()+"\\"+"TrainEpisodes"
        if not os.path.exists(basepath):
            os.makedirs(basepath)

        if userName!="":
            self.user=userName
        else:
            self.user="Unknown"
        self.path=basepath+"\\"+self.user
        if not os.path.exists(self.path):
            os.makedirs(self.path)


    def reset(self):
        self.episode=Definition.Episode()
        #self.time_proc.updateCurrentTime()
        #self.getUserName(self.user)

    def pushEvents(self,attrs):
        event=Definition.Event(attrs)
        self.episode.content.append(event)

    def pushEpisode(self,date):
        self.episode.date=date
        self.episodes.append(self.episode)
        self.reset()

    def saveEpisodes(self,date):
        self.episode.date=date
        self.episodes.append(self.episode)
        filename=time.strftime("%c")+".pickle"
        filename=re.sub(r'''[\:/]''',"-",filename)
        filename=self.path+"\\"+filename
        file=open(filename,'wb')
        pickle.dump(self.episodes,file)
        file.close()