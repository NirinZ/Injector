import os
import sys
from Layer2.one_byte import enc, dec
from Layer3.filepart import Encoder
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

def get_img_multilayer(defaults: bool = True) -> float:
    img_multiplier = 2

    if not defaults:
        img_multiplier = abs(float(input("Enter the image multiplier: ")))

    return img_multiplier

def get_flags(defaults: bool = True) -> Encoder.Flags:
    flags = Encoder.Flags()

    if not defaults:
        print("~ Fileparting ~")
        print("Choose the ordering version:")
        print("1) Part Num 1B")
        print("2) Part Num 3B")
        print("3) Offset 5B")
        print("4) Offset 6B X")
        ordering = input("Enter the number: ")

        if ordering == '1':
            ordering = Encoder.Ordering.PART_NUM1
        elif ordering == '2':
            ordering = Encoder.Ordering.PART_NUM3
        elif ordering == '3':
            ordering = Encoder.Ordering.OFFSET5
        elif ordering == '4':
            print("Not supported")
            ordering = flags.order_version
        else:
            print("Choosing the default")
            ordering = flags.order_version
        
        print("\nChoose the num rapping version:")
        print("1) Adding")
        print("2) UTF-8 X")
        print("3) UTF-16 X")
        print("4) UTF-Nirin X")
        num_rapping= input("Enter the number: ")
        
        if num_rapping == '1':
            num_rapping = Encoder.NumRapping.ADDING
        elif num_rapping == '2':
            print("Not supported")
            num_rapping = flags.num_rapping
        elif num_rapping == '3':
            print("Not supported")
            num_rapping = flags.num_rapping
        elif num_rapping == '4':
            print("Not supported")
            num_rapping = flags.num_rapping
        else:
            print("Choosing the default")
            num_rapping = flags.num_rapping


        print("\nChoose the checksum version:")
        print("1) No checksum")
        print("2) Checksum 4B")
        print("3) Error correction X")
        print("4) *Not set yet* X")
        checksum_type = input("Enter the number: ")

        if checksum_type == '1':
            checksum_type = Encoder.Checksum.NO_CHECKSUM
        elif checksum_type == '2':
            checksum_type = Encoder.Checksum.CHECKSUM4
        elif checksum_type == '3':
            print("Not supported")
            checksum_type = flags.checksum_type
        elif checksum_type == '4':
            print("Not supported")
            checksum_type = flags.checksum_type
        else:
            print("Choosing the default")
            checksum_type = flags.checksum_type

        flags.order_version = ordering
        flags.num_rapping = num_rapping
        flags.checksum_type = checksum_type
    
    return flags

def _in(img, bit_num, file, defaults: bool = True, img_multiplier: float = 2.0) -> str:

    print("\n################")
    print(f"# {img} #")
    print("################\n")

    # img_multiplier = get_img_multilayer(defaults)

    size = Injector.Injector.calculate_space(img, bit_num, img_multiplier)

    if os.path.splitext(file)[1] != ".filepart":
        if not os.path.exists("Images - "+os.path.basename(file)): # Here because the extension will be .filepart
            os.mkdir("Images - "+os.path.basename(file))
        os.chdir("Images - "+os.path.basename(file))
        # Now all files will be created in the temp {file} folder
        
        password = input("Enter the password to the file: ")

        print("\n################")
        print("#    Layer 2   #")
        print("################\n")

        enc_file = enc.encrypte(file, password, False)

        print("\n################")
        print("#    Layer 3   #")
        print("################\n")

        flags = get_flags(defaults)
        filepart = Encoder.Filepart.create(enc_file, flags)
        split = Encoder.Filepart.split(filepart, size)
        os.remove(enc_file.name)

    else:
        filepart = Encoder.Filepart.open(file)
        dir = filepart.group
        if os.path.splitext(dir)[1] == ".enc":
            dir = os.path.splitext(dir)[0]
        if not os.getcwd().endswith("Images - " + dir):
            if os.path.exists("Images - " + dir):
                os.chdir("Images - " + dir)
            else:
                os.chdir(os.path.dirname(file))
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

    injector = Injector.Injector(img, file_name, bit_num, img_multiplier)
    os.remove(file_name)

    return injector.out_name

if __name__ == "__main__":
    print(os.getcwd())

    img = file_input_loop("Enter the image: ")
    print(CalcSpace.print_all_bit_num(Injector.Injector.calculate_space, img))
    bit_num = int(input("Enter the bit_num: "))
    file = file_input_loop("Enter the file to inject: ")

    print(_in(img, bit_num, file))
