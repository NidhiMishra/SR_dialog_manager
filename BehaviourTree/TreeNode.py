#####################################################
#                                                   #
#    A python implementation of Behavior Tree       #
#                 Gengdai LIU                       #
#                 2012-12-20                        #
#                                                   #
#####################################################

def enum(**enums):
    '''define enum'''
    return type('Enum', (), enums)
# NodeType
NodeType = enum(LOOP='Loop', PARALLEL='Parallel', SELECTION='Selection', SEQUENCE='Sequence', ACTION = 'Action', CONDITION = 'Condition')
# Status of a node
Status = enum(READY='Ready', RUNNING='Running', FINISH='Finish')

class TreeNode:
    '''base class for all tree node'''
    def __init__(self, nodeName):
        self.name = nodeName
        self.children = []
        self.parent = None
        self.successful = False
        self.status = Status.READY
        self.id = -1

    def addChild(self, node):
        '''add a child to the end'''
        self.children.append(node)
        node.parent = self

    def insertChild(self, node, i):
        '''insert a child before element i'''
        self.children.insert(i, node)

    def removeChild(self, node):
        '''remove child - node from its children list'''
        self.children.remove(node)

    def childrenCount(self):
        '''get number of children'''
        return len(self.children)

    def getIndex(self):
        '''get index in all siblings'''
        index = 0
        if self.parent!= None:
            index = self.parent.children.index(self)
        return index

    def isSucceeded(self):
        return self.successful

    def execute(self):
        pass

    def halt(self):
        pass