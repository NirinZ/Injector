import io
import random as rd
from os.path import splitext
from os.path import basename
from os.path import exists

def dec(file: str, offset, close: bool = True) -> str or io.BufferedRandom:
  if not exists(file):
      raise Exception('File %s does not exist' % file)
  
  dir = basename(file)
  if splitext(dir)[1] == ".enc":
      dir = splitext(dir)[0]
    
  nf = open(dir + ' - out', 'wb+')
  with open(file, 'rb+') as of:
    for i in of.read():
      i -= offset
      if i < 0:
        i += 256
      t = i.to_bytes(1, 'little')
      nf.write(t)

  if close:
    nf.close()
    return nf.name
  else:
    nf.seek(0)
    return nf

def pass_to_offset(pas):
  rd.seed(pas)
  return rd.randrange(256)

def decryption(file: str, password: str, close: bool = True) -> str or io.BufferedRandom:
  return dec(file, pass_to_offset(password), close)


if __name__ == '__main__':
  file = input("The File: ")
  pas = input("Password: ")
  decryption(file, pas)
  print("Done!")