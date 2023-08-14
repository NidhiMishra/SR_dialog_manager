import sys
sys.path.append('gen-py')

from Tkinter import *
import zjz_speech.SpeechInput as ss
from zjz_speech.ttypes import *

import zjz_face.FaceInput as fs
from zjz_face.ttypes import *

from thrift.transport import TTransport
from thrift.transport import TSocket
from thrift.protocol import TBinaryProtocol
from thrift.protocol import TCompactProtocol

Emotions = ['HOPE','FEAR','SATISFACTION','FEAR_CONFORMED','DISAPPOINTMENT','RELIEF','JOY','DISTRESS','GRATIFICATION','REMORSE','PRIDE','SHAME']
Animations = ['WAVE_HAND','SHAKE_HANDS','STAND_UP','SIT_DOWN','ROCK','PAPER','SCISSOR','RIGHT_SWEEP','POINTING_YOU','WHY','HAND_ON_HIP','OFFER','RIGHT_STRONG_SWEEP', 'NOD_YES','NOD_NO','DONT_KNOW']
Face_Expressions = ['NEUTRAL','ANGER','DISGUST','FEAR','HAPPINESS','SADNESS','SURPRISE']


class Application(Frame):
        def createWidgets(self):
                self.Registration = Button(self, text="Registration")
                self.Registration["command"] =  self.registration
                self.Registration.grid(row=1, column=1)


                self.YES = Button(self, text="Yes")
                self.YES["command"] =  self.yes
                self.YES.grid(row=3, column=1)

                self.NO = Button(self, text="NO")
                self.NO["command"] =  self.no
                self.NO.grid(row=4, column=1)

                self.Load_User = Button(self, text="Load User")
                self.Load_User["command"] =  self.load_user
                self.Load_User.grid(row=5, column=1)

                self.Zerrin = Button(self, text="Nationality=Turkey")
                self.Zerrin["command"] =  self.zerrin
                self.Zerrin.grid(row=6, column=1)

                self.James_Nation = Button(self, text="Nationality=Chinese")
                self.James_Nation["command"] =  self.james_nation
                self.James_Nation.grid(row=7, column=1)

                self.James_Pos = Button(self, text="Position=Phd")
                self.James_Pos["command"] =  self.james_pos
                self.James_Pos.grid(row=8, column=1)

                self.James_Name = Button(self, text="Name=Zhang")
                self.James_Name["command"] =  self.james_name
                self.James_Name.grid(row=9, column=1)
                
                self.pack()

        def registration(self):
                print "Register No. "+self.user_id+" user"
                self.face_service.send_recog_user(self.user_id)
        
        def yes(self):
                print "Yes"
                self.speech_service.send_choice(1)
                
        def no(self):
                print "No"
                self.speech_service.send_choice(2)
                
        def load_user(self):
                print "load_user: Name="+self.user_name+", Nationality="+\
                      self.user_nationality+", School="+\
                      self.user_school+", Position="+self.user_position
                self.speech_service.send_name(self.user_name)
                self.speech_service.send_nationality(self.user_nationality)
                self.speech_service.send_school(self.user_school)
                self.speech_service.send_position(self.user_position)
                
        def zerrin(self):
                print "send: Nationality="+self.cue_1_nationality
                self.speech_service.send_nationality(self.cue_1_nationality)
                
        def james_nation(self):
                print "send: Nationality="+self.cue_2_nationality
                self.speech_service.send_nationality(self.cue_2_nationality)
                
        def james_pos(self):
                print "send: Position="+self.cue_2_position
                self.speech_service.send_position(self.cue_2_position)
                
        def james_name(self):
                print "send: Name="+self.cue_2_name
                self.speech_service.send_name(self.cue_2_name)
                
        
        
        def __init__(self, master=None):
                Frame.__init__(self, master)
                self.createWidgets()
                # Open speech_client
                self.speech_transport = TSocket.TSocket('localhost', 9099)
                self.speech_transport = TTransport.TBufferedTransport(self.speech_transport)
                self.speech_protocol = TBinaryProtocol.TBinaryProtocol(self.speech_transport)
                self.speech_transport.open()
                self.speech_service = ss.Client(self.speech_protocol)

                #open face_client
                self.face_transport = TSocket.TSocket('localhost', 9098)
                self.face_transport = TTransport.TBufferedTransport(self.face_transport)
                self.face_protocol = TBinaryProtocol.TBinaryProtocol(self.face_transport)
                self.face_transport.open()
                self.face_service = fs.Client(self.face_protocol)

                self.user_name="James"
                self.user_nationality="Chinese"
                self.user_school="SPMS"
                self.user_position="Phd"
                self.cue_1_nationality="Turkey"
                self.cue_2_nationality="Chinese"
                self.cue_2_name="Zhang"
                self.cue_2_position="Phd"
                self.user_id="22"
                

root = Tk()
app = Application(master=root)
app.mainloop()
root.destroy()
