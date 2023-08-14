import sys
sys.path.append("BehaviourTree")
from BehaviorTree import *
import time


class askForMail(ConditionNode):
    def __init__(self, name, *args):
        ConditionNode.__init__(self, name)
        self.btTree = args[0]

    def execute(self):
        return False
        #return self.main.Email.askForMail()

    def setMain(self,main):
        self.main=main

class updateUser(ConditionNode):
    def __init__(self, name, *args):
        ConditionNode.__init__(self, name)
        self.btTree = args[0]

    def execute(self):
        self.main.updateUser()
        return True

    def setMain(self,main):
        self.main=main

class quit(ConditionNode):
    def __init__(self, name, *args):
        ConditionNode.__init__(self, name)
        self.btTree = args[0]

    def execute(self):
        return True

    def setMain(self,main):
        self.main=main

class shutUp(ConditionNode):
    def __init__(self, name, *args):
        ConditionNode.__init__(self, name)
        self.btTree = args[0]
        
    def execute(self):
        return self.main.shutup()

    def setMain(self,main):
        self.main=main

class quitEmail(ConditionNode):
    def __init__(self, name, *args):
        ConditionNode.__init__(self, name)
        self.btTree = args[0]

    def execute(self):
        return True

    def setMain(self,main):
        self.main=main

class checkNumPeople(ConditionNode):
    def __init__(self, name, *args):
        ConditionNode.__init__(self, name)
        self.btTree = args[0]

    def execute(self):
        return self.main.checkNumPeople()

    def setMain(self,main):
        self.main=main

class askChatbot(ConditionNode):
    def __init__(self, name, *args):
        ConditionNode.__init__(self, name)
        self.btTree = args[0]
        
    def execute(self):
        self.main.askChatbot()
        return True

    def setMain(self,main):
        self.main=main

class checkFaceEmotion(ConditionNode):
    def __init__(self, name, *args):
        ConditionNode.__init__(self, name)
        self.btTree = args[0]

    def execute(self):
        return self.main.checkFaceEmotion()

    def setMain(self,main):
        self.main=main

class learnKnowledge(ConditionNode):
    def __init__(self, name, *args):
        ConditionNode.__init__(self, name)
        self.btTree = args[0]

    def execute(self):
        return self.main.learnKnowledge()

    def setMain(self,main):
        self.main=main
        
class pardon(ConditionNode):
    def __init__(self, name, *args):
        ConditionNode.__init__(self, name)
        self.btTree = args[0]
        
    def execute(self):
        #return self.main.pardon()
        return False

    def setMain(self,main):
        self.main=main

class askTitle(ConditionNode):
    def __init__(self, name, *args):
        ConditionNode.__init__(self, name)
        self.btTree = args[0]

    def execute(self):
        self.main.Email.askTitle()
        return False

    def setMain(self,main):
        self.main=main
        
class askContent(ConditionNode):
    def __init__(self, name, *args):
        ConditionNode.__init__(self, name)
        self.btTree = args[0]
        
    def execute(self):
        self.main.Email.askContent()
        return False

    def setMain(self,main):
        self.main=main
        
class askWhom(ConditionNode):
    def __init__(self, name, *args):
        ConditionNode.__init__(self, name)
        self.btTree = args[0]
        
    def execute(self):
        self.main.Email.setSender()
        self.main.Email.askWhom()
        return False

    def setMain(self,main):
        self.main=main
        
class initialization(ConditionNode):
    def __init__(self, name, *args):
        ConditionNode.__init__(self, name)
        self.btTree = args[0]
        
    def execute(self):
        self.main.setParameters()
        return False

    def setMain(self,main):
        self.main=main
        
class nobody(ConditionNode):
    def __init__(self, name, *args):
        ConditionNode.__init__(self, name)
        self.btTree = args[0]
        
    def execute(self):
        return self.main.checkUser()

    def setMain(self,main):
        self.main=main
        
class send(ConditionNode):
    def __init__(self, name, *args):
        ConditionNode.__init__(self, name)
        self.btTree = args[0]
        
    def execute(self):
        self.main.Email.send_email()
        return True

    def setMain(self,main):
        self.main=main
        
class updateEmotion(ConditionNode):
    def __init__(self, name, *args):
        ConditionNode.__init__(self, name)
        self.btTree = args[0]
        
    def execute(self):
        self.main.updateEmotion()
        return False

    def setMain(self,main):
        self.main=main
        
class addQuestion(ConditionNode):
    def __init__(self, name, *args):
        ConditionNode.__init__(self, name)
        self.btTree = args[0]
        
    def execute(self):
        self.main.addQuestion()
        return True

    def setMain(self,main):
        self.main=main
        
class known(ConditionNode):
    def __init__(self, name, *args):
        ConditionNode.__init__(self, name)
        self.btTree = args[0]
        
    def execute(self):
        return self.main.Email.notKnown()

    def setMain(self,main):
        self.main=main
        
class repeat(ConditionNode):
    def __init__(self, name, *args):
        ConditionNode.__init__(self, name)
        self.btTree = args[0]
        
    def execute(self):
        return self.main.repeat()

    def setMain(self,main):
        self.main=main
        
class analyzeInput(ConditionNode):
    def __init__(self, name, *args):
        ConditionNode.__init__(self, name)
        self.btTree = args[0]
        
    def execute(self):
        self.main.analyzeInput()
        return False

    def setMain(self,main):
        self.main=main
        
class askMemory(ConditionNode):
    def __init__(self, name, *args):
        ConditionNode.__init__(self, name)
        self.btTree = args[0]
        
    def execute(self):
        return self.main.askMemory()

    def setMain(self,main):
        self.main=main
        
class checkEnd(ConditionNode):
    def __init__(self, name, *args):
        ConditionNode.__init__(self, name)
        self.btTree = args[0]
        
    def execute(self):
        return self.main.checkEnd()

    def setMain(self,main):
        self.main=main

class checkName(ConditionNode):
    def __init__(self, name, *args):
        ConditionNode.__init__(self, name)
        self.btTree = args[0]

    def execute(self):
        return self.main.checkUserName()

    def setMain(self,main):
        self.main=main
        
class noInput(ConditionNode):
    def __init__(self, name, *args):
        ConditionNode.__init__(self, name)
        self.btTree = args[0]
        
    def execute(self):
        return self.main.hasNoInput()

    def setMain(self,main):
        self.main=main
        
class askEmail(ConditionNode):
    def __init__(self, name, *args):
        ConditionNode.__init__(self, name)
        self.btTree = args[0]
        
    def execute(self):
        self.main.Email.askEmail()
        return False

    def setMain(self,main):
        self.main=main
        
class noConfirm(ConditionNode):
    def __init__(self, name, *args):
        ConditionNode.__init__(self, name)
        self.btTree = args[0]
        
    def execute(self):
        return self.main.Email.noConfirm()

    def setMain(self,main):
        self.main=main
        

        

class myBT(BehaviorTree):
    def __init__(self):
        BehaviorTree.__init__(self)
        self.idAssigned = 0
    def setMain(self,main):
        '''set an instance to all nodes in the tree'''
        cls = []
        self.getConditionNodes(cls)
        for node in cls:
            node.setMain(main)
    
    def buildFromFile(self,filename):
        file = open(filename)
        self.treeDict = json.load(file)
        self.__fromDictToTree()
        file.close()

    def __createTreeNode(self,dict):
        node = None
        name = dict['name']
        type = dict['type']
        if type == 'Loop':
            node = LoopNode(name)
        elif type =='Sequence':
            node = SequenceNode(name)
        elif type == 'Parallel':
            node = ParallelNode(name)
        elif type =='Selection':
            node = SelectionNode(name)
        elif type =='Action':
            pass
        else:
            if name == 'updateUser':
                node = updateUser(name, self)
            if name == 'quitEmail':
                node = quitEmail(name, self)
            if name == 'checkFaceEmotion':
                node = checkFaceEmotion(name, self)
            if name == 'pardon':
                node = pardon(name, self)
            if name == 'askForMail':
                node = askForMail(name, self)
            if name == 'askTitle':
                node = askTitle(name, self)
            if name == 'checkNumPeople':
                node = checkNumPeople(name, self)
            if name == 'quit':
                node = quit(name, self)
            if name == 'shutUp':
                node = shutUp(name, self)
            if name == 'askContent':
                node = askContent(name, self)
            if name == 'askWhom':
                node = askWhom(name, self)
            if name == 'send':
                node = send(name, self)
            if name == 'checkName':
                node = checkName(name, self)
            if name == 'updateEmotion':
                node = updateEmotion(name, self)
            if name == 'addQuestion':
                node = addQuestion(name, self)
            if name == 'checkEnd':
                node = checkEnd(name, self)
            if name == 'noInput':
                node = noInput(name, self)
            if name == 'repeat':
                node = repeat(name, self)
            if name == 'askChatbot':
                node = askChatbot(name, self)
            if name == 'initialization':
                node = initialization(name, self)
            if name == 'nobody':
                node = nobody(name, self)
            if name == 'askMemory':
                node = askMemory(name, self)
            if name == 'known':
                node = known(name, self)
            if name == 'learnKnowledge':
                node = learnKnowledge(name, self)
            if name == 'analyzeInput':
                node = analyzeInput(name, self)
            if name == 'askEmail':
                node = askEmail(name, self)
            if name == 'noConfirm':
                node = noConfirm(name, self)
        node.id = self.idAssigned
        self.idAssigned+=1
        return node

    def __DTT(self,dict):
        if dict == self.treeDict:
            self.root = self.__createTreeNode(self.treeDict)
            self.stack.push(self.root)
        for child in dict['children']:
            newNode = self.__createTreeNode(child)
            self.stack.top().addChild(newNode)
            self.stack.push(newNode)
            self.__DTT(child)
            self.stack.pop()

    def __fromDictToTree(self):
        if not self.treeDict:
            pass # empty
        else:
            self.stack.clear()
            self.__DTT(self.treeDict)

if __name__ == "__main__":
    bt = myBT()
    bt.buildFromFile('InteractionBT.json')
    bt.execute()