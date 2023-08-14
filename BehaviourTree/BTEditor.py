#####################################################
#                                                   #
#    A python implementation of Behavior Tree       #
#                 Gengdai LIU                       #
#                 2012-12-20                        #
#                                                   #
#####################################################

from fltk import *
import json
import sys
from BehaviorTree import *


class Node:
    """
    a tree node contains a payload, a state, a list of children
    and a ref to its parent
    If you want to intercept node open/close events, you
    should subclass this
    """
    def __init__(self, tree, parent, title, type = 0, payload=None, children=None):
        """
        create a tree node    
        title is the text to be displayed    
        payload is an object which this node contains, can be any
        python object    
        children is a list of child nodes (optional)
        """
        self.tree = tree
        #self.id = tree.nodeCount+1
        self.parent = parent
        self.level = parent.level + 1
        self.title = title
        self.payload = payload
        if children == None:
            children = []
        self.children = children
        self.isopen = False
        self.type = type
    
    def append(self, title, type=0, data=None, refresh=True):
        """
        adds data to root node    
        Arguments:
            - title - text to show in tree display
            - data - an optional data payload
            - refresh - default True - whether to refresh the
              tree after adding this node
        """
        node = self.__class__(self.tree, self, title, type, data)
        self.children.append(node)    
        self.tree._nodeToShow = node
        self.tree.refresh()
        return node
    
    def refresh(self):
        """
        draws this node, and children (if any, and if open)
        """
        tree = self.tree    
        line = " " * (self.level * 4 + 1)    
        if self.children:
            if self.isopen:
                line += "[-] "
            else:
                line += "[+] "        
        line += self.title        
        tree.visibleNodes.append(self)
        self.treeIdx = tree.nitems
    
        # if this node was selected, mark it
        if tree._nodeToShow == self:
            tree._nodeToShowIdx = tree.nitems
    
        #print "refresh: node %s has idx %s" % (self.title, tree.nitems)
    
        tree.nitems += 1
        tree.add(line)
    
        if self.isopen:
            for child in self.children:
                child.refresh()
    
    def open(self):
        """
        opens this node
    
        Invokes the on_open handler, if any
        """
        self.isopen = True
        self.on_open()
        self.tree.refresh()
    
    def close(self):
        """
        closes this node        
        Invokes the on_close handler, if any
        """
        self.isopen = False
        self.on_close()
        self.tree.refresh()
    
    def toggle(self):
        """
        toggles open/close state
        """
        if self.isopen:
            self.close()
        else:
            self.open()
    
    
    def promote(self):
        """
        promotes this node up one level in hierarchy
        """
        parent = self.parent
    
        if parent == self.tree:
            # already at top - bail
            return
    
        grandparent = parent.parent    
        parentIdx = grandparent.children.index(parent)
        selfIdx = parent.children.index(self)
    
        parent.children.remove(self)
        grandparent.children.insert(parentIdx, self)
        self.parent = grandparent    
        self._changeLevel(-1)    
        self.tree._nodeToShow = self
        self.tree.refresh()
    
        #self.tree.value(self.tree.visibleNodes.index(self) + 1)
    
    def demote(self):
        """
        demotest this item, if possible
        """
        selidx = self.tree.value()    
        siblings = self.parent.children        
        selfidx = siblings.index(self)    
        if selfidx == 0:
            # already subordinate to previous visible node
            return
    
        siblings.remove(self)    
        prevsibling = siblings[selfidx-1]
        if not prevsibling.isopen:
            prevsibling.isopen = True
    
        prevsibling.children.append(self)    
        self.parent = prevsibling
        self._changeLevel(1)    
        self.tree._nodeToShow = self
        self.tree.refresh()
        
        #self.tree.value(selidx)
    
    def moveup(self):
        """
        moves this node up one
        """
        selidx = self.tree.value()    
        siblings = self.parent.children
        selfidx = siblings.index(self)
    
        if selfidx == 0:
            # already top child
            return
    
        prevnode = siblings[selfidx-1]    
        siblings[selfidx-1] = self
        siblings[selfidx] = prevnode    
        self.tree._nodeToShow = self
        self.tree.refresh()
        
        #self.tree.value(selidx-1)
    
    def movedown(self):
        """
        moves this node down one
        """
        selidx = self.tree.value()    
        siblings = self.parent.children
        selfidx = siblings.index(self)
    
        if selfidx >= len(siblings)-1:
            # already top child
            return
    
        nextnode = siblings[selfidx+1]    
        siblings[selfidx+1] = self
        siblings[selfidx] = nextnode
    
        self.tree._nodeToShow = self
        self.tree.refresh()
        
        #self.tree.value(selidx+1)
    
    def cut(self):
        '''remove current node'''  
        self.parent.children.remove(self)
        self.tree.refresh()
        return self
    
    def _changeLevel(self, diff=0):
        
        self.level += diff
        for child in self.children:
            child._changeLevel(diff)
    
    def _setLevel(self, level):
        
        self.level = level
        for child in self.children:
            child._setLevel(level)
    
    def on_open(self):
        """
        handler for when this node is opened    
        You might want to use this, say, when using
        the tree to browse a large hierarchy such as
        a filesystem    
        Your handler should either execute the .append() method,
        or manipulate the .children list    
        Override if needed
        """
        #print "on_open: not overridden"
    
    def on_close(self):
        """
        handler for when this node is closed
        
        You might want to use this, say, when using
        the tree to browse a large hierarchy such as
        a filesystem
    
        Your handler should either execute the .append() method,
        or manipulate the .children list
    
        Typically, you will want to do::
            
            self.children = []
    
        Override if needed
        """
        #print "on_close: not overridden"
    

class Fl_Tree(Fl_Hold_Browser):
    """
    Implements a tree widget
    If you want handlers for node open/close,
    you should subclass this class, and override
    the 'nodeClass' attribute
    """
    nodeClass = Node
    
    def __init__(self, x, y, w, h, label=0):
        """
        Create the tree widget, initially empty    
        The label will be the text of the root node
        """
        Fl_Hold_Browser.__init__(self, x, y, w, h, label)    
        self.children = []
        #self.nodeCount = 0               
        self.widget = self
        self.isopen = True    
        self.visibleNodes = []
        self.selectedNode = None
        self.level = -1    
        self._nodeToShow = None
        self._nodeToShowIdx = -1    
        # add the box deco
        self.box(FL_DOWN_BOX)
        self.root = self.append('Root')        
    
        self.callback(self.on_click)
    
    def handle(self, evid):    
        ret = Fl_Hold_Browser.handle(self, evid)    
        return ret
    
    def append(self, title, type=0, data = None):
        """
        adds data to root node
        """
        node = self.nodeClass(self, self, title, type, data)    
        self.children.append(node)   
        #self.nodeCount+=1
        self.refresh()
        return node
    
    def refresh(self):
        """
        redraws all the contents of this tree
        """
        self.clear()        
        # enumerate out all the children, and children's children
        self.nitems = 0
        self._nodeToShowIdx = -1
    
        self.visibleNodes = []
        for child in self.children:
            child.refresh()
    
        if self._nodeToShowIdx >= 0:
            self.value(self._nodeToShowIdx+1)
    
        self._nodeToShowIdx = -1
        self._nodeToShow = None
    
    def on_click(self, ev):        
        selidx = self.value()
        if selidx <= 0:
            self.selectedNode = None
            return
        thisidx = selidx - 1    
        node = self.visibleNodes[thisidx]

        #print "_on_click: thisidx=%s title %s level=%s" % (
        #    thisidx, node.title, node.level)    
        x = Fl.event_x() - self.x()    
        xMin = (node.level) * 16 + 8
        xMax = xMin + 16
    
        #print "x=%s xMin=%s xMax=%s" % (x, xMin, xMax)    
        if x >= xMin and x <= xMax:
            node.toggle()
            self.value(selidx)
        else:
            self.selectedNode = node
            self.on_select(node)            
    
    def on_select(self, node):
        """
        override in callbacks
        """

    def valuenode(self):        
        idx = self.value()        
        if idx <= 0:
            return None        
        idx -= 1
    
        return self.visibleNodes[idx]
    
    def cut(self):
        """
        does a cut of selected node
        """
        node = self.valuenode()
        if node is None:
            return None
        
        node.parent.children.remove(node)
        #self.nodeCount-=1
        self.refresh()
        return node

    def reset(self):
        '''reset the tree, keep root'''
        self.root.children[:]=[]
        self.refresh()
    
    def paste(self, node):
        """
        does a paste of selected node
        """
        parent = self.valuenode()
        if parent is None:
            return None
        
        parent.children.append(node)
        node._setLevel(parent.level+1)
        self.refresh()

class MyTree(Fl_Tree):
    ''' a tree view used in BTEdior'''
    def __init__(self, editor, x, y, w, h, label=0):
        Fl_Tree.__init__(self, x, y, w, h, label)
        self.editor = editor
        menutable = (('add a child',0,0,0,FL_MENU_INACTIVE), 
                     ('up',0,0,0,FL_MENU_INACTIVE),
                     ('down',0,0,0,FL_MENU_INACTIVE),
                     ('delete',0,0,0,FL_MENU_INACTIVE),                     
                     (None,0))
        self.popupMenu = Fl_Menu_Button(0,0,600,400,None)
        self.popupMenu.type(Fl_Menu_Button.POPUP3)
        self.popupMenu.copy(menutable)
        self.popupMenu.callback(self.on_popup)        

    def on_click(self, ev):
        '''override, called when clicked in tree viewer'''
        if self.value() <= 0:
            for widget in self.editor.group.children.values():
                widget.deactivate()
            #item = self.popupMenu.find_item('add a child')
            #item.deactivate()
            #item = self.popupMenu.find_item('delete')
            #item.deactivate()
        Fl_Tree.on_click(self,ev)

    def on_select(self,ev):
        '''override, called when an item is selected'''
        Fl_Tree.on_select(self,ev)
        item = self.popupMenu.find_item('up')
        item.activate()
        item = self.popupMenu.find_item('down')
        item.activate()
        item = self.popupMenu.find_item('add a child')
        if self.selectedNode.type != 5 and self.selectedNode.type != 6:
            if self.selectedNode.type == 1 and self.selectedNode.children.__len__() == 1:
                item.deactivate()
            else:
                item.activate()
        else:
            item.deactivate()   

        if self.selectedNode != self.root:
            item = self.popupMenu.find_item('delete')
            item.activate()
        else:
            item = self.popupMenu.find_item('delete')
            item.deactivate()
        for widget in self.editor.group.children.values():
                widget.activate()
        node = self.selectedNode
        group = self.editor.group
        nameInput = group.children['inNodeName']
        typeInput = group.children['chNodeType']
        nameInput.value(node.title)
        typeInput.value(node.type)

    def on_popup(self, menu):
        '''callback function for popup menu'''
        index = menu.value()
        if index == 0: # add a child
            self.valuenode().append('noname')
        elif index == 1: # up
            self.valuenode().moveup()
        elif index ==2: #down
            self.valuenode().movedown()
        else: # delete selected node
            self.cut()

    def __getActionNodes(self, node, list):
        if node.type == 5:
            list.append(node)
        for child in node.children:
            self.__getActionNodes(child, list)

    def getActionNodes(self, list):
        self.__getActionNodes(self.root, list)

    def __getConditionNodes(self, node, nls):
        if node.type == 6:
            nls.append(node)
        for child in node.children:
            self.__getConditionNodes(child, nls)

    def getConditionNodes(self, nls):
        self.__getConditionNodes(self.root, nls)

# main window
class BTEditor(Fl_Window):
    '''a behavior tree editor, save a json file'''
    def __init__(self, xpos, ypos, width, height, label=None):
        Fl_Window.__init__(self, xpos, ypos, width, height, label)
        self.treeDict = {}
        self.stack = Stack()
        self.menuBar()
        self.treeView(self) # tree control
        self.editView() # editor
        self.exportView() # export
    
    def menuBar(self):
        '''set menu bar'''
        menubar = Fl_Menu_Bar(0,0,500,25)
        menutable = (("&File",0,0,0,FL_SUBMENU),
                     ("&Import", 0, self.__importMenuCB),
	                 ("&Export", 0, self.__exportMenuCB),
	                 ("&Quit", 0, self.__quitMenuCB),
                     (None,0),
                     (None,0))
        menubar.copy(menutable)

    def __toTreeView(self, dict):
        '''from dictionary to tree, recurse from root'''
        if dict == self.treeDict:
            self.tree.root.title = str(self.treeDict['name'])
            self.tree.root.type = self.__fromTypeToInt(self.treeDict['type'])
            self.stack.push(self.tree.root)
        for child in dict['children']:
            name = str(child['name'])
            type = self.__fromTypeToInt(child['type'])
            newNode = self.stack.top().append(name, type)
            self.stack.push(newNode)
            self.__toTreeView(child)
            self.stack.pop()

    def __importMenuCB(self, widget):
        '''callback function for import menu button'''
        openfile = fl_file_chooser("Open File?", "*","Open Tree File")
        if openfile != None:
            file = open(openfile)
            self.treeDict = json.load(file)
            self.stack.clear()
            self.tree.reset()
            self.__toTreeView(self.treeDict)
            self.tree.refresh()
            file.close()

    def __exportMenuCB(self, widget):
        '''callback function for export menu button'''
        openfile = fl_file_chooser("Open File?", "*","Open Tree File")
        if openfile != None:
            self.treeDict.clear()
            self.stack.clear()
            self.__toTreeDict(self.tree.root)
            file = open(openfile, 'w')
            file.write(json.dumps(self.treeDict))
            file.close()
    
    def __quitMenuCB(self, widget):
        '''callback function for quit menu button'''
        sys.exit(0)

    def treeView(self, editor):
        '''create a tree view'''
        self.tree = MyTree(editor,20,50,210,430,'Tree Viewer')
        self.tree.align(FL_ALIGN_TOP_LEFT)        

    def editView(self):
        '''create the editor view'''
        # group
        self.group = Fl_Group(240, 50, 250, 220, "Edit")
        self.group.children = {}        
        self.group.box(FL_ENGRAVED_BOX)
        self.group.align(FL_ALIGN_TOP_LEFT)
        # node name
        inNodeName = Fl_Input(320,70,150,30,"Node Name")
        self.group.children['inNodeName'] = inNodeName
        # node type
        chNodeType = Fl_Choice(320,140,150,30,'Node Type')
        pulldown= (("",),  
         ("Loop",	FL_ALT+ord('l')),
	     ("Selection",	FL_ALT+ord('s')),
         ("Sequence",	FL_ALT+ord('q')),
         ("Parallel",	FL_ALT+ord('p')),
         ("Action",	FL_ALT+ord('a')),
         ("Condition", FL_ALT+ord('c')),
	     (None,))
        chNodeType.copy(pulldown)
        chNodeType.callback(self.__typeChoiceCB)
        self.group.children['chNodeType'] = chNodeType
        # update button
        btUpdate = Fl_Button(380, 220, 80,30,'Update')
        btUpdate.callback(self.__updateCB)
        btUpdate.name = 'update'
        self.group.children['btUpdate'] = btUpdate
        self.group.end()

    def exportView(self):
        '''export python and json file'''
        group = Fl_Group(240, 300, 250, 180, "Export")
        group.align(FL_ALIGN_TOP_LEFT)
        group.box(FL_ENGRAVED_BOX)
        self.pyFileNameInput = Fl_Input(320,330,150,30,"Python File")
        self.jsFileNameInput = Fl_Input(320,380,150,30,"Json File")
        btExport = Fl_Button(380, 430, 80,30,'Export')
        btExport.name = 'export'
        btExport.callback(self.__exportCB)
    
    def __typeChoiceCB(self,menu):
        '''Callback function: choice list for node type'''
        index = menu.value()
        if index == 1: # Loop
            pass
        elif index == 2: # Selection
            pass
        elif index ==3: # Sequence
            pass
        elif index == 4: # Parallel
            pass
        elif index == 5: # Action
            pass
        else: # Condition
            pass

    def __updateCB(self,widget):
        '''callback function for update behavior tree'''
        if widget.name != 'update':
            return
        node = self.tree.selectedNode
        if node == None:
            fl_alert('please select a tree node first')
            return
        nodename = self.group.children['inNodeName'].value()
        nodetype = self.group.children['chNodeType'].value()
        if nodename == '' or nodetype == 0:
            fl_alert('node name and type can not be empty')
            return

        node.type = nodetype
        node.title = nodename
        self.tree.refresh()

    def __exportCB(self,widget):
        '''callback function for export python and json files'''
        if widget.name != 'export':
            return
        self.pyfilename = self.pyFileNameInput.value()
        self.jsfilename = self.jsFileNameInput.value()
        if self.pyfilename =='' or self.jsfilename =='':
            fl_alert('file names can not be empty')
            return
        self.savePythonFile()
        self.saveTreeFile()

    def __fromIntToType(self, index):
        '''from integar to string representation of node type'''
        type = ''
        if index == 1: # Loop
            type = 'Loop'
        elif index == 2: # Selection
            type = 'Selection'
        elif index ==3: # Sequence
            type = 'Sequence'
        elif index == 4: # Parallel
            type = 'Parallel'
        elif index == 5: # Action
            type = 'Action'
        else: # Condition
            type = 'Condition'
        return type

    def __fromTypeToInt(self, type):
        '''from integar to string representation of node type'''
        index = 0
        if type == 'Loop': # Loop
            index = 1
        elif type == 'Selection': # Selection
            index = 2
        elif type == 'Sequence': # Selection
            index = 3
        elif type == 'Parallel': # Parallel
            index = 4
        elif type == 'Action': # Action
            index = 5
        else: # Condition
            index = 6
        return index

    def __toTreeDict(self,node):
        '''from tree to a dict'''
        if node == self.tree.root:
            self.treeDict['name'] = node.title
            self.treeDict['type'] = self.__fromIntToType(node.type)
            self.treeDict['children'] = []
            self.stack.push(self.treeDict)
        for child in node.children:
            newDict={}
            newDict['name']=child.title
            newDict['type']=self.__fromIntToType(child.type)
            newDict['children']=[]
            self.stack.top()['children'].append(newDict)
            self.stack.push(newDict)
            self.__toTreeDict(child)
            self.stack.pop()

    def saveTreeFile(self):
        '''save json file of tree structure'''
        file = open(self.jsfilename+'.json','w')
        self.treeDict.clear()
        self.stack.clear()
        self.__toTreeDict(self.tree.root)
        file.write(json.dumps(self.treeDict))
        file.close()

    def savePythonFile(self):
        '''save python file of behavior tree implementation'''
        actNodes = []
        conNodes = []
        actDict = {}
        conDict = {}
        actStr = '''from BehaviorTree import *
import time
        '''
        conStr=''
        self.tree.getActionNodes(actNodes)
        self.tree.getConditionNodes(conNodes)
        for node in actNodes:
            if node.title not in actDict:
                actDict[node.title] = node.type
            else:
                pass
        for nodeTitle in actDict.keys():
            actStr+=self.inheritedActionNode(nodeTitle)
       
        for node in conNodes:
            if node.title not in conDict:
                conDict[node.title] = node.type
            else:
                pass
        for nodeTitle in conDict.keys():
            conStr+=self.inheritedConditionNode(nodeTitle)

        file = open(self.pyfilename+'.py','w')
        str_main = actStr + conStr + '''

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
        elif type =='Action':'''
        for node in actDict.keys():
            str_main+='''
            if name == '''+ "'"+ node +"':"
            str_main+='''
                node = '''+ node +'(name, self)'
        if len(conDict)>0:
            str_main+='''
        else:'''
        for node in conDict.keys():
            str_main+='''
            if name == '''+"'"+ node +"':"
            str_main+='''
                node = ''' + node +'(name, self)'
        str_main+='''
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
    '''
        str_main+="bt.buildFromFile('"+self.jsfilename+'.json'+"')\n"
        str_main+="    bt.execute()"
        file.write(str_main)
        file.close()

    def inheritedActionNode(self,name):
        '''generate a string that represents an inherited ActionNode'''
        fun = '''
class '''
        fun+= name +'(ActionNode):' +'''
    def __init__(self, name, *args):
        ActionNode.__init__(self, name)
        self.btTree = args[0]
        
    def execute(self):
        return True
        '''
        return fun

    def inheritedConditionNode(self, name):
        '''generate a string that represents an inherited ConditionNode'''
        fun = '''
class '''
        fun+= name +'(ConditionNode):' +'''
    def __init__(self, name, *args):
        ConditionNode.__init__(self, name)
        self.btTree = args[0]
        
    def execute(self):
        return False
        '''
        return fun

# main
if __name__=='__main__':
    window = BTEditor(700, 200, 500, 500, 'BTEditor')
    window.end()
    window.show(len(sys.argv), sys.argv)
    Fl.run()