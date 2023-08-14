#####################################################
#                                                   #
#    A python implementation of Behavior Tree       #
#                 Gengdai LIU                       #
#                 2012-12-20                        #
#                                                   #
#####################################################

from TreeNode import *

class ActionNode(TreeNode):
    ''' 
        the action node of behavior tree, including actual behaviors being executed 
        a leaf node should be inherited from this class
    '''
    def __init__(self, nodeName):
        TreeNode.__init__(self, nodeName)
        self.type = NodeType.ACTION

    def addChild(self, node):
        '''it's leaf node, cannot add any child'''
        raise Exception('can not add any child to a leaf node')

    def execute(self):
        '''it should be overrided and implemented by the inherited class'''
        return True