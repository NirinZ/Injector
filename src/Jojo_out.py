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

def out(img:str) -> str:

    print("\n################")
    print(f"#      {img}     #")
    print("################\n")
    

    print("\n################")
    print("#    Layer 5   #")
    print("################\n")

    extractor = Extractor.Extractor(img, "img - extracted")

    print("\n################")
    print("#    Layer 4?  #")
    print("################\n")

    file = dec.decryption(extractor.file.name, extractor.bit_num, False)

    print("\n################")
    print("#    Layer 3   #")
    print("################\n")

    filepart = Encoder.Filepart.open_file(file)
    filepart.file.close()

    dir = "Out - " + filepart.group
    if os.path.splitext(dir)[1] == ".enc":
        dir = os.path.splitext(dir)[0]
    if not os.path.exists(dir):
        os.mkdir(dir)
        
    new_name = os.path.join(dir, os.path.basename(filepart.name))
    while os.path.exists(new_name):
        new_name += '1'
    os.rename(filepart.name, new_name)
    os.remove(extractor.file.name)

    return os.path.abspath(dir)

if __name__ == "__main__":
    print('\n' + os.getcwd())
    print(out(file_input_loop("Enter the image: ")))

    #print(injector.out_name)
