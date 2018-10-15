import shlex
import enums
import os

Token = enums.Token
Type = enums.Type
Error = enums.Error

functions = {}

class functionPrintConsole():

    def __init__(self):
        self.params = [((Token.TYPE, Type.STR), (Token.ID, "s"))]

    def __repr__(self):
        return "({})".format(self.params)

    def execute(self, params):
        if len(params) != 1:
            print("printConsole requires one parameter")
            exit(Error.PAR_EXPECTED)
        else:
            print(str(params[0][2]))
            return None

class functionPrintFile():

    def __init__(self):
        self.params = [((Token.TYPE, Type.STR), (Token.ID, "s")),((Token.TYPE, Type.STR), (Token.ID, "f"))]

    def __repr__(self):
        return "({})".format(self.params)

    def execute(self, params):
        if len(params) != 2:
            print("printFile requires two parameters")
            exit(Error.PAR_EXPECTED)
        else:
            with open(str(params[1][2]), "w") as myfile:
                myfile.write(str(params[0][2]) + "\n")
            return None

class functionAppendFile():

    def __init__(self):
        self.params = [((Token.TYPE, Type.STR), (Token.ID, "s")),((Token.TYPE, Type.STR), (Token.ID, "f"))]

    def __repr__(self):
        return "({})".format(self.params)

    def execute(self, params):
        if len(params) != 2:
            print("appendFile requires two parameters")
            exit(Error.PAR_EXPECTED)
        else:
            with open(str(params[1][2]), "a") as myfile:
                myfile.write(str(params[0][2]) + "\n")
            return None

class functionSysCall():

    def __init__(self):
        self.params = [((Token.TYPE, Type.STR), (Token.ID, "s"))]

    def __repr__(self):
        return "({})".format(self.params)

    def execute(self, params):
        if len(params) != 1:
            print("syscall requires one parameter")
            exit(Error.PAR_EXPECTED)
        else:
            os.system(params[0][2])
            return None

    
functions["printConsole"]=functionPrintConsole()
functions["printFile"]=functionPrintFile()
functions["appendFile"]=functionAppendFile()
functions["syscall"]=functionSysCall()
