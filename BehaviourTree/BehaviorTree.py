#####################################################
#                                                   #
#    A python implementation of Behavior Tree       #
#                 Gengdai LIU                       #
#                 2012-12-20                        #
#                                                   #
#####################################################

from ActionNode import *
from TreeNode import *
from LoopNode import *
from SelectionNode import *
from SequenceNode import *
from ParallelNode import *
from ConditionNode import *
import json

class Stack:
    '''a stack class'''
    def __init__(self):
        self.__stack = []
        self.__num = 0

    def push(self, elem):
        '''push a new element'''
        self.__stack.append(elem)
        self.__num+=1

    def pop(self):
        '''pop the top element if not empty, no return'''
        if self.__num <1:
            raise Exception('the stack is empty')
        self.__stack.pop(-1)
        self.__num-=1

    def top(self):
        '''return the top element'''
        if self.__num<1:
            raise Exception('the stack is empty')
        return self.__stack[-1]

    def empty(self):
        '''check if the stack is empty or not'''
        if self.__num ==0:
            return True
        else:
            return False

    def count(self):
        '''return the count of elements in the stack'''
        return self.__num

    def clear(self):
        '''clear up all elements'''
        self.__stack = []
        self.__num = 0

class BehaviorTree:
    ''' 
        a behavior tree base class
        your own behavior tree class should be inherited from this class
        override function buildTree to create a new tree
    '''
    def __init__(self):
        # root node
        self.root = None
        # a dictionary representation of this behavior tree, which is designed for data exchange
        self.treeDict = {}
        self.stack = Stack()

    def buildTree(self):
        '''you must override this function and build your own behavior tree in it'''
        pass
        
    def __TTD(self, node):
        '''from tree to dictionary, recurse from root'''
        if node == self.root:
            self.treeDict['name'] = node.name
            self.treeDict['type'] = node.type
            self.treeDict['children'] = []
            self.stack.push(self.treeDict)
        for child in node.children:
            newDict={}
            newDict['name']=child.name
            newDict['type']=child.type
            newDict['children']=[]
            self.stack.top()['children'].append(newDict)
            self.stack.push(newDict)
            self.__TTD(child)
            self.stack.pop()

    def __fromTreeToDict(self):
        '''convert behavior tree to a list representation'''
        if self.root == None:
            pass # empty
        else:
            self.treeDict.clear()
            self.stack.clear()
            self.__TTD(self.root)

    def dumpTree(self,filename):
        '''save this behavior tree as a json file'''
        file = open(filename,'w')
        self.__fromTreeToDict()
        file.write(json.dumps(self.treeDict))
        file.close()

    def __getNode(self, node, nodeName, result):
        '''get a node, recursive'''
        for child in node.children:
            self.__getNode(child,nodeName,result)
            if child.name == nodeName:
                result.append(child)

    def getNode(self, nodeName, result):
        '''
        get a node by its name (nodeName)
        result is a null list which should be defined beforehand
        '''
        if nodeName == self.root.name: # if the nodeName is root's name
            result.append(self.root)
            return
        if self.root == None:
            raise Expection('error: root of the behavior tree is not defined')
        return self.__getNode(self.root, nodeName, result)

    def insertNode(self, parentName, node, index):
        '''insert a node under parent node, before the node at index position'''
        parent = []
        self.getNode(parentName, parent)
        parent[0].insert(node, index)

    def removeNode(self, nodeName):
        '''remove a node from the tree'''
        node = []
        self.getNode(nodeName, node)
        parent = node[0].parent
        parent.removeChild(node)

    def __actionCount(self, node, cls):
        ''' compute number of leaf nodes, recursive '''
        if node.type == 'Action':
            cls[0]+=1
        for child in node.children:
            self.__actionCount(child, cls)

    def actionCount(self, countlist):
        ''' 
        get the number of actions (leaf nodes) in the tree
        countlist is a null list which should be defined beforehand
        '''
        countlist.append(0)
        self.__actionCount(self.root,countlist)

    def __nodeCount(self, node, cls):
        cls[0]+=1
        for child in node.children:
            self.__nodeCount(child, cls)

    def nodeCount(self, countlist):
        '''get the number of actions (leaf nodes) in the tree'''
        countlist.append(0)
        self.__nodeCount(self.root,countlist)

    def __actionNodes(self, node, nls):
        if node.type == 'Action':
            nls.append(node)
        for child in node.children:
            self.__actionNodes(child, nls)

    def getActionNodes(self, nls):
        self.__actionNodes(self.root, nls)

    def __conditionNodes(self, node, nls):
        if node.type == 'Condition':
            nls.append(node)
        for child in node.children:
            self.__conditionNodes(child, nls)

    def getConditionNodes(self, nls):
        self.__conditionNodes(self.root, nls)
    
    def execute(self):
        '''execute the behavior tree'''
        if self.root == None:
            raise Expection('error: root of the behavior tree is not defined')
        return self.root.execute()