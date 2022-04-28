import random as rd
from os.path import splitext

def dec(file, extention, offset):
  nf = open(splitext(file)[0] + f' - out.{extention}', 'wb')
  with open(file, 'rb') as of:
    for i in of.read():
      i -= offset
      if i < 0:
        i += 256
      t = i.to_bytes(1, 'little')
      nf.write(t)
  nf.close()

def pass_to_offset(pas):
  rd.seed(pas)
  return rd.randrange(256)

if __name__ == '__main__':
  file = input("The File: ")
  extantion = input("File extantion: ")
  pas = input("Password: ")
  dec(file, extantion, pass_to_offset(pas))
  print("Done!")