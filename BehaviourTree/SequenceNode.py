#####################################################
#                                                   #
#    A python implementation of Behavior Tree       #
#                 Gengdai LIU                       #
#                 2012-12-20                        #
#                                                   #
#####################################################

from TreeNode import *

class SequenceNode(TreeNode):
    '''the children of sequence node will be executed one by one'''
    def __init__(self, nodeName):
        TreeNode.__init__(self, nodeName)
        self.type = NodeType.SEQUENCE
        self.finishedCount = 0
        self.startIndex = 0
        self.failedIndex = -1

    def execute(self):
        '''execute one by one'''
        if len(self.children) == 0:
            raise Exception(self.name+': no child')
            return False
        for child in self.children[self.startIndex:]:
            if not child.execute():
                self.successful = False
                self.failedIndex = child.getIndex()
                return False
            self.finishedCount += 1
        #print self.name, ' finished execution'
        return True

    def startFrom(self, idx):
        '''start executing from which child'''
        if idx < 0 or idx >= self.childrenCount():
            raise Exception('can not start from ', idx, 'th child of ', self.nodename, ' because it is out of range')
        self.startIndex = idx