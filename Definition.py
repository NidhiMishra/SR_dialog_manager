__author__ = 'Zhang Juzheng'

class Attribute:
    def __init__(self,content,type,coord=None):
        self.content=content
        self.coordinate=coord
        self.type=type
    def __del__(self):
        return

class Event:
    def __init__(self,content,coord=None,categoryIdx=None):
        self.content=content
        self.coordinate=coord
        self.category=categoryIdx
        self.index=None

    def __del__(self):
        return

class Episode:
    def __init__(self,content=[],coord=None,categoryIdx=None):
        self.content=content
        self.eventClusterIdx=None
        self.coordinate=coord
        self.category=categoryIdx
        self.maxEvIdx=None
        self.date=None
        self.index=None

    def __del__(self):
        return

from enum import Enum

class Attr(Enum):
    SENTENCE=1
    USER=2
    EMOTION=3
    MOOD=4
    STATE=5




