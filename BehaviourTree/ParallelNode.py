#####################################################
#                                                   #
#    A python implementation of Behavior Tree       #
#                 Gengdai LIU                       #
#                 2012-12-20                        #
#                                                   #
#####################################################

from TreeNode import *
import threading, time

class ParallelNode(TreeNode):
    '''the children of parallel node will be executed simultaneously'''
    def __init__(self, nodeName):
        TreeNode.__init__(self, nodeName)
        self.type = NodeType.PARALLEL
        self.threads = []
        self.results = []
        self.mutex = threading.Lock()
        self.failedIndex = -1

    def thread(self, index):
        '''a thread: executing one of children'''
        threadName = threading.currentThread().getName()        
        #self.mutex.acquire()
        result = self.children[index].execute()
        self.results[index] = result
        #self.mutex.release()
        time.sleep(1)
        if result:
            pass#print threadName, " execution succeeds"
        else:
            self.halt()
            #print threadName, " execution fails"

    def execute(self):
        '''execute all children at the same time, multi-threading'''
        del self.threads[:] # clear previous threads
        del self.results[:]
        # special case: Condition Node as the first child
        if self.children[0].type == 'Condition':
            if self.children[0].excute() == False:
                self.failedIndex = 0
                return False

        # normal case: concurrency
        num = len(self.children)
        if num == 0:
            raise Exception(self.name+': no child')
            return False
        result = True
        for x in xrange(num):
            self.results.append(False)
            self.threads.append(threading.Thread(target=self.thread, args=(x,),name=self.children[x].name))
        # start all threads
        for t in self.threads:
            t.start()
        for t in self.threads:
            t.join()
        for r in self.results:
            if not r:
                result = False
                failedIndex = self.results.index(r)
                break
        return result

    def halt(self):
        '''stop all subtrees(if the child is a loop node)'''
        for child in self.children:
            child.halt()