
import smtplib
import re
import os
import time
import sys
import string
from smtplib import SMTPRecipientsRefused,SMTPServerDisconnected
from copy import copy
import utils


class Email:
    def __init__(self):
        self.initParameters()

    def initParameters(self):
        self.email = ['send','email']
        self.stop_words = [ "cancel","stop","stop it",'cancel sending email' , 'stop sending email' , 'discard email', 'abort the email']
        ###############
        self.file_db = "New_Functionality\Email_list.txt"
        self.from_addr = "nadine.imi.ntu@gmail.com"
        self.pwd = 'nadine@ntuimi'
        self.connectServer()

    def connectServer(self):
        print "Connect to Email Server..."
        self.smtpserver = smtplib.SMTP("smtp.gmail.com",587)
        self.smtpserver.ehlo()
        self.smtpserver.starttls()
        #self.smtpserver.ehlo
        self.smtpserver.login(self.from_addr, self.pwd)

    def setMain(self,main):
        self.main=main
    
    def setCommonParameter(self,CommonParameter):
        self.CommonParameter=CommonParameter

    def setSender(self):
        if self.CommonParameter._userName in ["","Unknown"]:
            if self.main.becassineFlag:
                self.sender="Becassine"
            else:
                self.sender = "Nadine"
        else:
            self.sender= copy(self.CommonParameter._userName)

    def correctInput(self,sentence):
        res=utils.processSentence(sentence.lower())
        return res

    def askForMail(self):
        if all(word in self.CommonParameter._userInput for word in ["send","email"]):
            self.CommonParameter._userInput=""
            return True
        return False

    def noStop(self):
        if self.CommonParameter._userInput!="" and any(word in self.CommonParameter._userInput for word in self.stop_words):
            print "Stop sending mail"
            self.main.respond("Okea, I stop it")
            self.CommonParameter._userInput=""
            return False
        time.sleep(0.1)
        return True

    def noConfirm(self):
        while self.main.hasNoInput():
            time.sleep(0.1)
        self.main.emotion=self.main.EmoRecognition.parse(self.CommonParameter._userInput.lower())
        self.main.updateEmotion()
        confirm=self.main.QA.sent_proc.getOpinion(self.CommonParameter._userInput,self.CommonParameter._emotion.pos[0])
        self.CommonParameter._userInput=""
        if confirm:
            return False
        return True

    def getInput(self):
        input=None
        while input==None:
            self.CommonParameter._userInput=""
            while self.main.hasNoInput():
                time.sleep(0.1)
            if self.main.pardon():
                continue
            if self.main.repeat():
                continue
            if self.main.shutup():
                continue
            input=self.correctInput(self.CommonParameter._userInput)
        return input

    def askWhom(self):
        print "Ask Whom to Send Email"
        self.main.respond("To whom do you want to send email")
        self.to_name = self.getInput()
        self.main.respond("The receiver is "+ self.to_name +", right?")
        self.CommonParameter._userInput=""

    def askEmail(self):
        print "Ask Email Address"
        self.main.respond("Could you input the email address?")
        self.emailAddress=raw_input("Please input the email address: ")
        if self.emailAddress.endswith("\n"):
            self.emailAddress=self.emailAddress[:-1]
        self.saveEmail()
        #self.main.Dialogue.reply("The email address is "+ self.emailAddress +", right?")

    def askTitle(self):
        print "Ask Email Title"
        self.main.respond("What is the title?")
        self.title = self.getInput()
        self.main.respond("The title is "+ self.title +", right?")
        self.CommonParameter._userInput=""

    def saveEmail(self):
        with open(self.file_db, "a") as text_file:
            text_file.write("%s : %s" % (self.to_name, self.emailAddress) + "\n")
            print "Email id is saved in the DB" #talk


    def notKnown(self):
        if(os.path.isfile(self.file_db)):
            with open(self.file_db) as f:
                for line in f:
                    line_name = line.split(" :")
                    if (self.to_name == line_name[0]):
                        print "Email matching found"
                        f_score = line.split(": ")
                        print "Email_ID:" ,f_score[1]
                        self.emailAddress=f_score[1]
                        if self.emailAddress.endswith("\n"):
                            self.emailAddress=self.emailAddress[:-1]
                        return False

        print 'Email not found' #talk
        return True





    def askContent(self):
        print "Ask Email Content"
        self.main.respond("What is the content?")
        self.content = self.getInput()
        self.main.respond("The content is "+ self.content +", right?")
        self.CommonParameter._userInput=""

    def write_content(self):
        if self.sender == "Nadine":
            email_sender="Nadine"
        elif self.sender=="Becassine":
            email_sender="Becassine"
        else:
            if self.main.becassineFlag:
                email_sender="Becassine on behalf of "+self.sender
            else:
                email_sender="Nadine on behalf of "+self.sender

        context = string.join((
            "",
            "Dear %s" % self.to_name.capitalize(),
            "",
            self.content.capitalize(),
            "",
            "",
            "Regards",
            email_sender+" \n"
            "",
            "Institute for Media Innovation (IMI)",
            "XFrontiers Block, Level 03-01 ",
            "Nanyang Technological University ",
            "Singapore 637553 ",
            "https://en.wikipedia.org/wiki/Nadine_Social_Robot"
            ), "\r\n")
        return context

    def send_email(self):
        try:
            context = self.write_content()

            BODY = string.join((
                "From: %s" % self.sender,
                "To: %s" % self.emailAddress,
                "Subject: %s" % self.title.capitalize(),
                "",
                context
                ), "\r\n")
            print BODY

            self.smtpserver.sendmail(self.from_addr, self.emailAddress, BODY)
            print 'Mail has been sent!'  #talk
            self.main.respond("Mail has been sent!")
        except SMTPRecipientsRefused:
            print "Could not send email. Kindly check your email address" #talk
            self.main.respond("Could not send email. Kindly check your email address")
        except SMTPServerDisconnected:
            print "The email server is disconnected, try again" #talk
            self.connectServer()
            self.main.respond("The email server is disconnected, try again")
        except:
            print "Unexpected Error: ",sys.exc_info()[0]



		
		
		
		
