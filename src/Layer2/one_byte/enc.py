import io
import random as rd
from os.path import exists
from os.path import getsize
from os.path import basename

def enc(file: str, offset, close: bool = True) -> str or io.BufferedRandom:
  if not exists(file):
      raise Exception('File %s does not exist' % file)

  nf = open(basename(file) + '.enc', 'wb+')
  size = getsize(file)
  num = 0

  with open(file, 'rb') as of:
    for i in of.read():
      i+=offset
      if i > 255:
        i -= 256
      t = i.to_bytes(1, 'little')
      nf.write(t)
      num += 1
      if num % 100 == 0:
        print("Encrypting the file... ", f'{100 * num/size:.1f}',"%", end='           \r')
    print()
  
  if close:
    nf.close()
    return nf.name
  else:
    nf.seek(0)
    return nf

def pass_to_offset(pas):
  rd.seed(pas)
  return rd.randrange(256)

def encrypte(file: str, password: str, close: bool = True) -> str or io.BufferedRandom:
  return enc(file, pass_to_offset(password), close)

if __name__ == '__main__':
  file = input("The File: ")
  pas = input("Password: ")
  encrypte(file, pas)
  print("Done!")