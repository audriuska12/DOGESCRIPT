import string
import re
import enums
from enum import Enum
from decimal import Decimal

#Reikalingi enumai:
Token = enums.Token
Type = enums.Type
Error = enums.Error

#Lekseris

#Metodai id ir skaičių atpažinimui
keywords = ["for", "if", "else", "while", "do", "return"]
idpattern = re.compile("^[_a-zA-Z][_a-zA-Z0-9]*$")
intpattern = re.compile("^[+-]?[0-9]+$")
decpattern1 = re.compile("^([+-]?[0-9]+\.[0-9]*)$")
decpattern2 = re.compile("^([+-]?[0-9]*\.[0-9]*)$")
decpattern3 = re.compile("^([+-]?[0-9]+d)$")


def isId(string):
    return idpattern.match(string) is not None

def isInt(string):
    return intpattern.match(string) is not None

def isDec(string):
    return decpattern1.match(string) is not None or decpattern2.match(string) is not None or decpattern3.match(string) is not None

def isNumeric(string):
    return isInt(string) or isDec(string)

#Leksinė analizė

#Lekserio būsenos
class State(Enum):
    DEFAULT = 0          #Įprastinė būsena
    READING_STRING = 1   #Vykdomas eilutės nuskaitymas
    ESCAPE_CHARACTER = 2 #Spec. simbolių skaitymas
    OPERATOR = 3         #Operatorių nuskaitymas
    COMMENT = 4

#Išgaunama žetono reikšmė
def terminateToken(token, tokens):
    if token == "return":
        tokens.append((Token.RETURN,))
        token = ""
    elif isId(token):
        tokens.append((Token.ID, token))
        token = ""
    elif isInt(token):
        tokens.append((Token.LIT, Type.INT, int(token)))
        token = ""
    elif isDec(token):
        tokens.append((Token.LIT, Type.DEC, Decimal(token.replace("d",""))))
        token = ""


#Pagrindinis lekserio metodas 
def lex(data):
    tokens = []
    token = ""
    state = State.DEFAULT
    for char in data:
        if state == State.DEFAULT: #Standartinis režimas
            if token == "\"": #Aptiktas string'as
                state = State.READING_STRING
                token = char
                continue
            if char == "\"":
                state = State.READING_STRING
                continue
            if token + char == "/*": #Aptiktas komentaras
                token += char
                state = State.COMMENT
            else:
                if char == "{":
                    terminateToken(token, tokens)
                    tokens.append((Token.CURLYBRACELEFT,))
                    token = ""
                elif char == "}":
                    terminateToken(token, tokens)
                    tokens.append((Token.CURLYBRACERIGHT,))
                    token = ""
                elif char == "(":
                    terminateToken(token, tokens)
                    token = ""
                    tokens.append((Token.ROUNDBRACKETLEFT,))
                elif char == ")":
                    terminateToken(token, tokens)
                    token = ""
                    tokens.append((Token.ROUNDBRACKETRIGHT,))
                elif char == "[":
                    terminateToken(token, tokens)
                    token = ""
                    tokens.append((Token.SQUAREBRACKETLEFT,))
                elif char == "]":
                    terminateToken(token, tokens)
                    token = ""
                    tokens.append((Token.SQUAREBRACKETRIGHT,))
                elif char == ";":
                    terminateToken(token, tokens)
                    token = ""
                    tokens.append((Token.SEMICOLON,))
                elif char == ",":
                    terminateToken(token, tokens)
                    token = ""
                    tokens.append((Token.COMMA,))
                elif char == "?":
                    terminateToken(token, tokens)
                    token = ""
                    tokens.append((Token.QMARK,))
                elif char == ":":
                    terminateToken(token, tokens)
                    token = ""
                    tokens.append((Token.COLON,))
                elif char == "|":
                    terminateToken(token, tokens)
                    token = ""
                    tokens.append((Token.OR,))
                elif char == "^":
                    terminateToken(token, tokens)
                    token = ""
                    tokens.append((Token.XOR,))
                elif char == "&":
                    terminateToken(token, tokens)
                    token = ""
                    tokens.append((Token.AND,))
                elif char == "%":
                    terminateToken(token, tokens)
                    token = ""
                    tokens.append((Token.MOD,))
                elif char == ".":
                    if isInt(token):
                        token += char;
                    else:
                        terminateToken(token, tokens)
                        token = ""
                        tokens.append((Token.DOT,))
                elif char in "+-*/=<>!":
                    terminateToken(token, tokens)
                    token = char
                    state = State.OPERATOR
                else:
                    if not str.isspace(char):
                        token += char
                    if token == "for":
                        tokens.append((Token.FOR,))
                        token = ""
                    elif token == "if":
                        tokens.append((Token.IF,))
                        token = ""
                    elif token == "else":
                        tokens.append((Token.ELSE,))
                        token = ""
                    elif token == "while":
                        tokens.append((Token.WHILE,))
                        token = ""
                    elif token == "do":
                        tokens.append((Token.DO,))
                        token = ""
                    elif token == "return":
                        tokens.append((Token.RETURN,))
                        token = ""
                    elif token == "int":
                        tokens.append((Token.TYPE, Type.INT))
                        token = ""
                    elif token == "dec":
                        tokens.append((Token.TYPE, Type.DEC))
                        token = ""
                    elif token == "string":
                        tokens.append((Token.TYPE, Type.STR))
                        token = ""
                    elif token == "<EOF>":
                        tokens.append((Token.EOF,))
                        token = ""
                    elif isId(token) and not isId(token + char):
                        tokens.append((Token.ID, token))
                        token = ""
                    elif isInt(token) and (not isNumeric(token + char) or str.isspace(char)):
                        tokens.append((Token.LIT, Type.INT, int(token)))
                        token = ""
                    elif isDec(token) and (not isNumeric(token + char) or str.isspace(char)):
                        tokens.append((Token.LIT, Type.DEC, Decimal(token.replace("d",""))))
                        token = ""
                    else:
                        if token == "!=":
                            tokens.append((Token.NEQ,))
                            token = ""
                        elif token == "!":
                            tokens.append((Token.NEG,))
                            token = ""
                        elif token == "++":
                            tokens.append((Token.DOUBLEP,))
                            token = ""
                        elif token == "--":
                            tokens.append((Token.DOUBLEM,))
                            token = ""
        elif state == State.OPERATOR: #APtiktas operatorius
            if not str.isspace(char):
                if token == "+":
                    if char == "+":
                        tokens.append((Token.DOUBLEP,))
                        token = ""
                        state = State.DEFAULT
                    else:
                        tokens.append((Token.PLUS,))
                        token = char;
                        state = State.DEFAULT
                elif token == "-":
                    if char == "-":
                        tokens.append((Token.DOUBLEM,))
                        token = ""
                        state = State.DEFAULT
                    else:
                        tokens.append((Token.MINUS,))
                        token = char;
                        state = State.DEFAULT
                elif token == "*":
                    if char == "*":
                        tokens.append((Token.EXP,))
                        token = ""
                        state = State.DEFAULT
                    else:
                        tokens.append((Token.MUL,))
                        token = char;
                        state = State.DEFAULT
                elif token == "/":
                    if char == "*":
                        token += char
                        state = State.COMMENT
                    else:
                        tokens.append((Token.DIV,))
                        token = char;
                        state = State.DEFAULT
                elif token == "=":
                    if char == "=":
                        tokens.append((Token.EQEQ,))
                        token = ""
                        state = State.DEFAULT
                    else:
                        tokens.append((Token.EQUALS,))
                        token = char;
                        state = State.DEFAULT
                elif token == "<":
                    if char == "=":
                        token += char
                    elif char == ">":
                        tokens.append((Token.LTGT,))
                        token = ""
                        state = State.DEFAULT
                    elif char == "E":
                        token += char
                    else:
                        tokens.append((Token.LT,))
                        token = char;
                        state = State.DEFAULT
                elif token == "<=":
                    if char == ">":
                        tokens.append((Token.SWAP,))
                        token = ""
                        state = State.DEFAULT
                    else:
                        tokens.append((Token.LTEQ,))
                        token = char
                        state = State.DEFAULT
                elif token == "<E":
                    if char == "O":
                        token += (char)
                    else:
                        tokens.append((Token.LT,))
                        token = token[1:] + char
                        state = State.DEFAULT
                elif token == "<EO":
                    if char == "F":
                        token += char
                    else:
                        tokens.append((Token.LT,))
                        token = token[1:] + char
                        state = State.DEFAULT
                elif token == "<EOF":
                    if char == ">":
                        tokens.append((Token.EOF,))
                        token = ""
                        state = State.DEFAULT
                    else:
                        token += char
                        state = State.DEFAULT
                elif token == ">":
                    if char == "=":
                        tokens.append((Token.GTEQ,))
                        token = ""
                        state = State.DEFAULT
                    else:
                        tokens.append((Token.GT,))
                        token = char
                        state = State.DEFAULT
                elif token == "!":
                    if char == "=":
                        tokens.append((Token.NEQ,))
                        token = ""
                        state = State.DEFAULT
                    else:
                        tokens.append((Token.NEG,))
                        token = char
                        state = State.DEFAULT
                else:
                    print("Unknown operator: " + token)
                    System.exit(Error.LEX_UNKNOWN_OP)
                if token == "(":
                    tokens.append((Token.ROUNDBRACKETLEFT,))
                    token = ""
                elif token == ")":
                    tokens.append((Token.ROUNDBRACKETRIGHT,))
                    token = ""
                elif token == "[":
                    tokens.append((Token.SQUAREBRACKETLEFT,))
                    token = ""
                elif token == "]":
                    tokens.append((Token.SQUAREBRACKETRIGHT,))
                    token = ""
                elif token == "{":
                    tokens.append((Token.CURLYBRACELEFT,))
                    token = ""
                elif token == "}":
                    tokens.append((Token.CURLYBRACERIGHT,))
                    token = ""
            
        elif state == State.READING_STRING or state == State.ESCAPE_CHARACTER: #Skaitoma eilutė
            if state != State.ESCAPE_CHARACTER and char == "\"":
                state = State.DEFAULT
                tokens.append((Token.LIT, Type.STR, token))
                token = ""
            elif state !=State.ESCAPE_CHARACTER and char == "\\": #Aptiktas simbolio escape'inimas
                state = State.ESCAPE_CHARACTER
            else:
                token += char
                if state == State.ESCAPE_CHARACTER:
                    state = State.READING_STRING
        elif state == State.COMMENT:
            token = token[1] + char
            if token == "*/":
                token = ""
                state = State.DEFAULT
    tokens.pop() #Paskutinis žetonas turėtų būti <EOF> - jį galim išmesti
    return tokens
