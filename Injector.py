# %%
import time
import os
import numpy as np
from PIL import Image

# img = Image.new( 'RGB', (250,250), "black") #creating a new image

# # Image.fromarray(img, 'RGB').show()
# img.setflags(write=1)
# # for (x,y,rgb), value in np.ndenumerate(img):
# #     img[x,y,rgb] = 175 # set color RGB
# start_time = time.time()
# for i in range(img.shape[0]):   #for each column
#     for j in range(img.shape[1]):
#         for px in range(img.shape[2]):
#             img[i,j,px] = 175 # set color RGB
# end_time = time.time()
# total_time = end_time - start_time
# print("Time: ", total_time)


class Injector:
    bit_num = 2

    temp_pixel = ""
    buffer = ""

    column = 0
    row = 0
    px = 0

    image_name = ""
    file_name = ""

    def __init__(self, image_name, file_name, bit_num = 2):
        self.image_name = image_name
        self.file_name = file_name
        self.bit_num = bit_num
        start_time = time.time()
        self.img = np.array(Image.open(image_name))
        self.img.setflags(write=1)

        self.file_size = os.path.getsize(file_name)
        self.expected_pixel = self.file_size/(self.bit_num*3/8)
        self.available_space = self.calculate_space(self.image_name, self.bit_num)

        if(self.file_size > self.available_space):
            raise OSError("The file is too big! pay attetion to the space limitation of the bit num.")

        # self.img.show()

        # -- header --
        # self.write_string("This image hed injected!")  # verefication  //24 bytes
        # self.write_bin("00000000")  # version //1 byte
        # self.write_bin("10101010")  # start of file //1 byte
        self.read_from_file()
        end_time = time.time()
        total_time = end_time - start_time
        print()
        print(self.row, ',' ,self.column, ':',self.px)
        print("Pixel:", self.row * self.img.shape[1] + self.column)
        print("Time: ", total_time)
        ima = Image.fromarray(self.img, 'RGB')
        ima.show()
        ima.save("save.png")

    @staticmethod
    def full_byte(bina, bit_num=8):
        return (bit_num - len(bina)) * "0" + bina

    # [Injector.full_byte(bin(i)[2:]) for i in chr(int("01101000", 2)).encode()]

    @staticmethod
    def bi(a):
        b=''
        br = bytearray()
        for i in a.encode():
            b += Injector.full_byte(bin(i)[2:])
            br.append(i)
        return b, br

    @staticmethod
    def calculate_space(image_name, bit_num):
        img = np.array(Image.open(image_name))
        return int(img.size * bit_num / 8)

    @staticmethod
    def sizeof_fmt(num, suffix="B"):
        print(f"{num:,}")
        for unit in ["", "K", "M", "G", "T", "P", "E", "Z"]:
            if abs(num) < 1024.0:
                return f"{num:3.2f} {unit}{suffix}"
            num /= 1024.0
        return f"{num:.1f}Y{suffix}"


    # def make_pixel(self, tempicx):
    #     current_pixel = self.pixels[self.row, self.column]
    #     new_pixel = []
    #     for i in current_pixel:  #\/ removing the least significant bit from original pixel
    #         new_pixel.append(int(bin(i)[2:][:-self.bit_num] + self.temp_pixel[:self.bit_num], 2))
    #         # new_pixel.append(0)
    #         tempicx = tempicx[self.bit_num:]           # /\ adding the new pixel

    #     # print(new_pixel)
    #     self.pixels[self.row, self.column] = tuple(new_pixel)
    #     if self.column == self.img.shape[1] - 1:
    #         self.column = 0
    #         self.row += 1
    #     else:
    #         self.column += 1

    def make_subpixels(self, data, last=False):
        for i in range(int(len(data) / self.bit_num)):
            temp_pixel = data[:self.bit_num]
            # print(data)
            data = data[self.bit_num:]
            if len(temp_pixel) == self.bit_num:
                self.img[self.row, self.column, self.px] = int(bin(self.img[self.row, self.column, self.px])[2:][:-self.bit_num] + temp_pixel, 2) # set color RGB
                if self.px == 2:
                    self.px = 0
                    if self.column == self.img.shape[1] - 1:
                        self.column = 0
                        self.row += 1
                        print(f'{100 * self.row*self.img.shape[1]/self.expected_pixel:.1f}',"%", end='           \r')
                    else:
                        self.column += 1
                else:
                    self.px +=1
            elif last:
                temp_pixel += "0" * (self.bit_num * 3 - len( temp_pixel))
                self.make_subpixels(temp_pixel)

    def read_from_file(self):
        file = open(self.file_name, "rb")
        buffer = ""
        for byte in file.read():
            buffer += self.full_byte(bin(byte)[2:])
            if len(buffer) >= self.bit_num:
                index = int(len(buffer) / self.bit_num) * self.bit_num # שולח מספר שמתחלק במקדם ביטים
                self.make_subpixels(buffer[:index])
                buffer = buffer[index:]
        if buffer != "":
            self.make_subpixels(buffer, True)
            buffer = ""

    def write_string(self, data):
        for i in data:
            self.buffer += self.full_byte(bin(ord(i))[2:])
            if len(self.buffer) >= self.bit_num:
                index = int(len(self.buffer) / self.bit_num) * self.bit_num
                self.make_subpixels(self.buffer[:index])
                self.buffer = self.buffer[index:]
        if self.buffer != "":
            self.make_subpixels(self.buffer)
            self.buffer = ""

    def write_bin(self, data):
        self.buffer += data
        while len(self.buffer) >= self.bit_num:
            index = int(len(self.buffer) / self.bit_num) * self.bit_num
            self.make_subpixels(self.buffer[:index])
            self.buffer = self.buffer[index:]
        if self.buffer != "":
            self.make_subpixels(self.buffer)
            self.buffer = ""


if __name__ == "__main__":
    num = 7
    # image_name = input("Name of the image: ")
    image_name = "goku.png"
    print("The max is:", Injector.sizeof_fmt(Injector.calculate_space(image_name, num)))
    # Injector(image_name, input("Filename: "), num)
    Inj = Injector(image_name, "SpeedTest.mp3", num)

# %%

# Image.fromarray(img, 'RGB').show()

