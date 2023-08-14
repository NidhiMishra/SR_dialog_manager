# -*- coding: utf-8 -*-
"""
Created on Mon Sep 17 11:45:31 2018

@author: IMI-Ranjan
"""
import wave
import contextlib
from mutagen.mp3 import MP3
from Mic_Controller import AudioUtilities
import os

class AudioDuration:
    def __init__(self, fname,):
        self.fname = (fname)
        #self.age = age
    
    def len(self):
        #With contextlib.closing(wave.open(r"englishSpeech.wav",'r')) as f:
        if ".wav" in self.fname:
            with contextlib.closing(wave.open((self.fname),'r')) as f:
                frames = f.getnframes()
                rate = f.getframerate()
                duration = frames / float(rate)
                #print(duration)
        elif ".mp3" in self.fname:
            audio = MP3(self.fname)
            #print (audio.info.length)
            duration = audio.info.length

        return duration

            
            
#from framelen import framelength
#fl = framelength()
#fl.len()

#Audio_prop = AudioDuration("G:\\IMI-PROJECTS\\i2p_Nadine_Robot\\development\\i2p_interaction\\i2p_nadine_control\\build\\lipAnim.wav")
#Audio_Dur = Audio_prop.len()

# Main Entry Point
# This example mutes the mic for three seconds, the unmutes the mic
if __name__ == "__main__":
    from time import sleep  # DO NOT USE THIS FOR FINAL VERSION. SLEEP IS BLOCKING
    print("Mutes the microphone during Nadine Speech")
    # Create a Microphone controller object
    test_audio_control = AudioUtilities()
    test_audio_control.UnMuteMicrophone()
    while os.path.exists("process_mic_mute.txt"):
        try:
            os.remove("process_mic_mute.txt")
        except:
            continue
    try:
        while True:
            if os.path.exists("mic_mute.txt"):
                print("Mic_mute exists!!!")
                # Create a Microphone controller object
                #test_audio_control = AudioUtilities()

                #read the file
                mic_control = open("mic_mute.txt","r")
                duration = mic_control.read()
                mic_control.close()
                os.remove("mic_mute.txt")
                print(duration)
                # Mute the Microphone
                test_audio_control.MuteMicrophone()
                # sleep for 3 seconds for testing purposes
                sleep(float(duration))
                test_audio_control.UnMuteMicrophone()
                # Microphone Unmuted. Done with this example,
            if os.path.exists("process_mic_mute.txt"):
                if not test_audio_control.is_muted:
                    print("Microphone muted as Nadine is processing user query")
                    test_audio_control.MuteMicrophone()
                    sleep(1)
    except:
        test_audio_control = AudioUtilities()
        test_audio_control.UnMuteMicrophone()