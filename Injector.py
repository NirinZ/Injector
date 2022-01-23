# %%

import time

from PIL import Image

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
        for i in range(self.img.size[0]):   #for each column
            for j in range(self.img.size[1]):  #for each row
                self.pixels[i,j] = (50, 80, 50)  #set color RGB
        end_time = time.time()
        total_time = end_time - start_time
        print("Time: ", total_time)
        self.img.show()

if __name__ == "__main__":
    Injector().write_to_image()
'''


# %%
# img = Image.new( 'RGB', (250,250), "black") #creating a new image

class Injector:
    def __init__(self):
        self.bit_num = 2

        self.temp_pixel = ""
        self.buffer = ""

        self.row = 0
        self.column = 0

        image_name = input("Name of the image: ")

        self.img = Image.open(image_name)
        self.pixels = self.img.load()
        self.img.show()
        start_time = time.time()

    @staticmethod
    def make_pixel(self):
        current_pixel = self.pixels[self.self.column, self.row]
        new_pixel = []
        for i in current_pixel:
            new_pixel.append(bin(current_pixel[0])[2:][:-self.bit_num] + self.temp_pixel[:2])
            self.temp_pixel = self.temp_pixel[2:]
        self.pixels[self.self.column, self.row] = tuple(new_pixel)
        if self.row == self.img.size[1] - 1:
            self.row = 0
            self.self.column += 1
        else:
            self.row += 1
    
    @staticmethod
    def make_subpixels(self, data):
        for i in range(data / self.bit_num):
            self.temp_pixel += data[:self.bit_num]
            data = data[:self.bit_num]
            if len(self.temp_pixel) == self.bit_num * 3:
                self.make_pixel()
    
    @staticmethod
    def read_from_file(self, file_name):
        file = open(file_name, "rb")
        buffer = ""
        for byte in file.read():
            buffer += bin(byte)[2:]
            if (len(buffer) >= self.bit_num):
                index = int(len(buffer) / self.bit_num) * self.bit_num
                self.make_subpixels(buffer[:index])
                buffer = buffer[index:]
    
    @staticmethod
    def write_string(self, data):
        for i in data:
            self.buffer += bin(ord(i))[2:]
            if (len(self.buffer) >= self.bit_num):
                index = int(len(self.buffer) / self.bit_num) * self.bit_num
                self.make_subpixels(self.buffer[:index])
                self.buffer = self.buffer[index:]
        buffer = ""

    @staticmethod
    def write_bin(self, data):
        self.buffer += data[2:]
        while len(self.buffer) >= self.bit_num:
            index = int(len(self.buffer) / self.bit_num) * self.bit_num
            self.make_subpixels(self.buffer[:index])
            self.buffer = self.buffer[index:]
        buffer = ""

    def write_to_image(image_name):

        for i in range(self.img.size[0]):  # for each column
            for j in range(self.img.size[1]):  # for each self.row
                self.pixels[i, j] = (50, 80, 50)  # set color RGB


end_time = time.time()
total_time = end_time - start_time
print("Time: ", total_time)
self.img.show()
# %%
