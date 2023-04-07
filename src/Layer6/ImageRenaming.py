from ntpath import realpath
import os
path = input("The path: ")
img_num = 1
for f in os.listdir(path):
    oldpath = os.path.join(path, f)
    newpath = os.path.join(path, "ImageNum"+str(img_num)+".png")
    os.rename(oldpath, newpath)
    img_num += 1
    