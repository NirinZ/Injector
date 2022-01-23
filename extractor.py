import math
import time
import os
from PIL import Image
from Injector import Injector

class Extractor:
    bit_num = 2

    temp_pixel = ""
    buffer = ""

    column = 0
    row = 0

    image_name = ""
    file_name = ""

    def __init__(self, image_name, file_name, bit_num = 2):
        self.image_name = image_name
        self.file_name = file_name
        self.bit_num = bit_num
        start_time = time.time()
        self.img = Image.open(image_name)
        self.pixels = self.img.load()
        self.img = Image.open(image_name)
        self.file = open(file_name, "wb")
        self.pixels = self.img.load() # creates the pixel map
        self.write_to_image()
        self.file.close()

    @staticmethod
    def bitstring_to_bytes(s):
        v = int(s, 2)
        b = bytearray()
        while v:
            b.append(v & 0xff)
            v >>= 8
        return bytes(b[::-1])

    def write_to_image(self):
        start_time = time.time()
        for i in range(self.img.size[0]):   #for each row
            for j in range(self.img.size[1]):  #for each column
                for color in self.pixels[i,j]: # color RGB
                    byte = Injector.full_byte(bin(color)[2:][-self.bit_num:])
                    # print(byte)
                    self.buffer += byte
                self.file.write(self.bitstring_to_bytes(self.buffer))
                self.buffer = "" # כנראה שנאבד כאן מידע שמחלקים ב8
        end_time = time.time()
        total_time = end_time - start_time
        print("Time: ", total_time)

if __name__ == "__main__":
    Extractor("save.png", "te.txt", 7)