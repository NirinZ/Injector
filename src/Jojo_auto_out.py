import os
import Jojo_out
import Jojo_last

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
    
    print('\n' + os.getcwd())

    path = file_input_loop("Enter the path to all the images: ")

    for f in os.listdir(path):
        file_path = os.path.join(path, f)
        dir = Jojo_out.out(file_path)

    if len(os.listdir(path)) > 0:
        print(Jojo_last.last(dir))

    #print(injector.out_name)
