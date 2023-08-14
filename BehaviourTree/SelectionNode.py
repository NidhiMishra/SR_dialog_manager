#####################################################
#                                                   #
#    A python implementation of Behavior Tree       #
#                 Gengdai LIU                       #
#                 2012-12-20                        #
#                                                   #
#####################################################

from TreeNode import *

class SelectionNode(TreeNode):
    '''priority selector'''
    def __init__(self, nodeName):
        TreeNode.__init__(self, nodeName)
        self.type = NodeType.SELECTION
        self.failedIndex = -1
    
    def execute(self):
        '''select one of the children to execute'''
        if len(self.children) == 0:
            raise Exception(self.name+': no child')
        
        for child in self.children:
            if not child.execute():
                self.failedIndex = child.getIndex()
                continue
            else:
                self.successful = True
                return True

        self.successful = False
        return False