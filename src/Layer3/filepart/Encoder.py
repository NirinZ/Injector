# %%
import hashlib
from sys import byteorder
from math import log2
from math import ceil
import io
import os
import copy
from os import path
from os.path import splitext
from os.path import basename
from os.path import dirname
from os.path import exists
from enum import Enum, unique

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
    '''
    ~~~~~ Ordering versions ~~~~~
    num     ordering                                         supported
    --------------------------------------------------------------------
    0       part number (+1B) [50MB]                             V
    1       part number (+3B) [5TB]                              V
    2       offset from the original file start (+5B) [1TB]      V
    3       offset from the original file start (+6B) [256TB]    X
    '''
    PART_NUM1 = 0
    PART_NUM3 = 1
    OFFSET5 = 2
    OFFSET6 = 3

@unique
class NumRapping(Enum):
    '''
    num     format                                         supported
    --------------------------------------------------------------------
    0       normal adding                                        V
    1       utf-8                                                X
    2       utf-16                                               X
    3       utf-nirin                                            X
    '''
    ADDING = 0
    UTF_8 = 1
    UTF_16 = 2
    UTF_NIRIN = 3

@unique
class Checksum(Enum):
    '''
    num     checksum                                         supported
    --------------------------------------------------------------------
    0       no checksum (0B)                                     V
    1       checksum (4B)                                        V
    2       checksum & error correction (not set yet)            X
    3       not set yet                                          X
    '''
    NO_CHECKSUM = 0
    CHECKSUM4 = 1
    ERROR_CORRECTION = 2

class Flags:
    '''
    0 0 -> Ordering version
    0 -> Is supportes storing data size
    0 -> Is last
    0 0 -> Num rapping format  #Encryption type will be in the second layer {0: 1byte, 1: multybyte}
    0 0 -> Checksum type
    '''
    __order_version: Ordering = Ordering.OFFSET5
    __storing_size: bool = False
    __is_last: bool = True
    __num_rapping: NumRapping = NumRapping.ADDING
    __checksum_type: Checksum = Checksum.NO_CHECKSUM # Checksum.CHECKSUM4 Because of issue with the layer 5 that adding extra bytes

    def __init__(self, flags_byte=None):
        if flags_byte is None:
            return
        flags = ord(flags_byte)
        self.__order_version = Ordering(flags >> 6)
        self.__storing_size = bool(flags & 32)
        self.__is_last = bool(flags & 16)
        self.__num_rapping = NumRapping((flags & 12) >> 2)
        self.__checksum_type = Checksum(flags % 4)

    # @classmethod
    # def from_byte(cls, flags_byte=None)
    # Make the constructor normal, and create a classmethod from byte

    def __int__(self) -> int:
        return int( \
            full_byte(bin(self.order_version.value)[2:], 2) + \
            bin(self.storing_size)[2:] + \
            bin(self.is_last)[2:] + \
            full_byte(bin(self.num_rapping.value)[2:], 2) + \
            full_byte(bin(self.checksum_type.value)[2:], 2) \
            , 2)

    def to_byte(self) -> bytes:
        return int(self).to_bytes(1, byteorder)

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

    '''
    FILEPART  # (8B)
    \r\n      # (2B)    0D 0A
    \x1a      # To stop `type`    (1B)    1A
    \n        # To stop `cat`     (1B)    0A
    '''

    filepart_signature = b'FILEPART\r\n\x1a\n'

    def __init__(self, file: io.BufferedRandom, flags: Flags = Flags(), group: str = "none group",
                 order: int = 0, data_size: int = 0, header_length: int = 0, checksum=None):
        self.file = file
        self.name = file.name
        self.flags = flags
        self.group = group
        self.order = order
        self.checksum = checksum
        self.data_size = data_size
        self.header_length = header_length
        # File pointer should point to the data

    def __gt__(self, other):
        return self.order > other.order
    
    def __lt__(self, other):
        return self.order < other.order

    # Does not close the file!
    @classmethod
    def auto_open(cls, filename: str, flags: Flags = Flags()):
        if not os.path.exists(filename):
            raise IOError('File %s does not exist' % filename)
        file = open(filename, 'rb+')
        if check_format(file):
            return Filepart.open_file(file)
        else:
            return Filepart.create(file, flags)

    @classmethod
    def open(cls, filename: str):
        if not os.path.exists(filename):
            raise IOError('File %s does not exist' % filename)
        file = open(filename, 'rb+')
        if check_format(file):
            return Filepart.open_file(file)
        else:
            raise Exception('File %s is not supported' % filename)

    @classmethod
    def open_file(cls, file: io.BufferedReader):
        if not check_format(file):
            raise Exception("The file format is not supported")
        file.seek(12, 1)
        flags = Flags(file.read(1))
        name_len = read_versatile_number(file)
        group = file.read(name_len).decode()
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
            data_bytes = ceil(log2(path.getsize(file.name) - (file.tell() + 1)) / 8)
            data_size = int(file.read(data_bytes)[::-1].hex(), 16)
        else:
            data_size = path.getsize(file.name) - (file.tell() + 1)  # +1 Because of the switch byte
        if file.read(1) != switch_byte:  # Checking of the switch byte
            print(file.tell())
            raise ValueError(f"Could not find switch byte! error in {file.tell() - 1}")
        header_length = file.tell()
        # print('before return', type(data_size), data_size)
        # Now the pointer points to the data
        return cls(file, flags, group, order, data_size, header_length, checksum)

    @classmethod
    def create(cls, file: io.BufferedReader, in_flags: Flags = Flags()):
        data_size = path.getsize(file.name)

        filepart = open(f"{file.name}.filepart", 'wb+')

        # -- Signature -- (12B)
        filepart.write(filepart_signature)  # (12B)

        # -- Flags -- (1B)
        flags: Flags = copy.deepcopy(in_flags)
        flags.is_last = True  # Because on this function only one file is being created
        filepart.write(flags.to_byte())  # (1B)

        # -- Name -- (+1B + name)
        # need to add content signature
        group = basename(file.name)  # get file name
        filepart.write(num_to_versatile_bytes(len(group.encode())))  # write the len of the file name (+1B)
        # encoding for multibyte characters
        filepart.write(group.encode())  # write the file name

        # -- Ordering -- (+1B - +6B)
        order = 0
        if flags.order_version == Ordering.PART_NUM1:
            filepart.write(b'\x00')
        elif flags.order_version == Ordering.PART_NUM3:
            filepart.write(b'\x00' * 3)
        elif flags.order_version == Ordering.OFFSET5:
            filepart.write(b'\x00' * 5)

        # -- Checksum --
        checksum = None
        if flags.checksum_type == Checksum.CHECKSUM4:
            checksum = get_file_checksum(file)[:8] # We are using 8 charecters (4B) checksum
            filepart.write(checksum_to_bytes(checksum))

        # -- Storing size --
        # log2(file_len) /8
        if flags.storing_size:
            total_size = data_size + filepart.tell()
            needed_bytes = ceil(log2(total_size) / 8)
            # Because the gape can be maximum 1 byte I need to do just one check
            filepart.write(
                data_size.to_bytes(ceil(log2(total_size + needed_bytes) / 8), byteorder))  
            # The amount of bytes associated to the size
            # are based on the entire file size and not
            # just the size of the data

        # -- Switch byte --
        filepart.write(switch_byte)

        # -- Header length --
        header_length = filepart.tell()

        # -- Data --
        print()
        file.seek(0)
        data = file.read(2 ** 10)  # Reading 1KB
        while data != b'':  # While data is not empty
            filepart.write(data)
            data = file.read(2 ** 10)
            print("Coping the data to the created file ", 100 * filepart.tell() / data_size, "%", end="                                                     ")
        print()
        file.close()

        filepart.seek(header_length)
        return cls(filepart, flags, group, order, data_size, header_length)

    @classmethod
    def split(cls, sorce_file, size: int):
        if sorce_file.__class__ != Filepart:
            raise ValueError(f"sorce file should be a Filepart")
        if size >= path.getsize(sorce_file.name):
            return sorce_file
        
        avaliable_size = size - (len(Filepart.filepart_signature) + 2)  # +2 for the flags and switch byte
        flags: Flags = copy.deepcopy(sorce_file.flags)
        group = sorce_file.group
        avaliable_size -= len_of_bytes_num(len(group.encode()))  # for the group len byte
        avaliable_size -= len(group.encode())  # for the group bytes
        
        if flags.checksum_type == Checksum.CHECKSUM4:
            avaliable_size -= 4

        if flags.storing_size:
            avaliable_size -= ceil(log2(size) / 8)
            # We are cheking the data_storing here so we culd calculate the order for the sorce file
            
        order = 0
        if flags.order_version == Ordering.PART_NUM1:
            order = sorce_file.order
            avaliable_size -= len_of_bytes_num(order)
            sorce_file.order = order + 1
        elif flags.order_version == Ordering.PART_NUM3:
            order = sorce_file.order
            avaliable_size -= len_of_bytes_num(order, 3)
            sorce_file.order = order + 1

        elif flags.order_version == Ordering.OFFSET5:
            order = sorce_file.order
            avaliable_size -= len_of_bytes_num(order, 5)
            sorce_file.order = order + avaliable_size
        elif flags.order_version == Ordering.OFFSET6:
            order = sorce_file.order
            avaliable_size -= len_of_bytes_num(order, 6)
            sorce_file.order = order + avaliable_size

        

        if avaliable_size < 1:
            raise ValueError("There isn't enough space to store the data, choose bigger size.")

        header_length = size - avaliable_size

        # Now all the header is calculated

        file = open(os.path.dirname(os.path.abspath(sorce_file.name)) + f"\{group} - {order}.filepart", 'wb+')
        filepart = Filepart(file, flags, group, order, avaliable_size, header_length)
        filepart.write_header()
        filepart.write_data_from_filepart(sorce_file)

        return filepart

    def fix_pointer(self):
        self.file.seek(self.header_length)

    def write_header(self) -> None:
        self.file.seek(0)
        self.file.write(Filepart.filepart_signature) # Signature
        self.file.write(self.flags.to_byte()) # Flags

        # Name
        self.file.write(num_to_versatile_bytes(len(self.group.encode())))
        self.file.write(self.group.encode())
        
        # Ordering
        if self.flags.order_version == Ordering.PART_NUM1:
            self.file.write(num_to_versatile_bytes(self.order))
        elif self.flags.order_version == Ordering.PART_NUM3:
            self.file.write(num_to_versatile_bytes(self.order, 3))
        elif self.flags.order_version == Ordering.OFFSET5:
            self.file.write(num_to_versatile_bytes(self.order, 5))

        # Checksum
        if self.flags.checksum_type == Checksum.CHECKSUM4:
            self.file.write(b'\x00' * 4)

        # Storing size
        if self.flags.storing_size:
            self.file.write(
                self.data_size.to_bytes(ceil(log2(self.data_size + self.header_length) / 8), byteorder))
        
        # -- Switch byte --
        self.file.write(switch_byte)

    def rewrite_flags(self):
        self.file.seek(12)
        self.file.write(self.flags.to_byte())
        self.file.seek(self.header_length)

    def rewrite_checksum(self):
        self.file.seek(13) # Signature + Flags
        
        # Name
        name_len = read_versatile_number(self.file)
        self.file.seek(name_len, 1)  # Moving the pointer
        
        # Ordering
        if self.flags.order_version == Ordering.PART_NUM1:
            read_versatile_number(self.file, 1)
        elif self.flags.order_version == Ordering.PART_NUM3:
            read_versatile_number(self.file, 3)
        elif self.flags.order_version == Ordering.OFFSET5:
            read_versatile_number(self.file, 5)
        elif self.flags.order_version == Ordering.OFFSET5:
            read_versatile_number(self.file, 6)

        # Checksum
        if self.flags.checksum_type == Checksum.CHECKSUM4:
            checksum_start = self.file.tell()
            self.file.seek(self.header_length)
            checksum = get_file_checksum(self.file, self.header_length)[:8] # Need fix
            self.file.seek(checksum_start)
            self.file.write(checksum_to_bytes(checksum))
        
        self.file.seek(self.header_length)

    def write_data_from_filepart(self, sorce_file):
        # if self.flags.checksum != Checksum.NO_CHECKSUM:
        #     self.rewrite_checksum(data)
            
        # Pointer should point to the data as always
        print()
        remaning_data = self.data_size
        # print('Remaning data:',remaning_data)
        data_part = 0
        while remaning_data > 0 and data_part != b'':
            if remaning_data < 2**10: # 1KB
                data_part = sorce_file.file.read(remaning_data)
                self.file.write(data_part)
            else:    
                data_part = sorce_file.file.read(2 ** 10)  # Reading 1KB
                self.file.write(data_part)
                print("Writing data from filepart ", 100 * self.file.tell() / self.data_size, "%", end="            \r")
            remaning_data -= len(data_part)
        print()
        # print('dp', sorce_file.file.read(2 ** 10))
        # print('rd', remaning_data)
        # print('ds', self.data_size)

        if data_part == b'': # Last file
            self.flags.is_last = True
            sorce_file.file.close()
            os.remove(sorce_file.name)
            self.rewrite_flags()
        else:
            self.flags.is_last = False
            self.rewrite_flags()
            sorce_file.remove_redundent()
            sorce_file.file.seek(self.header_length)

        self.file.seek(self.header_length)

        if self.flags.checksum_type != Checksum.NO_CHECKSUM:
            self.rewrite_checksum()

    def write_data(self, data: io.BufferedReader):
        print("Start triming the original file")
        data_part = data.read(2 ** 10)  # Reading 1KB
        while data_part != b'':  # While data is not empty
            self.file.write(data_part)
            data_part = data.read(2 ** 10)
            print("Writing data ", 100 * self.file.tell() / self.data_size, "%", end="            \r")
        print()

    def remove_redundent(self) -> None:
        prev_file = self.file
        self.file = open('temp', 'wb+')
        data_size = self.size_of_remaning_bytes(prev_file)
        self.data_size = data_size
        self.write_header()
        self.write_data(prev_file)
        prev_file.close()
        self.file.close()
        os.remove(prev_file.name) ### HERE not closing
        os.rename('temp', prev_file.name)
        self.file = open(prev_file.name, 'rb+')
        self.rewrite_checksum()
        print("Done removing redundant")

    @staticmethod
    def size_of_remaning_bytes(file : io.BufferedReader, move_pointer : bool = False) -> int:
        prev_pointer = file.tell()
        file.seek(0, 2)
        sum = file.tell() - prev_pointer
        if not move_pointer:
            file.seek(prev_pointer)
        return sum

# How many bytes will it takes to store this number by the given bytes_num
def len_of_bytes_num(num: int, bytes_num: int = 1) -> int:
    return len(num_to_versatile_bytes(num, bytes_num))

def read_checksum(checksum_bytes: bytes) -> str:
    checksum = ""
    for byte in checksum_bytes:
        hex1 = byte >> 4
        hex2 = byte % 2 ** 4
        checksum += hex(hex1)[2:] + hex(hex2)[2:] ## Not tested
    return checksum

def checksum_to_bytes(checksum: str) -> bytes:
    _bytes = b''
    for i in range(len(checksum) // 2):
        i *= 2
        hex1 = checksum[i:2 + i][0]
        hex2 = checksum[i:2 + i][1]
        _bytes += byte_from_2hex(hex1, hex2)
    return _bytes

def get_file_checksum(file: io.BufferedReader, pointer: int = 0, return_pointer: bool = True) -> str:
    md5_hash = hashlib.md5()
    file.seek(pointer)
    data = file.read(2 ** 10)
    while data != b'':
        md5_hash.update(data)
        data = file.read(2 ** 10)
    digests = md5_hash.hexdigest()

    if return_pointer:
        file.seek(pointer)

    return digests

# ** Will NOT move the pointer 12 bytes, and the pointer will point to the start! **
def check_format(file: io.BufferedReader) -> bool:
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
    file.seek(name_len, 1)  # Moving the pointer
    if flags.order_version == Ordering.PART_NUM1:
        read_versatile_number(file, 1)
    elif flags.order_version == Ordering.PART_NUM3:
        read_versatile_number(file, 3)
    elif flags.order_version == Ordering.OFFSET5:
        read_versatile_number(file, 5)
    if flags.checksum_type == Checksum.CHECKSUM4:
        file.seek(4, 1)
    if flags.storing_size:
        data_bytes = ceil(log2(path.getsize(file.name) - (file.tell() + 1)) / 8)
        return int(file.read(data_bytes)[::-1].hex(), 16)  # Need to reverse the bytes for little endian byte order
    if file.read(1) != switch_byte:  # Checking of the switch byte
        raise ValueError(f"Could not find switch byte! error in {file.tell() - 1}")
    data_size = path.getsize(file.name) - file.tell()
    file.seek(0)
    return data_size      

def max_bytes_num(bytes_num: int = 1) -> int:
    return 2 ** (8 * bytes_num) - 1

def full_byte(bina, bit_num=8):
    return (bit_num - len(bina)) * "0" + bina

def byte_from_2hex(hex1: str, hex2: str) -> bytes:
    bin1 = full_byte(bin(int(hex1, 16))[2:], 4)
    bin2 = full_byte(bin(int(hex2, 16))[2:], 4)
    byte = int(bin1 + bin2, 2).to_bytes(1, byteorder)
    return byte

def bytes_to_int(byts: bytes, _byteorder: str = byteorder) -> int:
    if _byteorder == 'little':
        return int(byts[::-1].hex(), 16)
    elif _byteorder == 'big':
        return int(byts.hex(), 16)
    else:
        return int(byts.hex(), 16)

# byte_num is the default number of bytes that will be written for the smallest value and will multiply by it
def num_to_versatile_bytes(num: int, bytes_num: int = 1, _byteorder: str = byteorder) -> bytes:
    _bytes = b''
    while num >= max_bytes_num(bytes_num):
        _bytes += max_bytes_num(bytes_num).to_bytes(bytes_num, _byteorder)
        num -= max_bytes_num(bytes_num)
    _bytes += num.to_bytes(bytes_num, _byteorder)
    return _bytes

# ** Moving the pointer **
def read_versatile_number(file, bytes_num: int = 1) -> int:
    current_bytes = bytes_to_int(file.read(bytes_num))
    total_num = current_bytes
    while current_bytes >= max_bytes_num(bytes_num):
        current_bytes = bytes_to_int(file.read(bytes_num))
        total_num += current_bytes
    return total_num

def sizeof_fmt(num, suffix="B"):
    print(f"{num:,}")
    for unit in ["", "K", "M", "G", "T", "P", "E", "Z"]:
        if abs(num) < 1024.0:
            return f"{num:3.2f} {unit}{suffix}"
        num /= 1024.0
    return f"{num:.1f}Y{suffix}"

def print_bytes_max():
    for i in range(1, 16):
        print(i, ':', f'{2 ** (8 * i):,}', " ==> ", sizeof_fmt(2 ** (8 * i)))

# Working version
if __name__ == "__main__":
    print(os.getcwd())
    file_name = input("File name: ")
    size = int(input("Size: "))
    # f = open(file_name, 'rb')
    # size = input("Size: ")
    flags = Flags()
    flags.order_version = Ordering.OFFSET5
    flags.storing_size = False  # Recommended to be false
    flags.num_rapping = NumRapping.ADDING
    flags.checksum_type = Checksum.CHECKSUM4
    # fp = Filepart.auto_open(file_name, flags)
    fp = Filepart.auto_open(file_name, flags)
    sp_fp = Filepart.split(fp, size)
    # to_fi(file_name, size, flags)
    pass
