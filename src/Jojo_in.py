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

if __name__ == "__main__":
    
    print("\n################")
    print("# Preperations #")
    print("################\n")
    
    print(os.getcwd())

    img = file_input_loop("Enter the image: ")
    print(CalcSpace.print_all_bit_num(Injector.Injector.calculate_space, img))

    bit_num = int(input("Enter the bit_num: "))
    size = Injector.Injector.calculate_space(img, bit_num)

    file = file_input_loop("Enter the file to inject: ")
    if os.path.splitext(file)[1] != ".filepart":
        if not os.path.exists("temp - "+os.path.basename(file)):
            os.mkdir("temp - "+os.path.basename(file))
        os.chdir("temp - "+os.path.basename(file))
        # Now all files will be created in the temp {file} folder
        
        password = input("Enter the password to the file: ")

        print("\n################")
        print("#    Layer 2   #")
        print("################\n")

        enc_file = enc.encrypte(file, password, False)

        print("\n################")
        print("#    Layer 3   #")
        print("################\n")

        filepart = Encoder.Filepart.create(enc_file)
        split = Encoder.Filepart.split(filepart, size)
        os.remove(enc_file.name)

    else:
        filepart = Encoder.Filepart.open(file)
        dir = filepart.group
        if os.path.splitext(dir)[1] == ".enc":
            dir = os.path.splitext(dir)[0]
        os.chdir("temp - " + dir)
        split = Encoder.Filepart.split(filepart, size)

    filepart.file.close()
    split.file.close()
    
    print("\n################")
    print("#    Layer 4?  #")
    print("################\n")

    file_name = enc.encrypte(split.name, bit_num)
    os.remove(split.name)

    print("\n################")
    print("#    Layer 5   #")
    print("################\n")

    injector = Injector.Injector(img, file_name, bit_num)
    os.remove(file_name)

    print(injector.out_name)    
