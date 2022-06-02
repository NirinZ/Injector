# %%

import math
import time
import os
from PIL import Image
from sys import byteorder

# ניתן להעביר את כל הנתונים כאן למספרים במקום סטרינגים כדי להגדיל מהירות באופן דרמטי
# שינוי מינימלי בביטים האחרונים של הקובץ

class Extractor:

    supported_colors = len('RGB')

    bit_num = 2

    temp_pixel = ""
    buffer = ""

    column = 0
    row = 0

    image_name = ""
    file_name = ""
    file_size = 0
    current_pixel = 0
    last_pixel = 0

    def __init__(self, image_name, file_name):
        self.image_name = image_name
        self.file_name = file_name
        start_time = time.time()
        self.img = Image.open(image_name)
        self.file = open(file_name, "wb")
        self.pixels = self.img.load() # creates the pixel map

        self.bit_num = self.get_bit_num()
        self.last_pixel = self.get_last_pixel()
        self.header_len = 1 + self.get_size_block()
        self.write_to_image()
        self.file.close()
        end_time = time.time()
        total_time = end_time - start_time
        print()
        print("Time: ", total_time)

    # @staticmethod
    # def bitstring_to_bytes(s): #צריך ללמוד פעולות ביטים ולהבין איך זה עובד
    #     v = int(s, 2)
    #     b = bytearray()
    #     while v:
    #         b.append(v & 0xff)
    #         v >>= 8
    #     return bytes(b) # Im using litte so I dont need b[::-1] // from sys import byteorder \n print(byteorder)
    
    @staticmethod
    def bitstring_to_bytes(s):
        return int(s, 2).to_bytes(len(s) // 8, byteorder = "big") #byteorder) # Will throw an error if s is not devidable by 8

    @staticmethod
    def full_byte(bina, bit_num=8):
        return (bit_num - len(bina)) * "0" + bina


    def get_bit_num(self, default_bit_num: int = 1) -> int:
        buffer = ''
        for color in self.pixels[0,0]:
            byte = self.full_byte(bin(color)[2:], default_bit_num)[-default_bit_num:]
            buffer += byte
        self.current_pixel += 1
        return int(buffer, 2) + 1

    def get_size_block(self) -> int:
        max_size = self.img.size[0] * self.img.size[1]
        bina = bin(max_size)[2:]
        needed_pixels = math.ceil(len(bina)/(self.bit_num * self.supported_colors))
        return needed_pixels

    def get_last_pixel(self) -> int:
        buffer = ''
        for i in range(self.get_size_block()):
            for color in self.pixels[i+1, 0]: # +1 For the bit_num pixel
                byte = self.full_byte(bin(color)[2:], self.bit_num)[-self.bit_num:]
                buffer += byte
            self.current_pixel += 1
        return int(buffer, 2)

    def write_to_image(self):
        print(f"Bit_num =", self.bit_num)
        print(f'Last pixel =', self.last_pixel)
        for i in range(self.img.size[1]):   #for each row
            for j in range(self.img.size[0]):  #for each column
                if self.header_len > 0:
                    self.header_len -= 1
                    continue
                for color in self.pixels[j,i]: # color RGB
                    byte = self.full_byte(bin(color)[2:], self.bit_num)[-self.bit_num:] # I care just about the bit_num, so I'm not compliting the entire byte.
                    # print(byte)
                    self.buffer += byte
                # self.file.write(self.bitstring_to_bytes('0110100001101001'))
                if self.current_pixel >= self.last_pixel:
                    self.file.write(self.bitstring_to_bytes(self.buffer[ :len(self.buffer) -(len(self.buffer)%8)]))
                    return
                self.current_pixel += 1
            # print(self.buffer)
            self.file.write(self.bitstring_to_bytes(self.buffer[ :len(self.buffer) -(len(self.buffer)%8)]))
            self.buffer = self.buffer[len(self.buffer) -(len(self.buffer)%8):]
            print(f'{100 * self.current_pixel/ self.last_pixel:.1f}',"%", end="            \r")

if __name__ == "__main__":
    image_name = input("Name of the image: ")
    # image_name = "goku.png"
    
    Ext = Extractor(image_name, "OutFile")
