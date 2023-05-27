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
    while not os.path.isfile(file):
      print('File %s does not exist' % file)
      file = os.path.abspath(input(string))
    return file

# Returns the abs path
def path_input_loop(string: str="") -> list[str]:
    file = os.path.abspath(input(string))
    while not os.path.exists(file) or len(os.listdir(file)) == 0:
      print('Path %s does not exist or empty' % file)
      file = os.path.abspath(input(string))
    return file


if __name__ == "__main__":
    print(os.getcwd())
    
    way = input("Choose the way to inject:\n1) Auto\n2) One by one\nEnter ther number: ")

    bit_num = int(input("Enter the bit_num: "))
    file = path_input_loop("Enter the file or path of the files to inject: ")
    multi_files: bool = os.path.isdir(file)
    defaults = False if input("Use the default settings? (Y/N) ").upper() == 'N' else True
    img_multiplier: float = Jojo_in.get_img_multilayer(False)

    if way.lower() == '1' or way.lower() == "auto":

        images_path = file_input_loop("Enter the path to the images: ")
        total_size = 0

        for i in os.listdir(images_path):
            total_size += Injector.Injector.calculate_space(os.path.join(images_path, i), bit_num, img_multiplier)
        print("Total size:", total_size)
        
        if multi_files:
            files_dir = file
            files = []
            for i in os.listdir(file):
                p = os.path.join(file, i)
                if os.path.isfile(p):
                    files.append(p)
            if len(files) == 0:
                raise "There are no files in this folder, subfolders does'nt count."
            file = files[0]

            file_size = os.path.getsize(file)

            for img in os.listdir(images_path):
                img_size = Injector.Injector.calculate_space(os.path.join(images_path, i), bit_num, img_multiplier)

                if img_size > file_size:
                    pass

                dir_path = os.path.dirname(Jojo_in._ins(os.path.join(images_path, img), bit_num, file, defaults, img_multiplier))

                # Not [If in there is a '.filepart' in the folder => The file still havent been fully injected] ==> The file HAS been fully injected
                if not True in [os.path.splitext(f)[1] == '.filepart' for f in os.listdir(dir_path)]:
                    files.pop(0)
                    if len(files) == 0:
                        break
                    else:
                        file = files[0]

                    
                for f in os.listdir(dir_path):
                    if os.path.splitext(f)[1] == '.filepart':
                        file = os.path.join(dir_path, f)
                        print("Size left: ", os.path.getsize(file))
            if len(files) != 0:
                print("The path of the last filepart is:", file)
        
        else:
            file_size = os.path.getsize(file)
            if file_size > total_size:
                print("There is not enough space in the images... So the file will be partially injected.")
                if input("Is it OK? (y/n): ") != 'y':
                    exit(1)

            for img in os.listdir(images_path):
                dir_path = os.path.dirname(Jojo_in._in(os.path.join(images_path, img), bit_num, file, defaults, img_multiplier))

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
            if input("Do you have more images? (y/n):") != 'y':
                break
            img = file_input_loop("Enter an image: ")
            defaults = False if input("Use the default settings? (Y/N)") == 'N' else True
            dir_path = os.path.dirname(Jojo_in._in(img, bit_num, file, defaults))

    print("Done!!!")

