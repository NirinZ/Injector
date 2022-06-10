import os
import Jojo_in
from Layer3.filepart import Encoder
from Layer5.Image import Injector

# src_path = os.path.dirname(os.path.dirname(__file__))
# sys.path.append(os.path.join(src_path, "Layer 2\\Enc\\1byte"))
# sys.path.append(os.path.join(src_path, "Layer 3\\.filepart"))
# sys.path.append(os.path.join(src_path, "Layer 5\\Main"))

#################################################################
# Modifay all the classes so I could pass them a BufferedReader #
#################################################################

# Returns the abs path
def file_input_loop(string: str="") -> str:
    file = os.path.abspath(input(string))
    while not os.path.exists(file):
      print('File %s does not exist' % file)
      file = os.path.abspath(input(string))
    return file

if __name__ == "__main__":
    print(os.getcwd())
    
    way = input("Choose the way to inject:\n1) Auto\n2) One by one\nEnter ther number: ")

    bit_num = int(input("Enter the bit_num: "))
    file = file_input_loop("Enter the file to inject: ")
    defaults = False if input("Use the default settings? (Y/N) ").upper() == 'N' else True
    img_multiplier = Jojo_in.get_img_multilayer(defaults)

    if way.lower() == '1' or way.lower() == "auto":
        images_path = file_input_loop("Enter the path to the images: ")
        file_size = os.path.getsize(file)
        total_size = 0

        for i in os.listdir(images_path):
            total_size += Injector.Injector.calculate_space(os.path.join(images_path, i), bit_num, img_multiplier)

        if file_size > total_size:
            input("There is not enough space in the images... Please add more images.")
            exit(1)

        for img in os.listdir(images_path):
            dir_path = os.path.dirname(Jojo_in._in(os.path.join(images_path, img), bit_num, file, defaults))

            # If in there is a '.filepart' in the folder => The file still havent been fully injected
            if not True in [os.path.splitext(f)[1] == '.filepart' for f in os.listdir(dir_path)]:
                break
                
            for f in os.listdir(dir_path):
                if os.path.splitext(f)[1] == '.filepart':
                    file = os.path.join(dir_path, f)
                    print("Size left: ", os.path.getsize(file))


    
    else:
        img = file_input_loop("Enter an image: ")
        dir_path = os.path.dirname(Jojo_in._in(img, bit_num, file, defaults))

        # While in there is a '.filepart' in the folder => The file still havent been fully injected
        while True in [os.path.splitext(f)[1] == '.filepart' for f in os.listdir(dir_path)]:
            for f in os.listdir(dir_path):
                if os.path.splitext(f)[1] == '.filepart':
                    file = os.path.join(dir_path, f)
                    print("Size left: ", os.path.getsize(file))
            img = file_input_loop("Enter an image: ")
            defaults = False if input("Use the default settings? (Y/N)") == 'N' else True
            dir_path = os.path.dirname(Jojo_in._in(img, bit_num, file, defaults))

    print("Done!!!")

