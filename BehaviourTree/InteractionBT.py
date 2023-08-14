from BehaviorTree import *
import time
        
class updateUser(ConditionNode):
    def __init__(self, name, *args):
        ConditionNode.__init__(self, name)
        self.btTree = args[0]
        
    def execute(self):
        return False
        
class quitEmail(ConditionNode):
    def __init__(self, name, *args):
        ConditionNode.__init__(self, name)
        self.btTree = args[0]
        
    def execute(self):
        return False
        
class checkFaceEmotion(ConditionNode):
    def __init__(self, name, *args):
        ConditionNode.__init__(self, name)
        self.btTree = args[0]
        
    def execute(self):
        return False
        
class askForMail(ConditionNode):
    def __init__(self, name, *args):
        ConditionNode.__init__(self, name)
        self.btTree = args[0]
        
    def execute(self):
        return False
        
class askTitle(ConditionNode):
    def __init__(self, name, *args):
        ConditionNode.__init__(self, name)
        self.btTree = args[0]
        
    def execute(self):
        return False
        
class quit(ConditionNode):
    def __init__(self, name, *args):
        ConditionNode.__init__(self, name)
        self.btTree = args[0]
        
    def execute(self):
        return False
        
class shutUp(ConditionNode):
    def __init__(self, name, *args):
        ConditionNode.__init__(self, name)
        self.btTree = args[0]
        
    def execute(self):
        return False
        
class pardon(ConditionNode):
    def __init__(self, name, *args):
        ConditionNode.__init__(self, name)
        self.btTree = args[0]
        
    def execute(self):
        return False
        
class askContent(ConditionNode):
    def __init__(self, name, *args):
        ConditionNode.__init__(self, name)
        self.btTree = args[0]
        
    def execute(self):
        return False
        
class askWhom(ConditionNode):
    def __init__(self, name, *args):
        ConditionNode.__init__(self, name)
        self.btTree = args[0]
        
    def execute(self):
        return False
        
class send(ConditionNode):
    def __init__(self, name, *args):
        ConditionNode.__init__(self, name)
        self.btTree = args[0]
        
    def execute(self):
        return False
        
class updateEmotion(ConditionNode):
    def __init__(self, name, *args):
        ConditionNode.__init__(self, name)
        self.btTree = args[0]
        
    def execute(self):
        return False
        
class checkName(ConditionNode):
    def __init__(self, name, *args):
        ConditionNode.__init__(self, name)
        self.btTree = args[0]
        
    def execute(self):
        return False
        
class addQuestion(ConditionNode):
    def __init__(self, name, *args):
        ConditionNode.__init__(self, name)
        self.btTree = args[0]
        
    def execute(self):
        return False
        
class checkEnd(ConditionNode):
    def __init__(self, name, *args):
        ConditionNode.__init__(self, name)
        self.btTree = args[0]
        
    def execute(self):
        return False
        
class noInput(ConditionNode):
    def __init__(self, name, *args):
        ConditionNode.__init__(self, name)
        self.btTree = args[0]
        
    def execute(self):
        return False
        
class checkNumPeople(ConditionNode):
    def __init__(self, name, *args):
        ConditionNode.__init__(self, name)
        self.btTree = args[0]
        
    def execute(self):
        return False
        
class repeat(ConditionNode):
    def __init__(self, name, *args):
        ConditionNode.__init__(self, name)
        self.btTree = args[0]
        
    def execute(self):
        return False
        
class askChatbot(ConditionNode):
    def __init__(self, name, *args):
        ConditionNode.__init__(self, name)
        self.btTree = args[0]
        
    def execute(self):
        return False
        
class initialization(ConditionNode):
    def __init__(self, name, *args):
        ConditionNode.__init__(self, name)
        self.btTree = args[0]
        
    def execute(self):
        return False
        
class nobody(ConditionNode):
    def __init__(self, name, *args):
        ConditionNode.__init__(self, name)
        self.btTree = args[0]
        
    def execute(self):
        return False
        
class askMemory(ConditionNode):
    def __init__(self, name, *args):
        ConditionNode.__init__(self, name)
        self.btTree = args[0]
        
    def execute(self):
        return False
        
class known(ConditionNode):
    def __init__(self, name, *args):
        ConditionNode.__init__(self, name)
        self.btTree = args[0]
        
    def execute(self):
        return False
        
class analyzeInput(ConditionNode):
    def __init__(self, name, *args):
        ConditionNode.__init__(self, name)
        self.btTree = args[0]
        
    def execute(self):
        return False
        
class learnKnowledge(ConditionNode):
    def __init__(self, name, *args):
        ConditionNode.__init__(self, name)
        self.btTree = args[0]
        
    def execute(self):
        return False
        
class askEmail(ConditionNode):
    def __init__(self, name, *args):
        ConditionNode.__init__(self, name)
        self.btTree = args[0]
        
    def execute(self):
        return False
        
class noConfirm(ConditionNode):
    def __init__(self, name, *args):
        ConditionNode.__init__(self, name)
        self.btTree = args[0]
        
    def execute(self):
        return False
        

class myBT(BehaviorTree):
    def __init__(self):
        BehaviorTree.__init__(self)
        self.idAssigned = 0
    
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
        else:
            if name == 'updateUser':
                node = updateUser(name, self)
            if name == 'quitEmail':
                node = quitEmail(name, self)
            if name == 'checkFaceEmotion':
                node = checkFaceEmotion(name, self)
            if name == 'askForMail':
                node = askForMail(name, self)
            if name == 'askTitle':
                node = askTitle(name, self)
            if name == 'quit':
                node = quit(name, self)
            if name == 'shutUp':
                node = shutUp(name, self)
            if name == 'pardon':
                node = pardon(name, self)
            if name == 'askContent':
                node = askContent(name, self)
            if name == 'askWhom':
                node = askWhom(name, self)
            if name == 'send':
                node = send(name, self)
            if name == 'updateEmotion':
                node = updateEmotion(name, self)
            if name == 'checkName':
                node = checkName(name, self)
            if name == 'addQuestion':
                node = addQuestion(name, self)
            if name == 'checkEnd':
                node = checkEnd(name, self)
            if name == 'noInput':
                node = noInput(name, self)
            if name == 'checkNumPeople':
                node = checkNumPeople(name, self)
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
            if name == 'analyzeInput':
                node = analyzeInput(name, self)
            if name == 'learnKnowledge':
                node = learnKnowledge(name, self)
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