import random as rd
from os.path import splitext

def enc(file, offset):
  nf = open(splitext(file)[0] + '.enc', 'wb')
  with open(file, 'rb') as of:
    for i in of.read():
      i+=offset
      if i > 255:
        i -= 256
      t = i.to_bytes(1, 'little')
      nf.write(t)
  nf.close()

def pass_to_offset(pas):
  rd.seed(pas)
  return rd.randrange(256)

if __name__ == '__main__':
  file = input("The File: ")
  pas = input("Password: ")
  enc(file, pass_to_offset(pas))
  print("Done!")