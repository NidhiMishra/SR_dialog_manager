##############################################################
#                                                            #
#     Implementation of Conversation for Experiment One      #
#                  Gengdai LIU                               #
#                   2013-01-31                               #
#                                                            #
##############################################################

from BehaviorTree import *
from DialogueGenerator import *
from SpeechListener import *
import time
import sys
sys.path.append('gen-py')

# Thrift things
from I2P import constants
from I2P.ttypes import *
from Control import *
from thrift import Thrift
from thrift.transport import TSocket
from thrift.transport import TTransport
from thrift.protocol import TBinaryProtocol

# some global parameters used for control the process
context = None # store the context
reply = None # reply of user

Expressions = ['NEUTRAL','ANGER','DISGUST','FEAR','HAPPINESS','SADNESS','SURPRISE']
Gesture = ['WAVE','SWEEP','SWEEP_RIGHT','MOTEX','MOTEX_SOFTENED','YOU','WHY','OFFER']
        
class Ask(ActionNode):
    '''active ask question'''
    def __init__(self, name, *args):
        ActionNode.__init__(self, name)
        self.btTree = args[0]
        self.dialogue = None
        self.client = None

    def setDialogueGenerator(self, dialogue):
        '''set dialogue generator'''
        self.dialogue = dialogue

    def setClient(self, client):
        self.client = client

    def setExp(self, exp):
        self.exp = exp

    def execute(self):
        global context
        if self.dialogue == None or self.client == None:
            raise Exception('please set parameters before execute ask node: id '+str(self.id))
        sentence = self.dialogue.ask(self.exp.talkIndex)
        ask = self.dialogue.activeAsk[self.exp.talkIndex]
        if "expression" in ask:
            self.client.setFaceExpression(Expressions.index(ask["expression"]),10)
            time.sleep(1)
        if "gesture" in ask:
            self.client.playAnimation(Gesture.index(ask["gesture"]))
        self.client.speak(sentence,0)
        self.client.setLabel('')
        self.exp.talkIndex+=1
        time.sleep(2)
        self.client.setLabel('[Waiting for response]')
        l = speech.listenforanything(callback)
        while(l.islistening()):
            time.sleep(1)
        self.client.setLabel('')
        return True
        
class Say(ActionNode):
    '''say something'''
    def __init__(self, name, *args):
        ActionNode.__init__(self, name)
        self.btTree = args[0]
        self.dialogue = None
        self.client = None

    def setDialogueGenerator(self, dialogue):
        '''set dialogue generator'''
        self.dialogue = dialogue

    def setClient(self, client):
        self.client = client

    def setExp(self, exp):
        self.exp = exp

    def execute(self):
        global context
        if self.dialogue == None or self.client == None:
            raise Exception('please set parameters before execute say node: id '+str(self.id))
        sentence = self.dialogue.ask(self.exp.talkIndex)
        say = self.dialogue.activeAsk[self.exp.talkIndex]
        if "expression" in say:
            self.client.setFaceExpression(Expressions.index(say["expression"]),10)
            time.sleep(1)
        if "gesture" in say:
            self.client.playAnimation(Gesture.index(say["gesture"]))
        self.client.speak(sentence,0)
        self.client.setLabel('')
        self.exp.talkIndex+=1
        time.sleep(2)
        return True
        
class Answer(ActionNode):
    '''answer questions to users'''
    def __init__(self, name, *args):
        ActionNode.__init__(self, name)
        self.btTree = args[0]
        self.client = None

    def setDialogueGenerator(self, dialogue):
        '''set dialogue generator'''
        self.dialogue = dialogue
    
    def setClient(self, client):
        self.client = client

    def setExp(self, exp):
        self.exp = exp

    def displayHint(self, topic):
        '''display hint on the screen'''
        if self.client == None:
            raise Exception('set client before use it')
        if topic == "friend":
            self.client.setLabel('[mention your friend] '+self.dialogue.friend)
        elif topic == "recommend":
            self.client.setLabel('[recommend movie] '+self.dialogue.context)
        elif topic == "actor" or topic == "director":
            if self.dialogue.group == "exp" and self.dialogue.friend != None:
                self.client.setLabel('[mention your friend] '+ self.dialogue.friend)
                
    def execute(self):
        global context
        if self.dialogue == None or self.client == None:
            raise Exception('please set parameters before execute answer node: id '+str(self.id))
        sentence = ''
        answer = self.dialogue.response(self.exp.listenIndex-1, context)
        for ans in answer:
            if "topic" in ans:
                self.displayHint(ans["topic"])
            if "expression" in ans:
                self.client.setFaceExpression(Expressions.index(ans["expression"]),10)
                time.sleep(1)
            if "gesture" in ans:
                self.client.playAnimation(Gesture.index(ans["gesture"])) 
            self.client.speak(ans["sentence"],0)
            print ans["duration"]
            time.sleep(ans["duration"])
        
        return True
        
class Assert(ConditionNode):
    '''judge the status, true or false'''
    def __init__(self, name, *args):
        ConditionNode.__init__(self, name)
        self.btTree = args[0]
        self.listener = None
        self.client = None
    
    def setListener(self, listener):
        '''set speech listener for user's speech input'''
        self.listener = listener

    def setClient(self, client):
        '''set thrift client'''
        self.client = client    
        
    def setExp(self, exp):
        self.exp = exp

    def execute(self):
        global reply     
        if self.listener == None or self.client == None:
            raise Exception('please set parameters before execute condition node: id '+ str(self.id))
        self.client.setLabel(self.listener.questions[self.exp.listenIndex]["cue"])
        ans = self.listener.listen(self.exp.listenIndex)
        self.client.setLabel('')
        if ans[0] != None:
            raise Exception('an error occurs'+str(self.id))
        self.exp.listenIndex+=1
        reply = ans[1]
        if reply == 'yes' or reply =="yeah":
            self.exp.talkIndex+=1
            return True
        else:
            return False
        
class NoQuestion(ConditionNode):
    '''listening to the user's speech'''
    def __init__(self, name, *args):
        ConditionNode.__init__(self, name)
        self.btTree = args[0]
        self.listener = None
        self.client = None
    
    def setListener(self, listener):
        '''set speech listener for user's speech input'''
        self.listener = listener
    
    def setClient(self, client):
        '''set thrift client'''
        self.client = client    
    def setExp(self, exp):
            self.exp = exp

    def execute(self):
        global context
        global reply
        if self.listener == None or self.client == None:
            raise Exception('please set parameters before execute condition node: id '+str(self.id))
        self.client.setLabel(self.listener.questions[self.exp.listenIndex]["cue"])
        context = self.listener.listen(self.exp.listenIndex)
        self.client.setLabel('')
        print context[1]    
        self.exp.listenIndex+=1    
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
            if name == 'Ask':
                node = Ask(name, self)
            if name == 'Answer':
                node = Answer(name, self)
            if name == 'Say':
                node = Say(name, self)
        else:
            if name == 'Assert':
                node = Assert(name, self)
            if name == 'NoQuestion':
                node = NoQuestion(name, self)
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

def callback(phrase, listener):
    '''callback function after anything is said by the user'''
    print phrase
    listener.stoplistening()

def createClient():
    '''create a thrift client'''
    transport = TSocket.TSocket('localhost', 9090)
    transport = TTransport.TBufferedTransport(transport)
    protocol = TBinaryProtocol.TBinaryProtocol(transport)
    client = AgentControl.Client(protocol)
    transport.open()
    return client

def setDialogueGenerators(dialogue, tree, client):
    '''set dialogue generator and virtual human client for all action nodes in the behavior tree'''
    actions = []
    tree.getActionNodes(actions)
    for act in actions:
        act.setDialogueGenerator(dialogue)
        act.setClient(client)        

def setSpeechListeners(listener, tree, client):
    '''set speech listener for all condition nodes in the behavior tree'''
    conditions = []
    tree.getConditionNodes(conditions)
    for cond in conditions:
        cond.setListener(listener)
        cond.setClient(client)

def setExperimentGroup(tree, group):
    '''set group to answer nodes'''
    nodes = []
    tree.getNodes('Answer', nodes)
    for n in nodes:
        n.setGroup(group)

def getAskSayNodes(node, nls):
    '''get action nodes from a specific node'''
    if node.name == 'Ask' or node.name == 'Say':
        nls.append(node)
    for child in node.children:
        getAskSayNodes(child, nls)

def getConditionNodes(node, nls):
    '''get condition nodes from a specific node'''
    if node.type == 'Condition':
        nls.append(node)
    for child in node.children:
        getConditionNodes(child, nls)


def setExp(tree, nls):
    '''set an instance of ExpOne to all nodes in the tree'''
    tree.getActionNodes(nls)
    for node in nls:
        node.setExp()

class ExpOne:
    '''experiment one'''
    def __init__(self,name,group):
        self.talkIndex = 0 # index of sentences for Sophie
        self.listenIndex = 0 # index of sentences for the user
        # client connected to virtual human platform
        self.client = createClient()
        # an instance of the behavior tree 
        self.bt = myBT()
        self.bt.buildFromFile('Talking.json')
        # dialogue generator
        self.dialog = DialogueGenerator(name,group,self.bt,self)
        self.dialog.initialize()
        setDialogueGenerators(self.dialog, self.bt, self.client)
        # speech listener
        self.listener = SpeechListener()
        # pass some useful parameters to speech listener
        self.listener.setParams(self.dialog.db_movie,self.dialog.db_director,self.dialog.db_actor,self.dialog.questions) 
        setSpeechListeners(self.listener, self.bt, self.client)
        # set an instance of ExpOne to all nodes in the tree
        nls = []
        cls = []
        self.bt.getActionNodes(nls)
        self.bt.getConditionNodes(cls)
        nls.extend(cls)
        for node in nls:
            node.setExp(self)

    def start(self, idx):
        '''start the experiment'''
        self.bt.root.startFrom(idx)
        actions = []
        conditions = []
        for node in self.bt.root.children[0:idx]:
            getAskSayNodes(node, actions)
            getConditionNodes(node,conditions)
        self.talkIndex = len(actions)
        self.listenIndex = len(conditions)
        print 'talkIndex =', self.talkIndex
        print 'listenIndex =', self.listenIndex
        self.bt.execute()


if __name__ == "__main__":
    startIndex = 0
    user_name = sys.argv[1]
    if sys.argv[2] == '-c':
        exp = ExpOne(user_name, 'ctrl')
    elif sys.argv[2] == '-e':
        exp = ExpOne(user_name, 'exp')
    else: pass
    if len(sys.argv) == 4:
        startIndex = int(sys.argv[3])
    exp.start(startIndex)