#####################################################
#                                                   #
#    A python implementation of Behavior Tree       #
#                 Gengdai LIU                       #
#                 2012-12-20                        #
#                                                   #
#####################################################

from TreeNode import *

class ConditionNode(TreeNode):
    ''' 
        the condition node of behavior tree
        check external conditions
        a leaf node should be inherited from this class
    '''
    def __init__(self, nodeName):
        TreeNode.__init__(self, nodeName)
        self.type = NodeType.CONDITION

    def addChild(self, node):
        '''it's leaf node, cannot add any child'''
        raise Exception('can not add any child to a leaf node')

    def execute(self):
        '''it should be overrided and implemented by the inherited class'''
        return True