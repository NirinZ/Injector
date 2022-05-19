#%%
import hashlib
from sys import byteorder
from math import log2
from math import ceil
import os
from os import path
from os.path import splitext
from os.path import basename
from os.path import dirname
from os.path import exists
from enum import Enum, unique

from matplotlib.pyplot import flag

'''
---- Simbols ----
(XB) -> X bytes size are allocated in the file
[XB] -> optimazed for size of X bytes
'''

'''
            00000000
start byte  10101010 170 0xaa ª
switch byte 10000001 129 0x81 \x81
end byte    01010101 85  0x55 U
 '''

'''
Improvments:
- implemnting the utf-8 encoding for numbers <== TO DO this first
- try the utf-16 and utf-32
- fix the flags for that
'''

'''
~~~ JOJO Model ~~~
1: Compression
2: Encryption
3: File spliting
4: File combining
5: Data injecting
6: Data organizing

~~~ Dio Model ~~~
1: Files making 1-3
2: Files gruping 4
3: Data prepering 5-6
'''

filepart_signature = b'FILEPART\r\n\x1a\n'
start_byte = b'\xaa'
switch_byte = b'\x81'
end_byte = b'\x55'

@unique
class Ordering(Enum):
    PART_NUM1 = 0
    PART_NUM3 = 1
    OFFSET5 = 2
    OFFSET6 = 3

@unique
class NumRapping(Enum):
    ADDING = 0
    UTF_8 = 1
    UTF_16 = 2
    UTF_NIRIN = 3

@unique
class Checksum(Enum):
    NO_CHECKSUM = 0
    CHECKSUM4 = 1
    ERROR_CORRECTION = 2

class Flags:
    
    '''
    0 0 -> Ordering version
    0 -> Is supportes storing data size
    0 -> Is last
    0 0 -> Num rapping format {0: normal adding, V | 1: utf-8, X | 2: utf-16, X | 3: utf-nirin, X} #Encryption type will be in the second layer {0: 1byte, 1: multybyte}
    0 0 -> Checksum type
    '''
    __order_version: Ordering = Ordering.OFFSET5
    __storing_size: bool = False
    __is_last: bool = True
    __num_rapping: NumRapping = NumRapping.ADDING
    __checksum_type: Checksum = Checksum.NO_CHECKSUM
    def __init__(self, flags_byte=None):
        if flags_byte is None:
            return
        flags = ord(flags_byte)
        self.__order_version = Ordering(flags >> 6)
        self.__storing_size =  bool(flags & 32)
        self.__is_last = bool(flags & 16)
        self.__num_rapping = NumRapping((flags & 12) >> 2)
        self.__checksum_type = Checksum(flags % 4)

    def get_flags_number(self) -> int:
        return int(\
            full_byte(bin(self.order_version.value)[2:], 2) +\
            bin(self.storing_size)[2:] +\
                bin(self.is_last)[2:] +\
                    full_byte(bin(self.num_rapping.value)[2:], 2) +\
                        full_byte(bin(self.checksum_type.value)[2:], 2)\
                            ,2)

    def get_flags_byte(self) -> bytes:
        return self.get_flags_number().to_bytes(1, byteorder)

    @property
    def order_version(self) -> Ordering:
        return self.__order_version
    @property
    def storing_size(self) -> bool:
        return self.__storing_size
    @property
    def is_last(self) -> bool:
        return self.__is_last
    @property
    def num_rapping(self) -> NumRapping:
        return self.__num_rapping
    @property
    def checksum_type(self) -> Checksum:
        return self.__checksum_type

    @order_version.setter
    def order_version(self, value) -> None:
        self.__order_version = Ordering(value)
    @storing_size.setter
    def storing_size(self, value) -> None:
        self.__storing_size = bool(value)
    @is_last.setter
    def is_last(self, value) -> None:
        self.__is_last = bool(value)
    @num_rapping.setter
    def num_rapping(self, value) -> None:
        self.__num_rapping = NumRapping(value)
    @checksum_type.setter
    def checksum_type(self, value) -> None:
        self.__checksum_type = Checksum(value)

class Filepart():
    
    filepart_signature = b'FILEPART\r\n\x1a\n'

    def __init__(self, flags: Flags=Flags(), group: str = "none group"):
        self.flags = flags
        self.group = group

    def __init__(self, filename):
        file = open(filename, 'rb')
        name = file.name
        if not check_format(file):
            raise Exception("The file format is not supported")
        file.seek(12, 1)
        flags = Flags(file.read(1))
        name_len = read_versatile_number(file)
        group = file.read(name_len)
        order = 0
        if flags.order_version == Ordering.PART_NUM1:
            order = read_versatile_number(file, 1)
        elif flags.order_version == Ordering.PART_NUM3:
            order = read_versatile_number(file, 3)
        elif flags.order_version == Ordering.OFFSET5:
            order = read_versatile_number(file, 5)
        if flags.checksum_type == Checksum.CHECKSUM4:
            checksum_bytes = file.read(4)
            checksum = read_checksum(checksum_bytes)
        else:
            checksum = None
        if flags.storing_size:
            data_bytes = ceil(log2(path.getsize(file.name) -(file.tell() + 1))/8)
            data_size = int(file.read(data_bytes)[::-1].hex(), 16)
        else:
            data_size = path.getsize(file.name) - (file.tell() + 1) # +1 Because of the switch byte
        if file.read(1) != switch_byte: # Checking of the switch byte
            print(file.tell())
            raise ValueError(f"Could not find switch byte! error in {file.tell() -1}")
        # now the pointer points to the data

    def __init__(self, sorce_file, size:int):
        if sorce_file.__class__ != Filepart:
            raise ValueError(f"sorce file should be a Filepart")
        if size >= path.getsize(sorce_file.name):
            self = sorce_file
            return
        avaliable_size = size - (len(Filepart.filepart_signature) + 2) # for the flags and switch byte
        self.flags = sorce_file.flags
        self.group = sorce_file.group
        avaliable_size -= len_of_bytes_num(len(self.group.encode())) # for the group len byte
        avaliable_size -= len(self.group.encode())  # for the group bytes
        
        if flags.checksum_type == Checksum.CHECKSUM4:
            avaliable_size -= 4


        order = 0
        if flags.order_version == Ordering.PART_NUM1:
            order = sorce_file.order + 1
            avaliable_size -= len_of_bytes_num(order)

        elif flags.order_version == Ordering.PART_NUM3:
            order = sorce_file.order + 1
            avaliable_size -= len_of_bytes_num(order, 3)

        elif flags.order_version == Ordering.OFFSET5:
            avaliable_size -= len_of_bytes_num(avaliable_size, 5)
            order = avaliable_size
        
        elif flags.order_version == Ordering.OFFSET6:
            avaliable_size -= len_of_bytes_num(avaliable_size, 6)
            order = avaliable_size



    def get_header_size(self):
        pass


# How many bytes will it takes to store this number by the given bytes_num
def len_of_bytes_num(num:int, bytes_num:int=1) -> int:
    return len(num_to_versatile_bytes(num, bytes_num))

def read_checksum(checksum_bytes:bytes) -> str:
    checksum = ""
    for byte in checksum_bytes:
        hex1 = byte >> 4
        hex2 = byte % 2**4
        checksum += hex1 + hex2
    return checksum

# ** Will NOT move the pointer 12 bytes, and the pointer will point to the start! **
def check_format(file) -> bool:
    file.seek(0)
    supported = file.read(12) == filepart_signature
    file.seek(0)
    return supported


# ** Does format check **
def get_data_size(file) -> int:
    if not check_format(file):
        return 0
    file.seek(12, 1)
    flags = Flags(file.read(1))
    name_len = read_versatile_number(file)
    file.seek(name_len, 1) # Moving the pointer
    if flags.order_version == Ordering.PART_NUM1:
        read_versatile_number(file, 1)
    elif flags.order_version == Ordering.PART_NUM3:
        read_versatile_number(file, 3)
    elif flags.order_version == Ordering.OFFSET5:
        read_versatile_number(file, 5)
    if flags.checksum_type == Checksum.CHECKSUM4:
        file.seek(4, 1)
    if flags.storing_size:
        data_bytes = ceil(log2(path.getsize(file.name) -(file.tell() + 1))/8)
        return int(file.read(data_bytes)[::-1].hex(), 16) # Need to reverse the bytes for little endian byte order
    if file.read(1) != switch_byte: # Checking of the switch byte
        raise ValueError(f"Could not find switch byte! error in {file.tell() -1}")
    data_size = path.getsize(file.name) - file.tell()
    file.seek(0)
    return data_size


def split_filepart(file_name, size):
    sorce_file = Filepart(file_name)

    if size >= path.getsize(sorce_file.name):
        new_name = os.path.join(dirname(sorce_file.name), splitext(basename(file_name))[0] + " - Last.filepart")
        os.rename(sorce_file.name, new_name)
        print("Done splitting the file")
        return
    
    else:
        new_file = Filepart(sorce_file.flags, sorce_file.group, checksum=sorce_file.checksum)


def write_filepart_header(file, size):
    pass

def file_to_filepart(file_name: str, flags: Flags=Flags()):
    file = open(file_name, 'rb')
    size = path.getsize(file.name)

    filepart = open(f"{file_name}.filepart", 'wb+')

    # -- Signature -- (12B)
    filepart.write('FILEPART'.encode())         #                   (8B)
    filepart.write('\r\n'.encode())             #                   (2B)    0D 0A
    filepart.write('\x1a'.encode())             # To stop `type`    (1B)    1A
    filepart.write('\n'.encode())               # To stop `cat`     (1B)    0A

    # -- Flags -- (1B)
    flags.is_last = True # Because on this function only one file is being created
    filepart.write(flags.get_flags_byte()) # (1B)

    # -- Name -- (+1B + name)
    # need to add content signature
    name =  basename(file.name)      # get file name
    filepart.write(num_to_versatile_bytes(len(name.encode()))) # write the len of the file name (+1B)
                                                               # encoding for multibyte characters
    filepart.write(name.encode())                              # write the file name


    # -- Ordering -- (+1B - +6B)
    '''
    ~~~~~ Ordering versions ~~~~~
    num     ordering                                         supported
    --------------------------------------------------------------------
    0       part number (+1B) [50MB]                             V
    1       part number (+3B) [5TB]                              V
    2       offset from the original file start (+5B) [1TB]      V
    3       offset from the original file start (+6B) [256TB]    X
    '''
    if flags.order_version == Ordering.PART_NUM1:
        filepart.write(b'\x00')
    elif flags.order_version == Ordering.PART_NUM3:
        filepart.write(b'\x00'* 3)
    elif flags.order_version == Ordering.OFFSET5:
        filepart.write(b'\x00'* 5)

    # -- Checksum --
    '''
    num     checksum                                         supported
    --------------------------------------------------------------------
    0       no checksum (0B)                                     V
    1       checksum (4B)                                        V
    2       checksum & error correction (not set yet)            X
    3       not set yet                                          X
    '''
    if flags.checksum_type == Checksum.CHECKSUM4:
        md5_hash = hashlib.md5()
        data = file.read(2**10)
        while data != b'':
            md5_hash.update(data)
            data = file.read(2**10)
        digest = md5_hash.hexdigest()
        digest = digest[:8]
        for i in range(len(digest)//2):
            i*=2
            hex1 = digest[i:2+i][0]
            hex2 = digest[i:2+i][1]
            filepart.write(byte_from_2hex(hex1, hex2))
        file.seek(0)

    # -- Storing size --
    # log2(file_len) /8
    if flags.storing_size:
        filepart.write(size.to_bytes(ceil(log2(size) /8), byteorder)) # needs FIX

    # -- Switch byte --
    filepart.write(switch_byte)

    # -- Data --
    print()
    data = file.read(2**10) # Reading 1KB
    while data != b'': # While data is not empty
        filepart.write(data)
        data = file.read(2**10)
        print(100 * filepart.tell()/ size,"%", end="            \r")
    print()

    # Taking a split from the file
    split_filepart(file_name, size)

def max_bytes_num(bytes_num:int=1) -> int:
    return 2**(8 * bytes_num) - 1

def full_byte(bina, bit_num=8):
        return (bit_num - len(bina)) * "0" + bina

def byte_from_2hex(hex1: str, hex2: str) -> bytes:
    bin1 = full_byte(bin(int(hex1, 16))[2:], 4)
    bin2 = full_byte(bin(int(hex2, 16))[2:], 4)
    byte = int(bin1+bin2, 2).to_bytes(1, byteorder)
    return byte

def bytes_to_int(byts: bytes, _byteorder: str=byteorder) -> int:
    if _byteorder == 'little':
        return int(byts[::-1].hex(), 16)
    elif _byteorder == 'big':
        return int(byts.hex(), 16)
    else:
        return int(byts.hex(), 16)

# byte_num is the default number of bytes that will be written for the smallest value and will multiply by it
def num_to_versatile_bytes(num:int, bytes_num:int=1, _byteorder: str=byteorder) -> bytes:
    _bytes = b''
    while num >= max_bytes_num(bytes_num):
        _bytes += max_bytes_num(bytes_num).to_bytes(bytes_num, _byteorder)
        num -= max_bytes_num(bytes_num)
    _bytes += num.to_bytes(bytes_num, _byteorder)
    return _bytes

# ** Moving the pointer **
def read_versatile_number(file, bytes_num:int=1) -> int:
    current_bytes = bytes_to_int(file.read(bytes_num))
    total_num = current_bytes
    while current_bytes >= max_bytes_num(bytes_num):
        current_bytes = bytes_to_int(file.read(bytes_num))
        total_num += current_bytes
    return total_num
    

def to_fi(file_name:str, size:int, flags: Flags=Flags()) -> None:
    if not exists(file_name):
        print("File does not exist: " + file_name)
        input()
        exit()
    if exists(path.join(dirname(file_name), splitext(basename(file_name))[0] + ".filepart")): # The file already been trimed
        print("Found existing file: " + path.join(dirname(file_name)), splitext(basename(file_name))[0] + ".filepart")
        split_filepart(file_name, size)
    else:
        print("Could not find a file, creating a new one", path.join(dirname(file_name)), splitext(basename(file_name)[0] + ".filepart"))
        file_to_filepart(file_name, flags)

    
def sizeof_fmt(num, suffix="B"):
    print(f"{num:,}")
    for unit in ["", "K", "M", "G", "T", "P", "E", "Z"]:
        if abs(num) < 1024.0:
            return f"{num:3.2f} {unit}{suffix}"
        num /= 1024.0
    return f"{num:.1f}Y{suffix}"

def print_bytes_max():
    for i in range(1, 16):
	    print(i, ':', f'{2**(8*i):,}', " ==> ", sizeof_fmt(2**(8*i)))

#save 4
if __name__ == "__main__": ## working on the filepart class
    print(os.getcwd())
    file_name = input("File name: ")
    Filepart(file_name)
    size = input("Size: ")
    flags = Flags()
    flags.order_version = Ordering.PART_NUM1
    flags.storing_size = False # Recommended to be false
    flags.num_rapping = NumRapping.ADDING
    flags.checksum_type = Checksum.NO_CHECKSUM
    to_fi(file_name, size, flags)




    