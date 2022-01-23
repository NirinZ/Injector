# %%

import time
from PIL import Image
from matplotlib import pyplot as plt
from bitstring import ConstBitStream

class Injector:
    def __init__(self):
        self.img = Image.open("sub.jpg")
        self.file = open("text.txt", "rb")
        #img = Image.new( 'RGB', (250,250), "black") #creating a new image
        self.pixels = self.img.load() # creates the pixel map

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
# %%
