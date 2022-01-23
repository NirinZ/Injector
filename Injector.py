# %%
import math
import time
import os
from PIL import Image
from matplotlib.style import available

'''
class Injector:
    def __init__(self):
        self.img = Image.open("sub.jpg")
        self.file = open("text.txt", "rb")
        #img = Image.new( 'RGB', (250,250), "black") #creating a new image
        self.pixels = self.img.load() # creates the pixel map

    @staticmethod
    def read_from_file(self):
        bin(int(t.hex(),16))[2:]

    @staticmethod
    def write_to_image(self):
        self.img.show()
        start_time = time.time()
        for i in range(self.img.size[0]):   #for each row
            for j in range(self.img.size[1]):  #for each column
                self.pixels[i,j] = (50, 80, 50)  #set color RGB
        end_time = time.time()
        total_time = end_time - start_time
        print("Time: ", total_time)
        self.img.show()

if __name__ == "__main__":
    Injector().write_to_image()
'''


# img = Image.new( 'RGB', (250,250), "black") #creating a new image

class Injector:
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

        self.file_size = os.path.getsize(image_name)
        pixels_num = self.img.size[0] * self.img.size[1]
        self.available_space = int(pixels_num * 3 * self.bit_num)

        # self.img.show()
        self.write_string("This image hed injected!")  # verefication  //24 bytes
        self.write_bin("00000000")  # version //1 byte
        self.write_bin("10101010")  # start of file //1 byte
        self.read_from_file()
        end_time = time.time()
        total_time = end_time - start_time
        print("Time: ", total_time)
        self.img.show()
        self.img.save("save.jpg")

    @staticmethod
    def full_byte(bina):
        return (8 - len(bina)) * "0" + bina

    @staticmethod
    def calculate_space(image_name, bit_num):
        img = Image.open(image_name)
        pixels_num = img.size[0] * img.size[1]
        return int(pixels_num * 3 * bit_num / 8)

    @staticmethod
    def sizeof_fmt(num, suffix="B"):
        print(num)
        for unit in ["", "K", "M", "G", "T", "P", "E", "Z"]:
            if abs(num) < 1024.0:
                return f"{num:3.2f} {unit}{suffix}"
            num /= 1024.0
        return f"{num:.1f}Y{suffix}"


    def make_pixel(self, tempicx):
        current_pixel = self.pixels[self.row, self.column]
        new_pixel = []
        for i in current_pixel:  #\/ removing the least significant bit from original pixel
            new_pixel.append(int(bin(i)[2:][:-self.bit_num] + self.temp_pixel[:self.bit_num], 2))
            # new_pixel.append(0)
            tempicx = tempicx[self.bit_num:]           # /\ adding the new pixel

        # print(new_pixel)
        self.pixels[self.row, self.column] = tuple(new_pixel)
        if self.column == self.img.size[1] - 1:
            self.column = 0
            self.row += 1
        else:
            self.column += 1

    def make_subpixels(self, data, last=False):
        for i in range(math.ceil(len(data) / self.bit_num)):
            self.temp_pixel += data[:self.bit_num]
            data = data[self.bit_num:]
            if len(self.temp_pixel) == self.bit_num * 3:
                self.make_pixel(self.temp_pixel)
                self.temp_pixel = ""
            elif len(self.temp_pixel) > self.bit_num * 3:
                self.make_pixel(self.temp_pixel[:self.bit_num * 3])
                self.temp_pixel = self.temp_pixel[self.bit_num * 3 :] 
            elif last:
                self.temp_pixel += "0" * (self.bit_num * 3 - len(self.temp_pixel))

    def read_from_file(self):
        file = open(self.file_name, "rb")
        buffer = ""
        for byte in file.read():
            buffer += self.full_byte(bin(byte)[2:])
            if len(buffer) >= self.bit_num:
                index = int(len(buffer) / self.bit_num) * self.bit_num
                self.make_subpixels(buffer[:index])
                buffer = buffer[index:]
        if buffer != "":
            self.make_subpixels(buffer + "0" * (self.bit_num - len(buffer)), True)
            buffer = ""

    def write_string(self, data):
        for i in data:
            self.buffer += self.full_byte(bin(ord(i))[2:])
            if len(self.buffer) >= self.bit_num:
                index = int(len(self.buffer) / self.bit_num) * self.bit_num
                self.make_subpixels(self.buffer[:index])
                self.buffer = self.buffer[index:]
        if self.buffer != "":
            self.make_subpixels(self.buffer + "0" * (self.bit_num - len(self.buffer)), True)
            self.buffer = ""

    def write_bin(self, data):
        self.buffer += data
        while len(self.buffer) >= self.bit_num:
            index = int(len(self.buffer) / self.bit_num) * self.bit_num
            self.make_subpixels(self.buffer[:index])
            self.buffer = self.buffer[index:]
        if self.buffer != "":
            self.make_subpixels(self.buffer + "0" * (self.bit_num - len(self.buffer)), True)
            self.buffer = ""


if __name__ == "__main__":
    num = 7
    # image_name = input("Name of the image: ")
    image_name = "goku.png"
    print("The max is:", Injector.sizeof_fmt(Injector.calculate_space(image_name, num)))
    # Injector(image_name, input("Filename: "), num)
    Injector(image_name, "text.txt", num)

# %%
