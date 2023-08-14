__author__ = 'Zhang Juzheng'

import re
import string
# from Question import ConfusionWord
# from utils import randomFunc

class chatbot:
    def __init__(self,chat_client):
        self.client=chat_client
        #self.rdmFunc=randomFunc()

    def good_word(self,word):
        for c in word:
            if not c in string.printable:
                return False

        return True

    def clean_string(self,str):
        return ' '.join([w for w in str.split() if self.good_word(w)])

    def reply(self,sentence):
        # if sentence=="NONE":
        #     #if self.rdmFunc.randProb(0.3):
        #     sent=self.rdmFunc.randomChoose(ConfusionWord)
        #     return sent
        reply=self.client.client.chatbot(sentence)
        if reply.lower().startswith("your research topic is"):
            return ""
        if reply:
            reply = re.sub('\(.*?\)','', reply)
            reply = re.sub('\<.*?\>','', reply)
            reply = re.sub('\[.*?\]','', reply)

            Sentences = re.split('[?!.][\s]*',reply)
            if(len( Sentences ) > 2):
                s1 = re.sub('\(.*?\)','', Sentences[0])
                s2 = re.sub('\(.*?\)','', Sentences[1])
                # reply = s1 + ". "+s2+'. '
                if s1==s2:
                    reply=s1+'. '

            reply = self.clean_string(reply)
        return reply

    def getTodayInfo(self):
        try:
            sentDay=self.reply("weather Singapore")
            weather=sentDay.split(':')[1].split(",")[0]+" outside"
            #sentTime=self.reply("time")
            sentDate=self.reply("date")
            answer=sentDate+","+weather
            return answer
        except:
            return self.reply("date")


if __name__=="__main__":
    import sys
    sys.path.append("gen-py")
    sys.path.append("i2p/tools/py")
    import Inputs.ChatbotService as Chat_Service
    import ThriftTools
    import Inputs.constants

    ip_address='155.69.54.42'
    chatbot_client = ThriftTools.ThriftClient(ip_address,Inputs.constants.DEFAULT_CHATBOT_PORT,Chat_Service,'ChatBot')
    while not chatbot_client.connected:
        chatbot_client.connect()
    print "Successfully connect with chatbot"
    bot=chatbot(chatbot_client)
    while True:
        sentence=raw_input("User: ")
        reply=bot.reply(sentence)
        print "Robot: "+reply