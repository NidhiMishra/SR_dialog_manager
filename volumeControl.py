from ctypes import cast, POINTER
from comtypes import CLSCTX_ALL
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume

class volumeControl:
    def __init__(self):
        self.devices = AudioUtilities.GetSpeakers()
        self.interface = self.devices.Activate(
              IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
        self.volume = cast(self.interface, POINTER(IAudioEndpointVolume))
        self.readVolume()

    def setVolume(self,vol):
        if isinstance(vol,str):
            if vol in self.volumeSetting.keys():
                self.volume.SetMasterVolumeLevel(self.volumeSetting[vol],None)
        elif any(isinstance(vol,type) for type in [float,int]):
            self.volume.SetMasterVolumeLevel(vol, None)

    def readVolume(self):
        self.volumeSetting={}
        with open("volumeSetting.txt","rb") as file:
            while True:
                line=file.readline()
                if len(line)>0:
                    if line.startswith("#END"):
                        break
                    setting=line.split()
                    self.volumeSetting[setting[0]]=float(setting[1])
            print "Load Volume Setting Done!!!"





if __name__=="__main__":
    control=volumeControl()
    control.setVolume("Chinese")
    control.setVolume(-18)
# Control volume
#volume.SetMasterVolumeLevel(-0.0, None) #max
#volume.SetMasterVolumeLevel(-5.0, None) #72%
#volume.SetMasterVolumeLevel(-10.0, None) #51%
# volume.SetMasterVolumeLevel(-15.0, None) # 36%
