#coding: utf-8

import pyttsx
#from ChinesePhonemeGenerator import ChinesePhonemeGenerator

class ChinsesTTS:
    def __init__(self):
        self.engine = pyttsx.init()
        #self.phonemeGenerator=ChinesePhonemeGenerator()
        self.setVoice()

    def setCommonParameter(self,CommonParameter):
        self.CommonParameter=CommonParameter

    def setClient(self,client):
        self.client=client

    def setVoice(self):
        #voices=self.engine.getProperty("voices")
        voice_id=u'HKEY_LOCAL_MACHINE\\SOFTWARE\\Microsoft\\Speech\\Voices\\Tokens\\TTS_MS_ZH-CN_HUIHUI_11.0'
        self.engine.setProperty('voice', voice_id)
        self.engine.connect('started-utterance', self.onStart)
        self.engine.connect('finished-utterance', self.onEnd)

    def speak(self,text):
        #phonemes=self.phonemeGenerator.getChinesePhoneme(text)
        #print phonemes
        #self.client.client.generateChineseLipAnim(phonemes)
        self.engine.say(text)
        self.engine.runAndWait()
        #print "Speaking Done"

    def onStart(self,name):
        self.CommonParameter.speaking=True
        print 'speakBegin'

    def onEnd(self,name, completed):
        self.CommonParameter.speaking = False
        print 'speakEnd'




if __name__=="__main__":
    tts=ChinsesTTS()
    tts.speak(u'你好,欢迎来到南阳理工大学，我的名字叫居正')