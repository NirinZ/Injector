import numpy as np
from PIL import Image
import os

def calculate_space_img(image_name, bit_num):
    img = np.array(Image.open(image_name))
    return int(img.size * bit_num / 8)

#----------------------------------------------------------------

def calculate_space_size(size, bit_num):
    return int(size * 3 * bit_num / 8)

def sizeof_fmt(num, suffix="B"):
    for unit in ["", "K", "M", "G", "T", "P", "E", "Z"]:
        if abs(num) < 1024.0:
            return f"{num:3.2f} {unit}{suffix}"
        num /= 1024.0
    return f"{num:.1f}Y{suffix}"

def print_all_bit_num(func, param):
    for i in range(1, 9):
        print(f"For {i} bit_num the max is:", sizeof_fmt(func(param, i)))

def is_xy(txt):
    txt = txt.replace(' ', '')
    sp = txt.split(',')
    if (len(sp) == 2 and sp[0].isnumeric() and sp[1].isnumeric()):
        return int(sp[0]) * int(sp[1])
    else:
        return False

if __name__ == "__main__":
    while 1:
        try:
            inp = input("Img path or size: ")
            if (inp.isnumeric()):
                print_all_bit_num(calculate_space_size, int(inp))
            elif (is_xy(inp)):
                print_all_bit_num(calculate_space_size, is_xy(inp))
            elif (os.path.exists(inp)):
                print_all_bit_num(calculate_space_img, inp)
            else:
                print("Illigal input!")
        except Exception as e:
            print("Error: " + str(e))
