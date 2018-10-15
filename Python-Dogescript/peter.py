import string
import hannibal
import enums
import stdfunc
from decimal import Decimal

#Akiračio klasė - paremta stack'u. Saugosime [id] => (type, value)
class Scope:
    def __init__(self):
        self.stacks = [{}]
        self.layers = 1

    def inc(self): #lygio gilinimas
        self.stacks.insert(0, {})
        self.layers += 1
        
    def dec(self): #lygio mažinimas
        if(self.layers>1):
            self.stacks.pop(0)
            self.layers -= 1

    def push(self, key, value): #reikšmė dedama į esamą akiratį
        self.stacks[0][key] = value

    def replace(self, key, value): #reikšmės atnaujinimas - atnaujinamas lokaliausias, jei nerasta - klaida
        for scope in self.stacks:
            if key in scope:
                scope[key] = value;
                return True
        return False

    def get(self, key): #reikšmės gavimas
        for scope in self.stacks:
            val = scope.get(key)
            if(val is not None):
                return val
        return None

#Reikalingi enum'ai
Token = enums.Token
Type = enums.Type
Error = enums.Error

#Akiratis globalus, nes jį reikia pasiekti iš kelių vietų
scope = Scope()

#Sukonstruotas medis
parsedTree = []

#funkcijų sąrašas
functions = {}

#Reikšmių išgavimo metodai (grąžinamas tuple'as (Type, value)
def processInt(token):
    return (Type.INT, int(token[2]))

def processDec(token):
    return (Type.DEC, Decimal(token[2]))

def processString(token):
    return (Type.STR, token[2])

#Numeta () nuo galų, jei yra
def debracketRound(tokens):
    if tokens :
        if tokens[0][0] == Token.ROUNDBRACKETLEFT and tokens[-1][0] == Token.ROUNDBRACKETRIGHT:
            countLeft = 0
            countRight = 0
            for t in tokens:
                if t[0] == Token.ROUNDBRACKETLEFT:
                    countLeft += 1
                elif t[0] == Token.ROUNDBRACKETRIGHT:
                    countRight += 1
            if countLeft == countRight:
                tokens.pop(0)
                tokens.pop()
            else:
                print(") expected!")
                exit(Error.PAR_EXPECTED)
                     
#Baigia () apgaubtą išraišką, gali skaityti iš kairės į dešinę arba atvirkščiai
def getRoundsToClose(tokens, leftToRight = True):
    rounds = []
    depth = 1
    if(leftToRight == True):
        while(depth > 0 and tokens):
            new = tokens.pop(0)
            rounds.append(new)
            if new[0] == Token.ROUNDBRACKETLEFT:
                depth += 1
            elif new[0] == Token.ROUNDBRACKETRIGHT:
                depth -= 1
        if (depth > 0 and not tokens):
            print(") expected")
            exit(Error.PAR_EXPECTED)
    else:
        while(depth > 0 and tokens):
            new = tokens.pop()
            rounds.insert(0, new)
            if new[0] == Token.ROUNDBRACKETRIGHT:
                depth += 1
            elif new[0] == Token.ROUNDBRACKETLEFT:
                depth -= 1
        if (depth > 0 and not tokens):
            print("( expected")
            exit(Error.PAR_EXPECTED)
    return rounds

#Baigia {} apgaubtą išraišką, gali skaityti iš kairės į dešinę arba atvirkščiai
def getCurliesToClose(tokens, leftToRight = True):
    curlies = []
    depth = 1
    if(leftToRight == True):
        while(depth > 0 and tokens):
            new = tokens.pop(0)
            curlies.append(new)
            if new[0] == Token.CURLYBRACELEFT:
                depth += 1
            elif new[0] == Token.CURLYBRACERIGHT:
                depth -= 1
        if (depth > 0 and not tokens):
            print("} expected")
            exit(Error.PAR_EXPECTED)
    else:
        while(depth > 0 and tokens):
            new = tokens.pop()
            curlies.insert(0, new)
            if new[0] == Token.CURLYBRACERIGHT:
                depth += 1
            elif new[0] == Token.CURLYBRACELEFT:
                depth -= 1
        if (depth > 0 and not tokens):
            print("{ expected")
            exit(Error.PAR_EXPECTED)
    return curlies

#Baigia [] apgaubtą išraišką, gali skaityti iš kairės į dešinę arba atvirkščiai
def getSquaresToClose(tokens, leftToRight = True):
    squares = []
    depth = 1
    if(leftToRight == True):
        while(depth > 0 and tokens):
            new = tokens.pop(0)
            squares.append(new)
            if new[0] == Token.SQUAREBRACKETLEFT:
                depth += 1
            elif new[0] == Token.SQUAREBRACKETRIGHT:
                depth -= 1
        if (depth > 0 and not tokens):
            print("] expected!")
            exit(Error.PAR_EXPECTED)
    else:
        while(depth > 0 and tokens):
            new = tokens.pop()
            squares.insert(0, new)
            if new[0] == Token.SQUAREBRACKETRIGHT:
                depth += 1
            elif new[0] == Token.SQUAREBRACKETLEFT:
                depth -= 1
        if (depth > 0 and not tokens):
            print("[ expected!")
            exit(Error.PAR_EXPECTED)
    return squares

#Medžio mazgo klasės
#Išraiškų mazgai
#Reikšmės mazgas
class valueNode():

    def __init__(self, token):
        if token[0] == Token.ID:
            self.nodeType = Token.ID
            self.id = token[1]
        elif token[0] == Token.LIT:
            self.nodeType = Token.LIT
            self.type = token[1]
            self.val = token[2]
        else:
            print("Error setting value - token ", token)
            exit(Error.WTF)

    def __repr__(self):
        if self.nodeType == Token.ID:
            return str(self.id)
        elif self.nodeType == Token.LIT:
            return str(self.val)
        else:
            print("Error retrieving value")
            exit(Error.WTF)

    def get(self):
        if self.nodeType == Token.ID:
            return (Token.ID, self.id)
        elif self.nodeType == Token.LIT:
            return (Token.LIT, self.type, self.val)
        else:
            print("Error retrieving value")
            exit(Error.WTF)


#Gavimo mazgas - buvo įdėtas, kai planuota realizuoti masyvus; galutinėje versijoje nedaro nieko
class fetchNode():

    def __init__(self, value):
        self.value = value

    def __repr__(self):
        return str(self.value)

    def get(self):
        return value.get()

#++, -- operatorių mazgas
class unaryNode():

    def __init__(self, operator, fetch, prefix):
        self.operator = operator
        self.fetch = fetch
        self.prefix = prefix

    def __repr__(self):
        if self.prefix:
            if self.operator == Token.DOUBLEP:
                return "++"+str(self.fetch)
            elif self.operator == Token.DOUBLEM:
                return "--"+str(self.fetch)
            else:
                print("Unary operation parsing error")
                exit(Error.WTF)
        elif not self.prefix:
            if self.operator == Token.DOUBLEP:
                return str(self.fetch)+"++"
            elif self.operator == Token.DOUBLEM:
                return str(self.fetch)+"--"
            else:
                print("Unary operation parsing error")
                exit(Error.WTF)
        else:
            print("Unary operation parsing error")
            exit(Error.WTF)

    def get(self):
        tmp = self.fetch.get()
        if tmp[1] == Type.STR:
            if self.operator == Token.DOUBLEP:
                print("Operator ++ cannot be applied to a string")
                exit(Error.PAR_EXPECTED)
            elif self.operator == Token.DOUBLEM:
                print("Operator -- cannot be applied to a string")
                exit(Error.PAR_EXPECTED)
            else:
                print("Unary expression parsing error")
                exit(Error.WTF)
        if self.prefix:
            if tmp[0] != Token.ID:
                if self.operator == Token.DOUBLEP:
                    print("Variable expected after ++")
                    exit(Error.PAR_EXPECTED)
                elif self.operator == Token.DOUBLEM:
                    print("Variable expected after --")
                    exit(Error.PAR_EXPECTED)
                else:
                    print("Unary expression parsing error")
                    exit(Error.WTF)
            else:
                if self.operator == Token.DOUBLEP:
                    value = scope.get(tmp[1])
                    if value is None:
                        print("Variable ", tmp[1], "not found")
                        exit(Error.PAR_UNKNOWN_VAL)
                    value = (value[0], value[1] + 1)
                    if (scope.replace(tmp[1], (value[0], value[1]))):
                        return (Token.LIT, value[0], value[1])
                    else:
                        print("Unary expression execution error")
                        exit(Error.WTF)
                elif self.operator == Token.DOUBLEM:
                    value = scope.get(tmp[1])
                    value = (value[0], value[1] - 1)
                    if value is None:
                        print("Variable ", tmp[1], "not found")
                        exit(Error.PAR_UNKNOWN_VAL)
                    if (scope.replace(tmp[1], (value[0], value[1]))):
                        return (Token.LIT, value[0], value[1])
                    else:
                        print("Unary expression execution error")
                        exit(Error.WTF)
        elif not self.prefix:
            if tmp[0] != Token.ID:
                if self.operator == Token.DOUBLEP:
                    print("Variable expected after ++")
                    exit(Error.PAR_EXPECTED)
                elif self.operator == Token.DOUBLEM:
                    print("Variable expected after --")
                    exit(Error.PAR_EXPECTED)
                else:
                    print("Unary expression parsing error")
                    exit(Error.WTF)
            else:
                if self.operator == Token.DOUBLEP:
                    value = scope.get(tmp[1])
                    if tmp is None:
                        print("Variable ", tmp[1], "not found")
                        exit(Error.PAR_UNKNOWN_VAL)
                    if (scope.replace(tmp[1], (value[0], value[1] + 1))):
                        return (Token.LIT, value[0], value[1])
                    else:
                        print("Unary expression execution error")
                        exit(Error.WTF)
                elif self.operator == Token.DOUBLEM:
                    value = scope.get(tmp[1])
                    if tmp is None:
                        print("Variable ", tmp[1], "not found")
                        exit(Error.PAR_UNKNOWN_VAL)
                    if (scope.replace(tmp[1], (value[0], value[1] - 1))):
                        return (Token.LIT, value[0], value[1])
                    else:
                        print("Unary expression execution error")
                        exit(Error.WTF)

#! operatoriaus mazgas - atskiriam nuo kitų vienetinių operatorių dėl žymiai skirtingos vidinės logikos
class negNode():

    def __init__(self, fetch):
        self.fetch = fetch;

    def __repr__(self):
        return "!{}".format(self.fetch)

    def get(self):
        ft = self.fetch.get()
        if ft[0] == Token.LIT:
            if ft[1] != Type.INT:
                print("Operator ! can only be applied to int")
                exit(Error.PAR_INVALID_OP)
            else:
                return (Token.LIT, Type.INT, 1 if ft[2] == 0 else 0)
        elif ft[0] == Token.ID:
            val = scope.get(ft[1])
            if val[0] != Type.INT:
                print("Operator ! can only be applied to int")
                exit(Error.PAR_INVALID_OP)
            else:
                return (Token.LIT, Type.INT, 1 if val[1] == 0 else 0)

#** operatoriaus mazgas
class expNode():

    def __init__(self, opLeft, opRight):
        self.opLeft = opLeft
        self.opRight = opRight

    def __repr__(self):
        return "{} ** {}".format(self.opLeft, self.opRight)

    def get(self):
        left = self.opLeft.get()
        if left[0] == Token.ID:
            tmp = scope.get(left[1])
            left = (Token.LIT, tmp[0], tmp[1])
        right = self.opRight.get()
        if right[0] == Token.ID:
            tmp = scope.get(right[1])
            right = (Token.LIT, tmp[0], tmp[1])
        if left[1] == Type.STR or right[1] == Type.STR:
            print("Operator ** cannot be applied to string")
            exit(PAR_INVALID_OP)
        else:
            if left[1] == Type.INT and right[1] == Type.INT:
                return (Token.LIT, Type.INT, left[2] ** right[2])
            else:
                return (Token.LIT, Type.DEC, left[2] ** right[2])


#*,/,% operatorių mazgas
class mulNode():

    def __init__(self, opLeft, operator, opRight):
        self.opLeft = opLeft
        self.operator = operator
        self.opRight = opRight

    def __repr__(self):
        if self.operator[0] == Token.MUL:
            return "{} * {}".format(self.opLeft, self.opRight)
        elif self.operator[0] == Token.DIV:
            return "{} / {}".format(self.opLeft, self.opRight)
        elif self.operator[0] == Token.MOD:
            return "{} % {}".format(self.opLeft, self.opRight)
        else:
            print("Multiplication operation parsing error")
            exit(Error.WTF)

    def get(self):
        left = self.opLeft.get()
        if left[0] == Token.ID:
            tmp = scope.get(left[1])
            left = (Token.LIT, tmp[0], tmp[1])
        right = self.opRight.get()
        if right[0] == Token.ID:
            tmp = scope.get(right[1])
            right = (Token.LIT, tmp[0], tmp[1])
        if self.operator[0] == Token.MUL:
            if left[1] == Type.STR or right[1] == Type.STR:
                print("Operator * cannot be applied to string")
                exit(PAR_INVALID_OP)
            else:
                if left[1] == Type.INT and right[1] == Type.INT:
                    return (Token.LIT, Type.INT, left[2] * right[2])
                else:
                    return (Token.LIT, Type.DEC, left[2] * right[2])
        elif self.operator[0] == Token.DIV:
            if left[1] == Type.STR or right[1] == Type.STR:
                print("Operator / cannot be applied to string")
                exit(PAR_INVALID_OP)
            else:
                if left[1] == Type.INT and right[1] == Type.INT:
                    return (Token.LIT, Type.INT, left[2] // right[2])
                else:
                    return (Token.LIT, Type.DEC, left[2] / right[2])
        elif self.operator[0] == Token.MOD:
            if left[1] == Type.STR or right[1] == Type.STR:
                print("Operator * cannot be applied to string")
                exit(PAR_INVALID_OP)
            else:
                if left[1] == Type.INT and right[1] == Type.INT:
                    return (Token.LIT, Type.INT, left[2] % right[2])
                else:
                    return (Token.LIT, Type.DEC, left[2] % right[2])
        else:
            print("Multiplication operation parsing error")
            exit(Error.WTF)

#+,- operatorių mazgas
class addNode():

    def __init__(self, opLeft, operator, opRight):
        self.opLeft = opLeft
        self.operator = operator
        self.opRight = opRight

    def __repr__(self):
        if self.operator[0] == Token.PLUS:
            return "{} + {}".format(self.opLeft, self.opRight)
        elif self.operator[0] == Token.MINUS:
            return "{} - {}".format(self.opLeft, self.opRight)
        else:
            print("Multiplication operation parsing error")
            exit(Error.WTF)

    def get(self):
        left = self.opLeft.get()
        if left[0] == Token.ID:
            tmp = scope.get(left[1])
            if tmp is None:
                print("Variable {} not fount!".format(left[1]))
                exit(Error.PAR_UNKNOWN_VAL)
            left = (Token.LIT, tmp[0], tmp[1])
        right = self.opRight.get()
        if right[0] == Token.ID:
            tmp = scope.get(right[1])
            if tmp is None:
                print("Variable {} not fount!".format(right[1]))
                exit(Error.PAR_UNKNOWN_VAL)
            right = (Token.LIT, tmp[0], tmp[1])
        if self.operator[0] == Token.PLUS:
            if left[1] == Type.STR or right[1] == Type.STR:
                return (Token.LIT, Type.STR, str(left[2]) + str(right[2]))
            else:
                if left[1] == Type.INT and right[1] == Type.INT:
                    return (Token.LIT, Type.INT, left[2] + right[2])
                else:
                    return (Token.LIT, Type.DEC, left[2] + right[2])
        elif self.operator[0] == Token.MINUS:
            if left[1] == Type.STR or right[1] == Type.STR:
                print("Operator - cannot be applied to string")
                exit(PAR_INVALID_OP)
            else:
                if left[1] == Type.INT and right[1] == Type.INT:
                    return (Token.LIT, Type.INT, left[2] - right[2])
                else:
                    return (Token.LIT, Type.DEC, left[2] - right[2])
        else:
            print("Addition operation parsing error")
            exit(Error.WTF)


#<, <=, >, >= operatorių mazgas
class cmpNode():

    def __init__(self, opLeft, operator, opRight):
        self.opLeft = opLeft
        self.operator = operator
        self.opRight = opRight

    def __repr__(self):
        if self.operator[0] == Token.LT:
            return "{} < {}".format(self.opLeft, self.opRight)
        elif self.operator[0] == Token.LTEQ:
            return "{} <= {}".format(self.opLeft, self.opRight)
        if self.operator[0] == Token.GT:
            return "{} > {}".format(self.opLeft, self.opRight)
        elif self.operator[0] == Token.GTEQ:
            return "{} >= {}".format(self.opLeft, self.opRight)
        elif self.operator[0] == Token.LTGT:
            return "{} <> {}".format(self.opLeft, self.opRight)
        else:
            print("Comparison operation parsing error")
            exit(Error.WTF)

    def get(self):
        left = self.opLeft.get()
        if left[0] == Token.ID:
            tmp = scope.get(left[1])
            if tmp is None:
                print("Variable ", left[1], "not found")
                exit(Error.PAR_UNKNOWN_VAL)
            left = (Token.LIT, tmp[0], tmp[1])
        right = self.opRight.get()
        if right[0] == Token.ID:
            tmp = scope.get(right[1])
            if tmp is None:
                print("Variable ", right[1], "not found")
                exit(Error.PAR_UNKNOWN_VAL)
            right = (Token.LIT, tmp[0], tmp[1])
        if self.operator[0] == Token.LT:
            if left[1] == Type.STR or right[1] == Type.STR:
                print("Operator < cannot be applied to string")
                exit(Error.PAR_INVALID_OP)
            else:
                return (Token.LIT, Type.INT, 1 if left[2] < right[2] else 0)
        elif self.operator[0] == Token.LTEQ:
            if left[1] == Type.STR or right[1] == Type.STR:
                print("Operator <= cannot be applied to string")
                exit(Error.PAR_INVALID_OP)
            else:
                return (Token.LIT, Type.INT, 1 if left[2] <= right[2] else 0)
        elif self.operator[0] == Token.GT:
            if left[1] == Type.STR or right[1] == Type.STR:
                print("Operator > cannot be applied to string")
                exit(Error.PAR_INVALID_OP)
            else:
                return (Token.LIT, Type.INT, 1 if left[2] > right[2] else 0)
        elif self.operator[0] == Token.GTEQ:
            if left[1] == Type.STR or right[1] == Type.STR:
                print("Operator >= cannot be applied to string")
                exit(Error.PAR_INVALID_OP)
            else:
                return (Token.LIT, Type.INT, 1 if left[2] >= right[2] else 0)
        elif self.operator[0] == Token.LTGT:
            if left[1] == Type.STR or right[1] == Type.STR:
                print("Operator <> cannot be applied to string")
                exit(Error.PAR_INVALID_OP)
            else:
                return (Token.LIT, Type.INT, 1 if left[2] < right[2] or left[2] > right[2] else 0)
        else:
            print("Comparison operation parsing error")
            exit(Error.WTF)

#==, != operatorių mazgas
class eqNode():

    def __init__(self, opLeft, operator, opRight):
        self.opLeft = opLeft
        self.operator = operator
        self.opRight = opRight

    def __repr__(self):
        if self.operator[0] == Token.EQEQ:
            return "{} == {}".format(self.opLeft, self.opRight)
        elif self.operator[0] == Token.NEQ:
            return "{} != {}".format(self.opLeft, self.opRight)
        else:
            print("Comparison operation parsing error")
            exit(Error.WTF)

    def get(self):
        left = self.opLeft.get()
        if left[0] == Token.ID:
            tmp = scope.get(left[1])
            if tmp is None:
                print("Variable {} not fount!".format(left[1]))
                exit(Error.PAR_UNKNOWN_VAL)
            left = (Token.LIT, tmp[0], tmp[1])
        right = self.opRight.get()
        if right[0] == Token.ID:
            tmp = scope.get(right[1])
            if tmp is None:
                print("Variable {} not fount!".format(right[1]))
                exit(Error.PAR_UNKNOWN_VAL)
            right = (Token.LIT, tmp[0], tmp[1])
        if self.operator[0] == Token.EQEQ:
            return (Token.LIT, Type.INT, 1 if left[2] == right[2] else 0)
        elif self.operator[0] == Token.NEQ:
            return (Token.LIT, Type.INT, 1 if left[2] != right[2] else 0)
        else:
            print("Equality operation parsing error")
            exit(Error.WTF)

#& operatoriaus mazgas
class andNode():

    def __init__(self, opLeft, opRight):
        self.opLeft = opLeft
        self.opRight = opRight

    def __repr__(self):
        return "{} & {}".format(self.opLeft, self.opRight)

    def get(self):
        left = self.opLeft.get()
        if left[0] == Token.ID:
            tmp = scope.get(left[1])
            if tmp is None:
                print("Variable {} not fount!".format(left[1]))
                exit(Error.PAR_UNKNOWN_VAL)
            left = (Token.LIT, tmp[0], tmp[1])
        right = self.opRight.get()
        if right[0] == Token.ID:
            tmp = scope.get(right[1])
            if tmp is None:
                print("Variable {} not fount!".format(right[1]))
                exit(Error.PAR_UNKNOWN_VAL)
            right = (Token.LIT, tmp[0], tmp[1])
        return (Token.LIT, Type.INT, 1 if left[2] != 0 and right[2] != 0 else 0)


#^ operatoriaus mazgas
class xorNode():

    def __init__(self, opLeft, opRight):
        self.opLeft = opLeft
        self.opRight = opRight

    def __repr__(self):
        return "{} ^ {}".format(self.opLeft, self.opRight)

    def get(self):
        left = self.opLeft.get()
        if left[0] == Token.ID:
            tmp = scope.get(left[1])
            if tmp is None:
                print("Variable {} not fount!".format(left[1]))
                exit(Error.PAR_UNKNOWN_VAL)
            left = (Token.LIT, tmp[0], tmp[1])
        right = self.opRight.get()
        if right[0] == Token.ID:
            tmp = scope.get(right[1])
            if tmp is None:
                print("Variable {} not fount!".format(right[1]))
                exit(Error.PAR_UNKNOWN_VAL)
            right = (Token.LIT, tmp[0], tmp[1])
        return (Token.LIT, Type.INT, 1 if (left[2] != 0 and right[2] == 0) or (left[2] == 0 and right[2] != 0) else 0)


#| operatoriaus mazgas
class orNode():

    def __init__(self, opLeft, opRight):
        self.opLeft = opLeft
        self.opRight = opRight

    def __repr__(self):
        return "{} | {}".format(self.opLeft, self.opRight)

    def get(self):
        left = self.opLeft.get()
        if left[0] == Token.ID:
            tmp = scope.get(left[1])
            if tmp is None:
                print("Variable {} not fount!".format(left[1]))
                exit(Error.PAR_UNKNOWN_VAL)
            left = (Token.LIT, tmp[0], tmp[1])
        right = self.opRight.get()
        if right[0] == Token.ID:
            tmp = scope.get(right[1])
            if tmp is None:
                print("Variable {} not fount!".format(right[1]))
                exit(Error.PAR_UNKNOWN_VAL)
            right = (Token.LIT, tmp[0], tmp[1])
        return (Token.LIT, Type.INT, 1 if left[2] != 0 or right[2] != 0 else 0)


#Trinario operatoriaus mazgas
class ternOpNode():

    def __init__(self, cond, oif, oelse):
        self.cond = cond
        self.oif = oif
        self.oelse = oelse

    def __repr__(self):
        return "{} ? {} : {}".format(self.cond, self.oif, self.oelse)

    def get(self):
        cnd = self.cond.get()
        if cnd [0] == Token.ID:
            tmp = scope.get(cnd[1])
            if tmp is None:
                print("Variable {} not fount!".format(cnd[1]))
                exit(Error.PAR_UNKNOWN_VAL)
            cnd = (Token.LIT, tmp[0], tmp[1])
        if cnd[1] != Type.INT:
            print("Only int can be used for conditions")
            exit(Err.PAR_INVALID)
        else:
            if cnd[2] == 0:
                return self.oelse.get()
            else:
                return self.oif.get()


#Priskyrimo operatoriaus mazgas
class assignNode():

    def __init__(self, opLeft, opRight):
        self.opLeft = opLeft
        self.opRight = opRight

    def __repr__(self):
        return "{} = {}".format(self.opLeft, self.opRight)

    def get(self):
        left = self.opLeft.get()
        if(left[0] != Token.ID):
            print("Must assign to variable")
            exit(Error.PAR_INVALID)
        else:
            right = self.opRight.get()
            if right[0] == Token.ID:
                tmp = scope.get(right[1])
                if tmp is None:
                    print("Variable {} not fount!".format(right[1]))
                    exit(Error.PAR_UNKNOWN_VAL)
                right = (Token.LIT, tmp[0], tmp[1])
            if not scope.replace(left[1], (right[1], right[2])):
                scope.push(left[1], (right[1], right[2]))
            return (Token.ID, left[1])
            
        
#Sukeitimo operatoriaus mazgas
class swapNode():

    def __init__(self, opLeft, opRight):
        self.opLeft = opLeft
        self.opRight = opRight

    def __repr__(self):
        return "{} <=> {}".format(self.opLeft, self.opRight)

    def get(self):
        left = self.opLeft.get()
        right = self.opRight.get()
        if left[0] != Token.ID or right[0] != Token.ID:
            print("Can only swap variables")
            exit(Error.PAR_INVALID_OP)
        else:
            valLeft = scope.get(left[1])
            valRight = scope.get(right[1])
            if not scope.replace(left[1], valRight):
                print("Variable ", left[1], " not found.")
                exit(Error.PAR_UNKNOWN_VAL)
            if not scope.replace(right[1], valLeft):
                print("Variable ", right[1], " not found.")
                exit(Error.PAR_UNKNOWN_VAL)
            return (Token.ID, left[1])

#Išraiškos mazgas
class expressionNode():

    def __init__(self, children):
        self.children = children

    def __repr__(self):
        rep = ""
        for child in self.children:
            rep += "{},".format(child)
        rep = rep[:-1]
        return rep

    def get(self):
        lst = []
        for child in self.children:
            lst.append(child.get())
        return lst

#Teiginių mazgai
#Išraiškos teiginio mazgas:
class expressionStatementNode():

    def __init__(self, expr):
        self.expr = expr

    def __repr__(self):
        return "{};".format(self.expr)

    def execute(self):
        if self.expr is not None:
            self.expr.get()
        return None

#Grąžinimo teiginio mazgas:
class returnStatementNode():

    def __init__(self, expr):
        self.expr = expr

    def __repr__(self):
        return "return {};".format(self.expr)

    def execute(self):
        if self.expr is None:
            return None
        else:
            rez = self.expr.get();
            if len(rez) > 1:
                print("Can only return one value!")
                exit(Error.RET_ONE)
            elif len(rez) == 0:
                exit(Error.RET_ONE)
            else:
                rez = rez[0]
                if rez[0] == Token.ID:
                    var = scope.get(rez[1])
                    if var is None:
                        print("Variable {} not fount!".format(rez[1]))
                        exit(Error.PAR_UNKNOWN_VAL)
                    rez = (Token.LIT, var[0], var[1])
                return rez

#Bloko mazgas:
class blockNode():
    
    def __init__(self, statements):
        self.statements = statements

    def __repr__(self):
        string = "{"
        for st in self.statements:
            string += str(st)
        string += "}"
        return string

    def execute(self):
        if self.statements is not None:
            retval = None
            scope.inc()
            for st in self.statements:
                retval = st.execute();
                if retval is not None:
                    break
            scope.dec()
            return retval


#do-while mazgas:
class doWhileNode():

    def __init__(self, stm, cond):
        self.stm = stm
        self.cond = cond

    def __repr__(self):
        return "do {} while ({})".format(self.stm, self.cond)

    def execute(self):
        retval = self.stm.execute()
        cnt = self.cond.get()
        if len(cnt) != 1:
            print("Condition must be a single value")
            exit(Error.PAR_INVALID_OP)
        else:
            cnt = cnt[0]
        if cnt[0] != Token.LIT or cnt[1] != Type.INT:
            print("Condition must be type int")
            exit(Error.PAR_INVALID_OP)
        while(cnt[2] != 0):
            retval = self.stm.execute()
            if retval is not None:
                return retval
            cnt = self.cond.get()
            if len(cnt) != 1:
                print("Condition must be a single value")
                exit(Error.PAR_INVALID_OP)
            else:
                cnt = cnt[0]
        return None

#if-else mazgas
class ifElseNode():

    def __init__(self, cond, stmIf, stmElse):
        self.cond = cond
        self.stmIf = stmIf
        self.stmElse = stmElse

    def __repr__(self):
        return "if ({}) {} else {}".format(self.cond, self.stmIf, self.stmElse)

    def execute(self):
        retval = None
        cnd = self.cond.get()
        if len(cnd) != 1:
            print("Condition must be a single value")
            exit(Error.PAR_INVALID_OP)
        else:
            cnd = cnd[0]
        if cnd[0] != Token.LIT or cnd[1] != Type.INT:
            print("Condition must be type int")
            exit(Error.PAR_INVALID_OP)
        if cnd[2] != 0:
            retval = self.stmIf.execute()
            if retval is not None:
                return retval
        elif cnd[2] == 0:
            retval = self.stmElse.execute()
            if retval is not None:
                return retval
        else:
            print("If-else error")
            exit(Error.WTF)
        return None

#while mazgas:
class whileNode():

    def __init__(self, cond, stm):
        self.stm = stm
        self.cond = cond

    def __repr__(self):
        return "while ({}) {}".format(self.cond, self.stm)

    def execute(self):
        retval = None
        cnt = self.cond.get()
        if len(cnt) != 1:
            print("Condition must be a single value")
            exit(Error.PAR_INVALID_OP)
        else:
            cnt = cnt[0]
        if cnt[0] != Token.LIT or cnt[1] != Type.INT:
            print("Condition must be type int")
            exit(Error.PAR_INVALID_OP)
        while(cnt[2] != 0):
            retval = self.stm.execute()
            cnt = self.cond.get()
            if len(cnt) != 1:
                print("Condition must be a single value")
                exit(Error.PAR_INVALID_OP)
            else:
                cnt = cnt[0]
            if retval is not None:
                return retval
        return None
            

#for mazgas
class forNode():

    def __init__(self, arg1, arg2, arg3, stm):
        self.arg1 = arg1
        self.arg2 = arg2
        self.arg3 = arg3
        self.stm = stm

    def __repr__(self):
        return "for({},{},{}){}".format(self.arg1, self.arg2, self.arg3, self.stm)

    def execute(self):
        retval = None
        if self.arg1 is not None:
            self.arg1.get()
        cnt = self.arg2.get()
        if len(cnt) != 1:
            print("Condition must be a single value")
            exit(Error.PAR_INVALID_OP)
        else:
            cnt = cnt[0]
        if cnt[0] != Token.LIT or cnt[1] != Type.INT:
            print("Condition must be type int")
            exit(Error.PAR_INVALID_OP)
        while(cnt[2] != 0):
            retval = self.stm.execute()
            if retval is not None:
                return retval
            self.arg3.get()
            cnt = self.arg2.get()
            if len(cnt) != 1:
                print("Condition must be a single value")
                exit(Error.PAR_INVALID_OP)
            else:
                cnt = cnt[0]
        return None

#if mazgas
class ifNode():

    def __init__(self, cond, stmIf):
        self.cond = cond
        self.stmIf = stmIf

    def __repr__(self):
        return "if ({}) {}".format(self.cond, self.stmIf)

    def execute(self):
        retval = None
        cnd = self.cond.get()
        if len(cnd) != 1:
            print("Condition must be a single value")
            exit(Error.PAR_INVALID_OP)
        else:
            cnd = cnd[0]
        if cnd[0] != Token.LIT or cnd[1] != Type.INT:
            print("Condition must be type int")
            exit(Error.PAR_INVALID_OP)
        if cnd[2] != 0:
            return self.stmIf.execute()

#Kintamojo paskelbimo mazgas - be reikšmės
class variableDeclarationEmptyNode():

    def __init__(self, typeTok, idTok):
        self.typeTok = typeTok
        self.idTok = idTok

    def __repr__(self):
        return "{} {};".format("INT" if self.typeTok[1] == Type.INT else "DEC" if self.typeTok[1] == Type.DEC else "string", self.idTok[1])

    def execute(self):
        if self.typeTok[1] == Type.INT:
            scope.push(self.idTok[1], (Type.INT, 0))
        elif self.typeTok[1] == Type.DEC:
            scope.push(self.idTok[1], (Type.DEC, Decimal(0)))
        elif self.typeTok[1] == Type.STR:
            scope.push(self.idTok[1], (Type.STR, ""))
        return None

#Kintamojo paskelbimo mazgas - nurodoma reikšmė
class variableDeclarationNode():

    def __init__(self, typeTok, idTok, expr):
        self.typeTok = typeTok
        self.idTok = idTok
        self.expr = expr

    def __repr__(self):
        return "{} {} = {};".format("INT" if self.typeTok[1] == Type.INT else "DEC" if self.typeTok[1] == Type.DEC else "string", self.idTok[1], self.expr)

    def execute(self):
        val = self.expr.get()
        if val[0] == Token.ID:
            val = scope.get(val[1])
            if tmp is None:
                print("Variable {} not fount!".format(val[1]))
                exit(Error.PAR_UNKNOWN_VAL)
            val = (Token.LIT, val[0], val[1])
        if self.typeTok[1] == Type.INT:
            if val[1] != Type.INT:
                print("Int expected")
                exit(Error.PAR_EXPECTED)
            scope.push(self.idTok[1], (Type.INT, val[2]))
        elif self.typeTok[1] == Type.DEC:
            if val[1] != Type.INT and val[1] != Type.DEC:
                print("Decimal expected")
                exit(Error.PAR_EXPECTED)
            scope.push(self.idTok[1], (Type.DEC, Decimal(val[2])))
        elif self.typeTok[1] == Type.STR:
            if val[1] != Type.STR:
                print("String expected")
                exit(Error.PAR_EXPECTED)
            scope.push(self.idTok[1], (Type.STR, val[2]))
        return None

#Funkcija
class function():

    def __init__(self, params, block):
        self.params = params
        self.block = block

    def __repr__(self):
        return "({}){}".format(self.params, self.block)

    def execute(self, params):
        if len(params) < len(self.params):
            print("Not enough parameters.")
            exit(Error.PAR_EXPECTED)
        elif len(params) > len(self.params):
            print("Too many parameters.")
            exit(Error.PAR_EXPECTED)
        if self.block is not None:
            i = 0;
            while i < len(params):
                scope.push(self.params[i][1][1], (params[i][1], params[i][2]))
                i += 1
            returnval = self.block.execute()
            return returnval;

#Funkcijos prototipo mazgas
class functionPrototypeNode():

    def __init__(self, idToks, params = []):
        if len(idToks) == 1:
            self.type = None
            self.id = idToks[0][1];
            self.params = params
        elif len(idToks) == 2:
            self.type = idToks[0][1]
            self.id = idToks[1][1]
            self.params = params
        else:
            print("Invalid function ID!")
            exit(Error.WTF)

    def __repr__(self):
        pars = ""
        i = 0;
        while i < len(self.params):
            param = self.params[i];
            pars += "int " if param[0][1] == Type.INT else "dec " if param[0][1] == Type.DEC else "string " if param[0][1] == Type.STR else ""
            pars += param[1][1]
            i += 1
            if i < len(self.params):
                pars += ","
        return "{}{}({});".format("int " if self.type == Type.INT else "dec " if self.type == Type.DEC else "string " if self.type == Type.STR else "", self.id, pars)

    def execute(self):
        functions[self.id]=(function(self.params, []))

#Funkcijos paskelbimo mazgas
class functionDeclarationNode():

    def __init__(self, idToks, block, params = []):
        if len(idToks) == 1:
            self.type = None
            self.id = idToks[0][1];
            self.params = params
            self.block = block
        elif len(idToks) == 2:
            self.type = idToks[0][1]
            self.id = idToks[1][1]
            self.params = params
            self.block = block
        else:
            print("Invalid function ID!")
            exit(Error.WTF)

    def __repr__(self):
        pars = ""
        i = 0;
        while i < len(self.params):
            param = self.params[i];
            pars += "int " if param[0][1] == Type.INT else "dec " if param[0][1] == Type.DEC else "string " if param[0][1] == Type.STR else ""
            pars += param[1][1]
            i += 1
            if i < len(self.params):
                pars += ","
        return "{}{}({}){}".format("int " if self.type == Type.INT else "dec " if self.type == Type.DEC else "string " if self.type == Type.STR else "", self.id, pars, self.block)

    def execute(self):
        functions[self.id]=(function(self.params, self.block))

#Funkcijos kvietimo mazgas
class functionCallNode():

    def __init__(self, funcID, args):
        self.funcID = funcID[1]
        self.args = args

    def __repr__(self):
        return "{}({})".format(self.funcID, self.args)

    def get(self):
        scope.inc()
        args = [] if self.args is None else self.args.get()
        if args:
            i = 0
            while i < len(args):
                if args[i][0] == Token.ID:
                    var = scope.get(args[i][1])
                    if var is None:
                        print("Variable {} not fount!".format(args[i][1]))
                        exit(Error.PAR_UNKNOWN_VAL)
                    args[i] = (Token.LIT, var[0], var[1])
                i +=1;
        rez = functions[self.funcID].execute(args)
        scope.dec()
        return rez
        

#Išraiškų taisyklės    
#<value> taisyklė
def value(tokens):
    if not tokens:
        return None
    valueTokens = [tokens.pop(0)];
    if valueTokens[0][0] == Token.ROUNDBRACKETLEFT:
        valueTokens.extend(getRoundsToClose(tokens, True))
        debracketRound(valueTokens)
        return expression(valueTokens)
    elif valueTokens[0][0] == Token.LIT:
        return valueNode(valueTokens[0])
    elif valueTokens[0][0] == Token.ID:
        if tokens:
            valueTokens.append(tokens.pop(0))
            if valueTokens[1][0] == Token.ROUNDBRACKETLEFT: #funckijos kvietimas - reiks tvarkyti, kai implementuosim metodus
                valueTokens.extend(getRoundsToClose(tokens, True))
                funcIDToken = valueTokens.pop(0)
                debracketRound(valueTokens)
                funcArgs = argument(valueTokens)
                return functionCallNode(funcIDToken, funcArgs)
            elif valueTokens[1][0] != Token.ID:
                return valueNode(valueTokens[0])
        else:
            return valueNode(valueTokens[0])
    else:
        print("Parsing error")
        exit(Error.WTF)


#<opFetch> taisyklė:
def opFetch(tokens):
    if not tokens:
        return None
    fetchTokens = [tokens.pop()]
    if fetchTokens[0][0] == Token.SQUAREBRACKETRIGHT: #Vieta, kurioje būtų realizuojamas masyvo iškvietimas
        print("Processing array")
        fetchTokens.extend(getSquaresToClose(tokens, False))
        fetchTokens.pop(0)
        fetchTokens.pop()
        return value(fetchTokens)
    else: #Nerastas masyvas - turim paprastą reikšmę
        tokens.extend(fetchTokens)
        valueNode = value(tokens)
        return valueNode

#<opUnary> taisyklė
def opUnary(tokens):
    if not tokens:
        return None
    if tokens[0][0] == Token.NEG:
        tokens.pop(0)
        uno = opUnary(tokens)
        neg = negNode(uno)
        return neg
    elif tokens[0][0] == Token.DOUBLEP:
        tokens.pop(0)
        uno = unaryNode(Token.DOUBLEP, opUnary(tokens), True)
        return uno
    elif tokens[0][0] == Token.DOUBLEM:
        tokens.pop(0)
        uno = unaryNode(Token.DOUBLEM, opUnary(tokens), True)
        return uno
    elif tokens[-1][0] == Token.DOUBLEP:
        tokens.pop()
        fetch = opFetch(tokens)
        uno = unaryNode(Token.DOUBLEP, fetch, False)
        return uno
    elif tokens[-1][0] == Token.DOUBLEM:
        tokens.pop()
        fetch = opFetch(tokens)
        uno = unaryNode(Token.DOUBLEM, fetch, False)
        return uno
    else:
        return opFetch(tokens)

#<opExp> taisyklė
def opExp(tokens):
    if not tokens:
        return None
    opTokens = []
    depth = 0;
    while tokens:
        tok = tokens.pop()
        if tok[0] == Token.ROUNDBRACKETRIGHT:
            depth += 1
        elif tok[0] == Token.ROUNDBRACKETLEFT:
            depth -= 1
        if depth == 0 and opTokens:
            if tok[0] == Token.EXP:
                exp = opExp(tokens)
                uno = opUnary(opTokens)
                node = expNode(exp, uno)
                return node
            else:
                opTokens.insert(0, tok)
        else:
            opTokens.insert(0, tok)
    return opUnary(opTokens)

#<opMul> taisyklė
def opMul(tokens):
    if not tokens:
        return None
    opTokens = []
    depth = 0
    while tokens:
        tok = tokens.pop()
        if tok[0] == Token.ROUNDBRACKETRIGHT:
            depth += 1
        elif tok[0] == Token.ROUNDBRACKETLEFT:
            depth -= 1
        if depth == 0 and opTokens:
            if tok[0] == Token.MUL or tok[0] == Token.DIV or tok[0] == Token.MOD:
                mul = opMul(tokens)
                exp = opExp(opTokens)
                node = mulNode(mul, tok, exp)
                return node
            else:
                opTokens.insert(0, tok)
        else:
            opTokens.insert(0, tok)
    return opExp(opTokens)

#opAdd taisyklė
def opAdd(tokens):
    if not tokens:
        return None
    opTokens = []
    depth = 0
    while tokens:
        tok = tokens.pop()
        if tok[0] == Token.ROUNDBRACKETRIGHT:
            depth += 1
        elif tok[0] == Token.ROUNDBRACKETLEFT:
            depth -= 1
        if depth == 0 and opTokens:
            if tok[0] == Token.PLUS or tok[0] == Token.MINUS:
                add = opAdd(tokens)
                mul = opMul(opTokens)
                node = addNode(add, tok, mul)
                return node
            else:
                opTokens.insert(0, tok)
        else:
            opTokens.insert(0, tok)
    return opMul(opTokens)

#<opCmp> taisyklė
def opCmp(tokens):
    if not tokens:
        return None
    opTokens = []
    depth = 0
    while tokens:
        tok = tokens.pop()
        if tok[0] == Token.ROUNDBRACKETRIGHT:
            depth += 1
        elif tok[0] == Token.ROUNDBRACKETLEFT:
            depth -= 1
        if depth == 0 and opTokens:
            if tok[0] == Token.LT or tok[0] == Token.LTEQ or tok[0] == Token.GT or tok[0] == Token.GTEQ or tok[0] == Token.LTGT:
                cmp = opCmp(tokens)
                add = opAdd(opTokens)
                node = cmpNode(cmp, tok, add)
                return node
            else:
                opTokens.insert(0, tok)
        else:
            opTokens.insert(0, tok)
    return opAdd(opTokens)

#<opEq> taisyklė
def opEq(tokens):
    if not tokens:
        return None
    opTokens = []
    depth = 0
    while tokens:
        tok = tokens.pop()
        if tok[0] == Token.ROUNDBRACKETRIGHT:
            depth += 1
        elif tok[0] == Token.ROUNDBRACKETLEFT:
            depth -= 1
        if depth == 0 and opTokens:
            if tok[0] == Token.EQEQ or tok[0] == Token.NEQ:
                eq = opEq(tokens)
                cmp = opCmp(opTokens)
                node = eqNode(eq, tok, cmp)
                return node
            else:
                opTokens.insert(0, tok)
        else:
            opTokens.insert(0, tok)
    return opCmp(opTokens)

#<opAnd> taisyklė
def opAnd(tokens):
    if not tokens:
        return None
    opTokens = []
    depth = 0
    while tokens:
        tok = tokens.pop()
        if tok[0] == Token.ROUNDBRACKETRIGHT:
            depth += 1
        elif tok[0] == Token.ROUNDBRACKETLEFT:
            depth -= 1
        if depth == 0 and opTokens:
            if tok[0] == Token.AND:
                nd = opAnd(tokens)
                eq = opEq(opTokens)
                node = andNode(nd, eq)
                return node
            else:
                opTokens.insert(0, tok)
        else:
            opTokens.insert(0, tok)
    return opEq(opTokens)

#<opXor> taisyklė
def opXor(tokens):
    if not tokens:
        return None
    opTokens = []
    depth = 0
    while tokens:
        tok = tokens.pop()
        if tok[0] == Token.ROUNDBRACKETRIGHT:
            depth += 1
        elif tok[0] == Token.ROUNDBRACKETLEFT:
            depth -= 1
        if depth == 0 and opTokens:
            if tok[0] == Token.XOR:
                xor = opXor(tokens)
                nd = opAnd(opTokens)
                node = xorNode(xor, nd)
                return node
            else:
                opTokens.insert(0, tok)
        else:
            opTokens.insert(0, tok)
    return opAnd(opTokens)

#opOr taisyklė
def opOr(tokens):
    if not tokens:
        return None
    opTokens = []
    depth = 0
    while tokens:
        tok = tokens.pop()
        if tok[0] == Token.ROUNDBRACKETRIGHT:
            depth += 1
        elif tok[0] == Token.ROUNDBRACKETLEFT:
            depth -= 1
        if depth == 0 and opTokens:
            if tok[0] == Token.OR:
                oor = opOr(tokens)
                xor = opXor(opTokens)
                node = orNode(oor, xor)
                return node
            else:
                opTokens.insert(0, tok)
        else:
            opTokens.insert(0, tok)
    return opXor(opTokens)

#opIf taisyklė
def opIf(tokens):
    if not tokens:
        return None
    elseTokens = []
    ifTokens = []
    orTokens = []
    depth = 0
    elseFound = False
    ifFound = False
    while tokens:
        tok = tokens.pop()
        if tok[0] == Token.ROUNDBRACKETRIGHT:
            depth += 1
        elif tok[0] == Token.ROUNDBRACKETLEFT:
            depth -= 1
        if depth == 0:
            if not elseFound:
                if elseTokens:
                    if tok[0] == Token.COLON:
                        elseFound = True
                    else:
                        elseTokens.insert(0, tok)
                else:
                    elseTokens.insert(0, tok)
            elif elseFound and not ifFound:
                if ifTokens:
                    if tok[0] == Token.QMARK:
                        ifFound = True
                    else:
                        ifTokens.insert(0, tok)
                else:
                    ifTokens.insert(0, tok)
            elif ifFound:
                orTokens.insert(0, tok)
                while tokens:
                    orTokens.insert(0, tokens.pop())
                cond = opOr(orTokens)
                oif = opIf(ifTokens)
                oelse = opIf(elseTokens)
                return ternOpNode(cond, oif, oelse)
        else:
            if not elseFound:
                elseTokens.insert(0, tok)
            elif ifFound and not elseFound:
                ifTokens.insert(0, tok)
            elif ifFound:
                orTokens.insert(0, tok)
            else:
                print("Error parsing ternary operator: ? expected")
                exit(Error.PAR_EXPECTED)
    return opOr(elseTokens)

#<opAssign> taisyklė
def opAssign(tokens):
    if not tokens:
        return None
    opTokens = []
    depth = 0
    while tokens:
        tok = tokens.pop()
        if tok[0] == Token.ROUNDBRACKETRIGHT:
            depth += 1
        elif tok[0] == Token.ROUNDBRACKETLEFT:
            depth -= 1
        if depth == 0 and opTokens:
            if tok[0] == Token.EQUALS:
                oif = opIf(tokens)
                ass = opAssign(opTokens)
                node = assignNode(oif, ass)
                return node
            else:
                opTokens.insert(0, tok)
        else:
            opTokens.insert(0, tok)
    return opIf(opTokens)

#<opSwap> taisyklė
def opSwap(tokens):
    if not tokens:
        return None
    opTokens = []
    depth = 0
    while tokens:
        tok = tokens.pop()
        if tok[0] == Token.ROUNDBRACKETRIGHT:
            depth += 1
        elif tok[0] == Token.ROUNDBRACKETLEFT:
            depth -= 1
        if depth == 0 and opTokens:
            if tok[0] == Token.SWAP:
                ass = opAssign(tokens)
                swap = opSwap(opTokens)
                node = swapNode(ass, swap)
                return node
            else:
                opTokens.insert(0, tok)
        else:
            opTokens.insert(0, tok)
    return opAssign(opTokens)

#<expression> taisyklė
def expression(tokens):
    if not tokens:
        return None
    opTokens = []
    subexpressions = []
    depth = 0
    while tokens:
        tok = tokens.pop()
        if tok[0] == Token.ROUNDBRACKETRIGHT:
            depth += 1
        elif tok[0] == Token.ROUNDBRACKETLEFT:
            depth -= 1
        if depth == 0 and opTokens:
            if tok[0] == Token.COMMA:
                swap = opSwap(opTokens)
                subexpressions.insert(0, swap)
                opTokens = []
            else:
                opTokens.insert(0, tok)
        else:
            opTokens.insert(0, tok)
    if opTokens:
        swap = opSwap(opTokens)
        subexpressions.insert(0, swap)
        opTokens = []
    return expressionNode(subexpressions)

#Teiginių taisyklės

#Argumentas - kintamojo skelbimas negalimas, reikia paskelbti prieš naudojant!
def argument(tokens):
    if not tokens:
        return None
    expr = expression(tokens)
    return expr
    
#<normalStatement>
def normalStatement(tokens):
    if not tokens:
        return None
    stmTokens = []
    stmTokens.append(tokens.pop(0));
    if stmTokens[0][0] == Token.DO:
        stmTokens.pop(0)
        depth = 0
        whileFound = False
        while tokens:
            tok = tokens.pop(0);
            if tok[0] == Token.ROUNDBRACKETLEFT:
                stmTokens.append(tok)
                stmTokens.extend(getRoundsToClose(tokens, True))
            if tok[0] == Token.WHILE:
                whileFound = True
                if not tokens:
                    print("( expected after while")
                    exit(Error.PAR_EXPECTED)
                else:
                    tok = tokens.pop(0)
                    if tok[0] != Token.ROUNDBRACKETLEFT:
                        print("( expected after while")
                        exit(Error.PAR_EXPECTED)
                    whileTokens = [tok] + getRoundsToClose(tokens, True)
                    debracketRound(whileTokens)
                    whileExp = expression(whileTokens)
                    stm = statement(stmTokens)
                    node = doWhileNode(stm, whileExp)
                    return node
            else:
                stmTokens.append(tok)
    elif stmTokens[0][0] == Token.CURLYBRACELEFT:
        depth = 1;
        while depth > 0 and  tokens:
            stmTokens.append(tokens.pop(0))
            if stmTokens[-1][0] == Token.CURLYBRACELEFT:
                depth += 1
            elif stmTokens[-1][0] == Token.CURLYBRACERIGHT:
                depth -= 1
        if stmTokens[-1][0] != Token.CURLYBRACERIGHT:
            print("} expected!")
            exit(Error.PAR_EXPECTED)
        else:
            stmTokens.pop(0)
            stmTokens.pop()
            statements = statementList(stmTokens)
            return blockNode(statements)
    else:
        depth = 0;
        while tokens:
            tok = tokens.pop(0)
            stmTokens.append(tok)
            if stmTokens[0][0] == Token.ROUNDBRACKETLEFT:
                stmTokens.extend(getRoundsToClose(tokens, True))
            if stmTokens[-1][0] == Token.SEMICOLON:
                stmTokens.pop()
                break;
        if stmTokens[0][0] == Token.RETURN:
            stmTokens.pop(0)
            expr = expression(stmTokens)
            return returnStatementNode(expr)
        else:
            expr = expression(stmTokens)
            return expressionStatementNode(expr)
    #Teoriškai iki čia neturėtų būti prieinama?
    print("Extra Statement parsed?")
    return statement(tokens)

#<thenStatement>
def thenStatement(tokens):
    if not tokens:
        return None
    tok = tokens.pop(0)
    if tok[0] == Token.IF:
        tok = tokens.pop(0)
        if tok[0] != Token.ROUNDBRACKETLEFT:
            print("( expected after if")
            exit(Error.PAR_EXPECTED)
        else:
            tokExpr = []
            tokExpr.append(tok)
            tokExpr.extend(getRoundsToClose(tokens, True))
            thenTok = []
            elseTok = []
            depth = 0
            elseFound = False
            while tokens:
                while not elseFound:
                    tok = tokens.pop(0)
                    if tok[0] == Token.ROUNDBRACKETLEFT:
                        thenTok.append(tok)
                        thenTok.extend(getRoundsToClose(tokens, True))
                    elif tok[0] == Token.CURLYBRACELEFT:
                        thenTok.append(tok)
                        thenTok.extend(getCurliesToClose((tokens, True)))
                    elif tok[0] == Token.ELSE:
                            elseFound = True
                    else:
                        thenTok.append(tok)
            while tokens:
                tok = tokens.pop(0)
                if tok[0] == Token.ROUNDBRACKETLEFT:
                    elseTok.append(tok)
                    elseTok.extend(getRoundsToClose(tokens, True))
                elif tok[0] == Token.CURLYBRACELEFT:
                    elseTok.append(tok)
                    elseTok.extend(getCurliesToClose((tokens, True)))
                else:
                    elseTok.append(tok)
            if not elseFound:
                print("else expected after if")
                exit(Error.PAR_EXPECTED)
            debracketRound(tokExpr)
            expr = expression(tokExpr)
            thenSt = thenStatement(thenTok)
            elseSt = thenStatement(elseTok)
            return ifElseNode(expr, thenSt, elseSt)          
    elif tok[0] == Token.WHILE:
        tok = tokens.pop(0)
        if tok[0] != Token.ROUNDBRACKETLEFT:
            print("( expected after if")
            exit(Error.PAR_EXPECTED)
        else:
            tokExpr = []
            tokExpr.append(tok)
            tokExpr.extend(getRoundsToClose(tokens, True))
            debracketRound(tokExpr)
            expr = expression(tokExpr)
            thenStm = thenStatement(tokens)
            return whileNode(expr, thenStm)
    elif tok[0] == Token.FOR:
        tok = tokens.pop(0)
        if tok[0] != Token.ROUNDBRACKETLEFT:
            print("( expected after for")
            exit(Error.PAR_EXPECTED)
        else:
            args = []
            args.append(tok)
            args.extend(getRoundsToClose(tokens, True))
            debracketRound(args)
            depth = 0;
            arg1 = []
            while(args):
                tok = args.pop(0)
                if tok[0] == Token.ROUNDBRACKETLEFT:
                    depth += 1
                elif tok[0] == Token.ROUNDBRACKETRIGHT:
                    depth -= 1
                if depth == 0:
                    if tok[0] == Token.SEMICOLON:
                        break;
                    else:
                        arg1.append(tok)
                else:
                    arg1.append(tok)
            if not args:
                print("; expected")
                exit(Error.PAR_EXPECTED)
            arg2 = []
            while(args):
                tok = args.pop(0)
                if tok[0] == Token.ROUNDBRACKETLEFT:
                    depth += 1
                elif tok[0] == Token.ROUNDBRACKETRIGHT:
                    depth -= 1
                if depth == 0:
                    if tok[0] == Token.SEMICOLON:
                        break;
                    else:
                        arg2.append(tok)
                else:
                    arg2.append(tok)
            if not args:
                print("; expected")
                exit(Error.PAR_EXPECTED)
            arg3 = []
            while(args):
                tok = args.pop(0)
                if tok[0] == Token.ROUNDBRACKETLEFT:
                    depth += 1
                elif tok[0] == Token.ROUNDBRACKETRIGHT:
                    depth -= 1
                if depth == 0:
                    if tok[0] == Token.SEMICOLON:
                        break;
                    else:
                        arg3.append(tok)
                else:
                    arg3.append(tok)
            if args:
                print("Extra characters in for arguments:")
                exit(Error.PAR_INVALID_OP)
            stm = thenStatement(tokens)
            arg1 = argument(arg1)
            arg2 = argument(arg2)
            arg3 = argument(arg3)
            node = forNode(arg1, arg2, arg3, stm)
    else:
        tokens.insert(0, tok)
    return normalStatement(tokens)

#<statement>
def statement(tokens):
    if not tokens:
        return None
    tok = tokens.pop(0)
    if tok[0] == Token.TYPE: #Kintamojo deklaravimas
      varTokens = []
      varTokens.append(tok)
      if not tokens:
          print("Id expected after type")
          exit(Error.PAR_EXPECTED)
      tok = tokens.pop(0)
      if tok[0] == Token.ID:
          varTokens.append(tok)
          if not tokens:
              print("; expected")
              exit(Error.PAR_EXPECTED)
          tok = tokens.pop(0)
          if tok[0] == Token.SEMICOLON:
              return variableDeclarationEmptyNode(varTokens[0], varTokens[1])
          elif tok[0] == Token.EQUALS:
              exprTokens = []
              while tokens:
                  tok = tokens.pop(0)
                  if tok[0] == Token.ROUNDBRACKETLEFT:
                      exprTokens.append(tok)
                      exprTokens.extend(getRoundsToClose(tokens, True))
                  elif tok[0] == Token.SEMICOLON:
                      expr = opIf(exprTokens)
                      return variableDeclarationNode(varTokens[0], varTokens[1], expr)
                  else:
                      exprTokens.append(tok)
              else:
                  print("; expected after variable declaration")
                  exit(Error.PAR_EXPECTED)
      else:
          print("Id expected after type")
          exit(Error.PAR_EXPECTED)
    elif tok[0] == Token.IF:
        tok = tokens.pop(0)
        if tok[0] != Token.ROUNDBRACKETLEFT:
            print("( expected after if")
            exit(Error.PAR_EXPECTED)
        else:
            tokExpr = []
            tokExpr.append(tok)
            tokExpr.extend(getRoundsToClose(tokens, True))
            thenTok = []
            elseTok = []
            depth = 0
            elseFound = False
            while tokens and not elseFound:
                tok = tokens.pop(0)
                if tok[0] == Token.ROUNDBRACKETLEFT:
                    thenTok.append(tok)
                    thenTok.extend(getRoundsToClose(tokens, True))
                elif tok[0] == Token.CURLYBRACELEFT:
                    thenTok.append(tok)
                    thenTok.extend(getCurliesToClose(tokens, True))
                elif tok[0] == Token.ELSE:
                    elseFound = True
                else:
                    thenTok.append(tok)
            if not elseFound:
                debracketRound(tokExpr)
                expr = expression(tokExpr)
                thenSt = thenStatement(thenTok)
                return ifNode(expr, thenSt)                
            debracketRound(tokExpr)
            expr = expression(tokExpr)
            thenSt = thenStatement(thenTok)
            elseSt = statement(tokens)
            return ifElseNode(expr, thenSt, elseSt)          
    elif tok[0] == Token.WHILE:
        tok = tokens.pop(0)
        if tok[0] != Token.ROUNDBRACKETLEFT:
            print("( expected after if")
            exit(Error.PAR_EXPECTED)
        else:
            tokExpr = []
            tokExpr.append(tok)
            tokExpr.extend(getRoundsToClose(tokens, True))
            debracketRound(tokExpr)
            expr = expression(tokExpr)
            thenStm = thenStatement(tokens)
            return whileNode(expr, thenStm)
    elif tok[0] == Token.FOR:
        tok = tokens.pop(0)
        if tok[0] != Token.ROUNDBRACKETLEFT:
            print("( expected after for")
            exit(Error.PAR_EXPECTED)
        else:
            args = []
            args.append(tok)
            args.extend(getRoundsToClose(tokens, True))
            debracketRound(args)
            depth = 0;
            arg1 = []
            while(args):
                tok = args.pop(0)
                if tok[0] == Token.ROUNDBRACKETLEFT:
                    depth += 1
                elif tok[0] == Token.ROUNDBRACKETRIGHT:
                    depth -= 1
                if depth == 0:
                    if tok[0] == Token.SEMICOLON:
                        break;
                    else:
                        arg1.append(tok)
                else:
                    arg1.append(tok)
            if not args:
                print("; expected")
                exit(Error.PAR_EXPECTED)
            arg2 = []
            while(args):
                tok = args.pop(0)
                if tok[0] == Token.ROUNDBRACKETLEFT:
                    depth += 1
                elif tok[0] == Token.ROUNDBRACKETRIGHT:
                    depth -= 1
                if depth == 0:
                    if tok[0] == Token.SEMICOLON:
                        break;
                    else:
                        arg2.append(tok)
                else:
                    arg2.append(tok)
            if not args:
                print("; expected")
                exit(Error.PAR_EXPECTED)
            arg3 = []
            while(args):
                tok = args.pop(0)
                if tok[0] == Token.ROUNDBRACKETLEFT:
                    depth += 1
                elif tok[0] == Token.ROUNDBRACKETRIGHT:
                    depth -= 1
                if depth == 0:
                    if tok[0] == Token.SEMICOLON:
                        break;
                    else:
                        arg3.append(tok)
                else:
                    arg3.append(tok)
            if args:
                print("Extra characters in for arguments:")
                exit(Error.PAR_INVALID_OP)
            stm = thenStatement(tokens)
            arg1 = argument(arg1)
            arg2 = argument(arg2)
            arg3 = argument(arg3)
            node = forNode(arg1, arg2, arg3, stm)
            return node
    else:
        tokens.insert(0, tok)
    return normalStatement(tokens)

#<statementList>
def statementList(tokens):
    statements = []
    while tokens:
        statements.append(statement(tokens))
    return statements

#<params>
def params(tokens):
    if len(tokens) < 2:
        print("Parameters expected!")
        exit(Error.PAR_EXPECTED)
    prms = [];
    while(tokens):
        typ = tokens.pop(0)
        i = tokens.pop(0)
        prms.append([typ, i])
        if tokens:
            if not tokens.pop(0)[0] == Token.COMMA:
                print(", expected!")
                exit(Error.PAR_EXPECTED)
    return prms

#<declaration>
def declaration(tokens):
    if not tokens:
        return None
    tok = tokens.pop(0)
    if tok[0] == Token.TYPE:
      varTokens = []
      varTokens.append(tok)
      if not tokens:
          print("Id expected after type")
          exit(Error.PAR_EXPECTED)
      tok = tokens.pop(0)
      if tok[0] == Token.ID:
          varTokens.append(tok)
          if not tokens:
              print("; expected")
              exit(Error.PAR_EXPECTED)
          tok = tokens.pop(0)
          if tok[0] == Token.ROUNDBRACKETLEFT: #rasta funkcija
              paramTokens = []
              paramTokens.append(tok)
              paramTokens.extend(getRoundsToClose(tokens, True))
              debracketRound(paramTokens)
              stmTokens = [tokens.pop(0)]
              if stmTokens[0][0] == Token.CURLYBRACELEFT: #Funkcijos deklaracija
                stmTokens.extend(getCurliesToClose(tokens, True))
                stmTokens.pop(0)
                stmTokens.pop()
                statements = statementList(stmTokens)
                block = blockNode(statements)
                if paramTokens:
                    return functionDeclarationNode(varTokens, block, params(paramTokens)) 
                return functionDeclarationNode(varTokens, block) 
              elif stmTokens[0][0] == Token.SEMICOLON: #Funkcijos prototipas
                  return functionPrototypeNode(varTokens, params(paramTokens))
          if tok[0] == Token.SEMICOLON: #rastas kintamasis
              return variableDeclarationEmptyNode(varTokens[0], varTokens[1])
          elif tok[0] == Token.EQUALS: #rastas kintamasis
              exprTokens = []
              while tokens:
                  tok = tokens.pop(0)
                  if tok[0] == Token.ROUNDBRACKETLEFT:
                      exprTokens.append(tok)
                      exprTokens.append(getRoundsToClose(tokens))
                  elif tok[0] == Token.SEMICOLON:
                      expr = opIf(exprTokens)
                      return variableDeclarationNode(varTokens[0], varTokens[1], expr)
                  else:
                      exprTokens.append(tok)
              else:
                  print("; expected after variable declaration")
                  exit(Error.PAR_EXPECTED)
            
                
      else:
          print("Id expected after type")
          exit(Error.PAR_EXPECTED)
    return statementList(tokens)

def declarations(tokens):
    decs = []
    while(tokens):
        decs.append(declaration(tokens))
    return decs
    
#Parseris
def parse(tokens):
    functions.update(stdfunc.functions)
    expressions = []
    while(tokens):
        parsedTree.extend(declarations(tokens))
    for decl in parsedTree:
        decl.execute()
    functions["main"].execute([]);
