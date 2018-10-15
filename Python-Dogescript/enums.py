from enum import Enum
#enum'ų saugykla

#Žetonų rūšys (saugojimo formatas)
class Token(Enum):
    EOF = -1               #Failo pabaiga. (EOF, )
    ID = 0                 #Kintamojo pavadinimas. (ID, pavadinimas)
    LIT = 1                #Kintamojo literalas. (LIT, tipas, reikšmė)
    TYPE = 2               #Kintamojo tipas. Palaikomi int, dec, string tipai. (TYPE, Type)
    CURLYBRACELEFT = 3     #{ (CURLYBRACELEFT,)
    CURLYBRACERIGHT = 4    #} (CURLYBRACERIGHT,)
    ROUNDBRACKETLEFT = 5   #( (ROUNDBRACKETLEFT,)
    ROUNDBRACKETRIGHT = 6  #) (ROUNDBRACKETRIGHT,)
    SQUAREBRACKETLEFT = 7  #[ (SQUAREBRACKETLEFT,)
    SQUAREBRACKETRIGHT = 8 #] (SQUAREBRACKETRIGHT,)
    SEMICOLON = 9          #; (SEMICOLON,)
    EQUALS = 10            #= (EQUALS,)
    FOR = 11               #for (FOR,)
    IF = 12                #if (IF,)
    ELSE = 13              #else (ELSE,)
    WHILE = 14             #while (WHILE,)
    DO = 15                #do (DO,)
    RETURN = 16            #return (RETURN,)
    QMARK = 17             #? (QMARK,)
    SWAP = 18              #<=> (SWAP,)
    COLON = 19             #: (COLON,)
    OR = 20                #| (OR,)
    XOR = 21               #^ (XOR,)
    AND = 22               #& (AND,)
    EQEQ = 23              #== (EQEQ,)
    NEQ = 24               #!= (NEQ,)
    LT = 25                #< (LT,)
    LTEQ = 26              #<= (LTEQ,)
    GT = 27                #> (GT,)
    GTEQ = 28              #>= (GTEQ,)
    PLUS = 29              #+ (PLUS,)
    MINUS = 30             #- (MINUS,)
    MUL = 31               #* (MUL,)
    DIV = 32               #/ (DIV,)
    MOD = 33               #% (MOD,)
    EXP = 34               #** (EXP,)
    DOUBLEP = 35           #++ (DOUBLEP,)
    DOUBLEM = 36           #-- (DOUBLEM,)
    DOT = 37               #. (DOT,)
    COMMA = 38             #, (COMMA,)
    LTGT = 39              #<> (LTGT,)
    NEG = 40               #! (NEG,)

#Palaikomi tipai - loginius kintamuosius realizuosim sveikaisiais skaičiais (0 - false, ne 0 - true)
class Type(Enum):
    INT = 0 #Sveikasis skaičius
    DEC = 1 #Dešimtainis skaičius
    STR = 2 #String

#Klaidos - 0 nenaudojama,
class Error(Enum):
    WTF = -1             #Nežinomos prigimties klaida
    LEX_UNKNOWN_OP = 1   #Lekseris rado nepažįstamą operatorių.
    PAR_EXPECTED = 2     #Parseris nerado ieškomo simbolio
    PAR_UNKNOWN_TYPE = 3 #Parseris neatpažino kintamojo tipo
    PAR_UNKNOWN_VAL = 4  #Parseris nerado kintamojo
    PAR_INVALID_OP = 5   #Operatorius netinka tipui
    RET_ONE = 5          #Bandoma grąžinti ne vieną reikšmę
