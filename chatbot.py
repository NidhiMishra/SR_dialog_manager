import time
import aiml
import sys
import marshal
import os
sys.path.append("gen-py")
sys.path.append("i2p/tools/py")

import Inputs.ChatbotService as Chat_Service
import Inputs.constants

#to ease client server creation in python
import ThriftTools


class ChabotHandler:
    def __init__(self):
        self.kernel = aiml.Kernel()
        self.kernel.learn("std-startup.xml")
        self.kernel.respond("load aiml b")
        self.userName=None
        self.filepath=None
        self.known=False

    def reset(self):
        self.__init__()

    def storeReply(self,replyS):
        if self.known:
            outputHis=self.kernel.getPredicate("_outputHistory",self.userName)
            outputHis.append(replyS)
            self.kernel.setPredicate("_outputHistory",outputHis,self.userName)
        else:
            outputHis=self.kernel.getPredicate("_outputHistory")
            outputHis.append(replyS)
            self.kernel.setPredicate("_outputHistory",outputHis)

    def storeInput(self,inputS):
        if self.known:
            inputHis=self.kernel.getPredicate("_inputHistory",self.userName)
            inputHis.append(inputS)
            self.kernel.setPredicate("_inputHistory",inputHis,self.userName)
        else:
            inputHis=self.kernel.getPredicate("_inputHistory")
            inputHis.append(inputS)
            self.kernel.setPredicate("_inputHistory",inputHis)

    def chatbot(self, sentence):
        if sentence.startswith("User="):
            self.userName=sentence.split("=")[1]
            directory=os.getcwd()+"\\userData"
            self.filepath=directory+"\\"+self.userName+".ses"
            if os.path.isfile(self.filepath):
                print "Loading Historical Chatting Data for " + self.userName
                sessionFile = file(self.filepath, "rb")
                session = marshal.load(sessionFile)
                sessionFile.close()
                self.known=True
                print session
                for pred,value in session.items():
                    print pred, value
                    self.kernel.setPredicate(pred, value, self.userName)
                reply="Welcome back "+self.userName
                self.storeReply(reply)
                return reply   
            else:
                if not os.path.exists(directory):
                    os.mkdir(directory)
                self.kernel.setPredicate("name",self.userName)
                reply="Nice to meet you "+self.userName
                self.storeReply(reply)
                return reply
            
        elif sentence=="save the memory" and self.filepath:
            session=None
            if self.known:
                session = self.kernel.getSessionData(self.userName)
            else:
                session = self.kernel.getSessionData()["_global"]
            #print session
            sessionFile = file(self.filepath, "wb")
            marshal.dump(session, sessionFile)
            sessionFile.close()
            self.reset()
            print "Save OK"
            return "Save OK"
            
        elif sentence.startswith("Input="):
            inputS=sentence.split("=")[1]
            self.storeInput(inputS)
            return "Store input successfully"
            
                
        elif sentence.startswith("Reply="):
            replyS=sentence.split("=")[1]
            self.storeReply(replyS)
            return "Store output successfully"

        else:
            if self.known:
                return self.kernel.respond(sentence,self.userName)
            else:
                return self.kernel.respond(sentence)

if __name__=="__main__":
    chatbot_handler=ChabotHandler()
    # print "load finished"
    # chatbot_handler.reset()
    # print "reset"
    chatbot_server=ThriftTools.ThriftServerThread(Inputs.constants.DEFAULT_CHATBOT_PORT,Chat_Service,chatbot_handler,'Chatbot Service',"155.69.55.254")#155.69.54.42
    chatbot_server.start()

    # while True:
    #     sentence=raw_input("User: ")
    #     reply=chatbot_handler.chatbot(sentence)
    #     if reply:
    #         print "Bot: "+reply
    #     else:
    #         break
        

            




		    

