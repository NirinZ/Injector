from time import sleep
from os import system
from threading import Thread

global work1
work1 = True

global work2
work2 = True


def loading1(load_txt: str="Loading...", finish_txt:str = "Done!"):
    a = r'"\"'
    a=a[1]
    global work1
    while work1:
            print(load_txt + " |", end="\r")
            sleep(0.09)
            print(load_txt + " /", end="\r")
            sleep(0.09)
            print(load_txt + " -", end="\r")
            sleep(0.09)
            print(load_txt + " "+a, end="\r")
            sleep(0.09)
    print(finish_txt + " "*(len(load_txt)) + "           ", end="\r")
    print()

def loading2(load_txt: str="Loading...", finish_txt:str = "Done!"):
    a = r'"\"'
    a=a[1]
    spaces = ""
    for i in range(len(load_txt)):
        spaces+=" "
    global work2
    while work2:
            print(spaces + " |")
            print(load_txt + " |")
            sleep(0.09)
            system("cls")
            print(spaces + "  /")
            print(load_txt + " /")
            sleep(0.09)
            system("cls")
            print(spaces + " __")
            print(load_txt)
            sleep(0.09)
            system("cls")
            print(spaces + a)
            print(load_txt + " "+a)
            sleep(0.09)
            system("cls")
    
    print(finish_txt)

def end1():
    global work1
    work1 = False
    sleep(0.8)

def end2():
    global work2
    work2 = False
    sleep(0.8)

def T_loading1(load_txt: str="Loading...", finish_txt:str="Done!"):
    Thread(target=loading1, args=(load_txt, finish_txt)).start()

def T_loading2(load_txt: str="Loading...", finish_txt:str = "Done!"):
    Thread(target=loading2, args=(load_txt, finish_txt)).start()
    
if __name__ == '__main__':
    if(input("Num: ")=='1'):loading1('load_txt', 'finish_txt')
    else:loading2('load_txt', 'finish_txt')
