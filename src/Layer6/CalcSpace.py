if __name__ == "__main__":
    print("Welcome to CalcSpace!")
    print("With this you can calculate the size we can use in an image.")
    print("===================================================")
    print("There are 3 ways to use this program:")
    print("1) Enter the number of the image pixels. -> 2800745")
    print("2) Enter the image ratio. -> 1080, 1920")
    print("3) Enter the image path. -> path\\to\\the\\image.png (You need to have PIL to use this option)")
    print("===================================================")
    print("The bit_num is effecting the size we can use:")
    print("Low bit_num is hard to detect but can store less data,\nwhereas high bit_num can store more data but easier to detect.\n")


#----------------------------------------------------------------

import os
import sys
import numpy as np
from PIL import Image
import math


def calculate_space_img(image_name, bit_num, supported_colors: int = 3):
    img = np.array(Image.open(image_name))
    max_size =  img.shape[0] * img.shape[1]
    multiplier = math.ceil(len(bin(max_size)[2:])/(bit_num * supported_colors))
    return int(img.size * bit_num / 8)  - supported_colors - multiplier # For bit_num pixel (RGB/ RGBA)

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
    print('----------------------------')
    for i in range(1, 9):
        print(f"For {i} bit_num the max is:", sizeof_fmt(func(param, i)))
    print('----------------------------')

def is_xy(txt):
    txt = txt.replace(' ', '')
    if 'x' in txt.lower():
        sp = txt.lower().split('x')
    else:
        sp = txt.split(',')
    if (len(sp) == 2 and sp[0].isnumeric() and sp[1].isnumeric()):
        return int(sp[0]) * int(sp[1])
    else:
        return False

if __name__ == "__main__":
    while 1:
        try:
            inp = input("Enter the image path or the image size: ")
            if (inp.isnumeric()):
                print_all_bit_num(calculate_space_size, int(inp))
            elif (is_xy(inp)):
                print_all_bit_num(calculate_space_size, is_xy(inp))
            # ------------------------------------------------------
            elif (os.path.exists(inp)):
                print_all_bit_num(calculate_space_img, inp)
            # ------------------------------------------------------
            elif (inp == 'ex'):
                exit()
            else:
                print("Illigal input!")
        except Exception as e:
            print("Error: " + str(e))
