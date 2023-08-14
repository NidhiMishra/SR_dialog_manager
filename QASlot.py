__author__ = 'IMI-User'

class QASlot:
    def __init__(self,question,answers,threshold=0.):
        self.question=question
        self.answers=answers
        self.threshold=threshold