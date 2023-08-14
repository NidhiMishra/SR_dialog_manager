#####################################################
#                                                   #
#    A python implementation of Behavior Tree       #
#                 Gengdai LIU                       #
#                 2012-12-20                        #
#                                                   #
#####################################################

from TreeNode import *

class LoopNode(TreeNode):
    '''the subtree of loopnode will be executed repeatedly'''
    def __init__(self, nodeName):
        TreeNode.__init__(self, nodeName)
        self.type = NodeType.LOOP
        self.loop = True
        self.loopCount = 0;

    def addChild(self, node):
        ''' 
            override this function in superclass: TreeNode 
            LoopNode can have only one child
        '''
        if len(self.children) == 0:
            self.children.append(node)
            node.parent = self
        else:
            raise Exception('can not add ',node.name,' as a child to ', self.name)

    def insertChild(self, node, i):
        if len(self.children) == 0 and i == 0:
            self.children.append(node)
        else:
            raise Exception('can not insert ',node.name,' as a child to ', self.name)

    def execute(self):
        '''loop'''
        if len(self.children) == 0:
            raise Exception(self.name+': no child')
            return False
        self.loop = True
        while(self.loop):
            result = self.children[0].execute()
            #print self.name, 'executes loop: ', self.loopCount
            self.loopCount+=1 
            if result:
                self.successful = True                               
            else:
                self.successful = False
                if self.parent == None:
                    continue
                else:
                    break
        self.loopCount = 0
        return False # return false always

    def halt(self):
        '''stop looping (stopped after this execution)'''
        self.loop = False
        #print self.name, ' halts'