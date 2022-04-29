from PIL import Image
from os.path import splitext, basename


def check_injc(bit_num, image_name):
    img = Image.open(image_name)
    pixels = img.load()
    tpx = []
    for i in range(img.size[1]):   #for each row
        for j in range(img.size[0]):  #for each column
            for color in pixels[j,i]: # color RGB
                num = int(full_byte(bin(color)[2:])[-bit_num:], 2)
                tpx.append(normalize(num, bit_num))
            pixels[j, i] = tuple(tpx)
            tpx = []
        print(f'{100 * i/ img.size[1]:.1f}',"%", end="            \r")
    img.show()
    img.save(splitext(basename(image_name))[0] + " - out.png")

    
def full_byte(bina, bit_num=8):
    return (bit_num - len(bina)) * "0" + bina

def normalize(value, bit_num, max_value = 255):
    return int(max_value*value/(2**bit_num - 1))

if __name__ == "__main__":
    bit_num = int(input("Bit num: "))
    image_name = input("Image name: ")
    check_injc(bit_num, image_name)
    print("Done!")