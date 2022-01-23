# %%
import time

import numpy as np
from PIL import Image
from matplotlib import image

# img = Image.new( 'RGB', (250,250), "black") #creating a new image
img = np.array(Image.open("sub.jpg"))
# %%
# Image.fromarray(img, 'RGB').show()
img.setflags(write=1)
# for (x,y,rgb), value in np.ndenumerate(img):
#     img[x,y,rgb] = 175 # set color RGB
start_time = time.time()
for i in range(img.shape[0]):   #for each column
    for j in range(img.shape[1]):
        for px in range(img.shape[2]):
            img[i,j,px] = 175 # set color RGB
end_time = time.time()
total_time = end_time - start_time
print("Time: ", total_time)
# Image.fromarray(img, 'RGB').show()

