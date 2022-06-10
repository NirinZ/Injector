import os
import sys
from Layer2.one_byte import enc, dec
from Layer3.filepart import Decoder, Encoder
from Layer5.Image import Injector, Extractor
from Layer6 import CalcSpace

# src_path = os.path.dirname(os.path.dirname(__file__))
# sys.path.append(os.path.join(src_path, "Layer 2\\Enc\\1byte"))
# sys.path.append(os.path.join(src_path, "Layer 3\\.filepart"))
# sys.path.append(os.path.join(src_path, "Layer 5\\Main"))

#################################################################
# Modifay all the classes so I could pass them a BufferedReader #
#################################################################

def file_input_loop(string: str="") -> str:
    file = os.path.abspath(input(string))
    while not os.path.exists(file):
      print('File %s does not exist' % file)
      file = os.path.abspath(input(string))
    return file

def last(dir_path: str) -> str:

    print("\n################")
    print("#     Last!    #")
    print("################\n")
    
    print("\n################")
    print("#    Layer 3   #")
    print("################\n")
    
    decoder = Decoder.Decoder(dir_path)

    if not decoder.is_last:
        print("Done, the file isn't completed yet...\n")
        print(decoder.file)
        exit(0)

    print("\n################")
    print("#    Layer 2   #")
    print("################\n")

    password = input("Enter the password to the file: ")
    file = dec.decryption(decoder.file, password)
    return file


if __name__ == "__main__":
    print('\n' + os.getcwd())
    print(last(file_input_loop("Enter the dir path: ")))
