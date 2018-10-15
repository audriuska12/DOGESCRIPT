from sys import *
#hannibal - lekseris
import hannibal
#peter - parseris
import peter

#Išsaugojam nuorodas, kad būtų lengviau rašyti
Token = hannibal.Token
Type = hannibal.Type

#nuskaitomas failo turinys
def read_file(filename):
    try:
        file = open(filename, 'r')
        data = file.read()
        data += "<EOF>" #pridedamas, kad lekseris žinotų apie failo pabaigą
        return data
    except FileNotFoundError as e:
        print("File " + filename + " was not found!")
        exit(2)
                  
def run():
    #nuskaitomas parametru nurodytas failas
    try:
        data = read_file(argv[1])
    except IndexError as e:
        print("Usage: python dogescript.py <file name>")
        exit(1)
    #iš failo išgaunami žetonai
    tokens = hannibal.lex(data)
    #kuriamas ir vykdomas medis
    peter.parse(tokens)

run()
