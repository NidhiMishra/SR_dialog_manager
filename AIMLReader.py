__author__ = 'IMI-User'
import os
from aiml import AimlParser
import glob
import time
import sys
import xml.sax
import re

class AIMLReader:
    def __init__(self):
        self._verboseMode = True
        self._textEncoding = "utf-8"

    def getFiles(self,paths):
        if isinstance(paths,list):
            return paths
        else:
            return [paths]

    def readAIML(self, filename):
        """Load and learn the contents of the specified AIML file.

        If filename includes wildcard characters, all matching files
        will be loaded and learned.

        """
        for f in glob.glob(filename):
            if self._verboseMode: print "Loading %s..." % f,
            start = time.clock()
            # Load and parse the AIML file.
            parser = AimlParser.create_parser()
            handler = parser.getContentHandler()
            handler.setEncoding(self._textEncoding)
            try: parser.parse(f)
            except xml.sax.SAXParseException, msg:
                err = "\nFATAL PARSE ERROR in file %s:\n%s\n" % (f,msg)
                sys.stderr.write(err)
                continue
            # store the pattern/template pairs in the PatternMgr.
            resDict={}
            for pattern, template in handler.categories.items():
                question=self.clearText(pattern[0])
                answers=self.getTextFromTree(template)
                resDict[question]=answers

            if self._verboseMode:
                print "done (%.2f seconds)" % (time.clock() - start)
            return resDict

    def clearText(self,text):
        text=re.sub(r'''\n''',"",text)
        text=text.lower()
        return text

    def getTextFromNode(self,tree,answers):
        if isinstance(tree,list):
            if tree[0]=="text":
                if tree[2] not in ["","\n"]:
                    answers.append(self.clearText(tree[2]))
            else:
                for node in tree:
                    self.getTextFromNode(node,answers)

    def getTextFromTree(self,tree):
        answers=[]
        for node in tree:
            self.getTextFromNode(node,answers)
        return answers


    def read(self,path):
        resDict={}
        self.files=self.getFiles(path)
        for file in self.files:
            if os.path.isfile(path):
                res=self.readAIML(file)
                resDict.update(res)
        return resDict


if __name__=="__main__":
    #path="D:\\BTC_VH\\SOURCE\\AIMLReader\\aiml\\zz_imi_std-test.aiml"
    import os
    path=os.getcwd()+"\\AIML\\02-23-17 13-41-09.aiml"
    reader=AIMLReader()
    resDict=reader.read(path)
    print len(resDict)


