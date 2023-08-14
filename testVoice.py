# from win32com.client import constants
# import win32com.client
# sapi = win32com.client.Dispatch("SAPI.SpVoice")
# sapi.Speak("Hello world!")


import pyttsx
engine = pyttsx.init()
engine.say('Sally sells seashells by the seashore.')
engine.say('The quick brown fox jumped over the lazy dog.')
engine.runAndWait()
