import io
import os
from sys import byteorder
from math import ceil, log2

combined_signature = b'CMF'

class Combine():

    current_size: int = 0
    files: list[io.BufferedRandom] = []
    def __init__(self, file: io.BufferedRandom, total_size: int) -> None:
        self.file = file
        self.name = file.name
        self.current_size += file.seek(0,2)
        file.seek(0)
        #self.files.append(file)
        self.total_size: int = total_size

    @classmethod
    def create(cls, file: io.BufferedReader, total_size: int):
        file_size = file.seek(0,2)
        file.seek(0)
        combined = open(f"{file.name}.combined", 'wb+')

        # -- Signature -- (3B)
        combined.write(combined_signature)

        # -- Num of files -- (1B) [NOT dinemic]
        combined.write(b'\x00')

        # -- Swintching point -- (Dynemic)
        switch_point = len(combined_signature) + 1 + file_size
        others = 3+1 # 3 to header + 1 to num of files
        needed_bytes = ceil(log2(file_size + others) / 8)
        combined.write(
            switch_point.to_bytes(needed_bytes, byteorder)   
        )

        header_length = combined.tell()

        # -- Data --
        print()
        file.seek(0)
        data = file.read(2 ** 10)  # Reading 1KB
        while data != b'':  # While data is not empty
            combined.write(data)
            data = file.read(2 ** 10)
            print("Coping the data to the created file ", 100 * combined.tell() / file_size, "%", end="                                   \r")
        print()
        file.close()

        combined.seek(header_length)
        return cls(combined, total_size)

    @classmethod
    def add_file():
        pass

    def remaning_size(self) -> int:
        return self.total_size - self.current_size

    @staticmethod
    def is_more_spase(size: int, file: str) -> bool:
        file_size = os.path.getsize(file)
        others = 3+1 # 3 to header + 1 to num of files
        needed_bytes = ceil(log2(file_size + others) / 8)
        return size > file_size + needed_bytes + others + 40 # 40 -> normal header.
