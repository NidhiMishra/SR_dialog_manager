from Tkinter import *
import sys
sys.path.append("gen-py")
sys.path.append("i2p/tools/py")

import Inputs.SpeechGuiService as GUI_Service
from Inputs.ttypes import *
import Inputs.constants

from I2P.ttypes import *
from thrift.transport import TSocket
import ThriftTools
import time

import socket

IP = socket.gethostbyname(socket.gethostname())
print IP

class Application(Frame):
    def start(self):
        self.text=Text(width = 20, height=4, font=("Helvetica",40))
        #self.text.insert(1.0,self.content)
        self.text.pack()

    def editText(self, sentence):
        self.text.delete(1.0,"end")
        self.text.insert(1.0,sentence)
        self.callback=self.text.after(10000,self.clear)

    def clear(self):
        self.text.delete(1.0,"end")
        for name in self.text.tag_names():
            self.text.tag_delete(name)

    def update(self):
        if self.gui_handler.text!=None:
            root.after_cancel(self.callback)
            self.editText(self.gui_handler.text)
            if self.gui_handler.text=="SPEAK AGAIN":
                self.text.tag_add("Again",1.0,"end")
                self.text.tag_config("Again",background="red",foreground="blue")
            self.gui_handler.text=None
        root.after(500, self.update) # every second...


    def __init__(self, master=None):
        Frame.__init__(self, master)
        self.start()
        self.editText("Begin")
        self.gui_handler = GUIHandler()
        self.gui_server = ThriftTools.ThriftServerThread(Inputs.constants.DEFAULT_SPEECHGUI_PORT,GUI_Service,self.gui_handler,'Speech GUI Service','localhost')
        self.gui_server.start()

class GUIHandler:
    def __init__(self):
        self.text=None
        #self.text="SPEAK AGAIN"

    def __del__(self):
        return

    def updateText(self, text):
        print text
        self.text=text


if __name__=="__main__":

    root = Tk()
    app = Application(master=root)
    #app.editText("begin")
    app.update()
    root.mainloop()
    #root.destroy()





            
