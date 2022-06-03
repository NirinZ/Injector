import os
import sys
sys.path.append(os.path.dirname(__file__))
import Encoder
from Encoder import Filepart

 
class Decoder:
    def __init__(self, dir_path):
        self.dir_path: str = dir_path
        self.files: list = []

        self.add_files()
        if len(self.files) == 0:
            print("There are no files to work with")
            exit(1)
        if not self.check_formats():
            print("Not all the files have the same format!")
            exit(1)
        self.check_checksums()
        if len(self.files) == 0:
            print("There are no files to work with")
            exit(1)
        self.sort_ordering()
        if not self.check_ordering():
            print("You are missing some files in the middle!")
            exit(1)    

        self.file: str = ""
        self.is_last: bool = False
        self.file, self.is_last = self.merge_files()

    def merge_files(self) -> str and bool:
        if len(self.files) == 0:
            return

        out_file = open(self.files[0].group, 'wb+')

        for f in self.files:
            f.fix_pointer()

        for f in self.files:
            data = f.file.read(2 ** 10)
            while data != b'':
                out_file.write(data)
                data = f.file.read(2 ** 10)

        for f in self.files:
            f.fix_pointer()

        if not self.files[-1].flags.is_last:
            temp = out_file.name
            out_file = Filepart.create(out_file, self.files[-1].flags)
            out_file.file.close()
            os.remove(temp)
        else:
            out_file.close()

        return out_file.name, self.files[-1].flags.is_last
        
    def check_ordering(self) -> bool:
        if len(self.files) == 0:
            return True
        order_version: Encoder.Ordering = self.files[0].flags.order_version

        if order_version == Encoder.Ordering.PART_NUM1 or order_version == Encoder.Ordering.PART_NUM3:
            num: int = 0
            for f in self.files:
                if num != f.order:
                    return False
                num += 1
            return True

        elif order_version == Encoder.Ordering.OFFSET5 or order_version == Encoder.Ordering.OFFSET6:
            offset: int = 0
            for f in self.files:
                if offset < f.order:
                    return False
                if offset > f.order:
                    raise Exception("There is still no support for offset overlaping...")
                offset += f.data_size
            return True
        
    def sort_ordering(self) -> list:
        for i in range(len(self.files)):
            for j in range(len(self.files) - i -1):
                if self.files[i] > self.files[j+i+1]:
                    t =  self.files[i]
                    self.files[i] = self.files[j+i+1]
                    self.files[j+i+1] = t

    def check_checksums(self):
        for i in range(len(self.files)):
            if self.files[i].flags.checksum_type == Encoder.Checksum.CHECKSUM4:
                checksum = Encoder.get_file_checksum(self.files[i].file, self.files[i].header_length)[:8]
                if self.files[i].checksum != checksum:
                    print(f"File {self.files[i].name} have mismatching checksum!")
                    self.files.pop(i)

    def check_formats(self) -> bool:
        order_version: Encoder.Ordering = self.files[0].flags.order_version
        num_rapping: Encoder.NumRapping = self.files[0].flags.num_rapping
        
        for f in self.files:
            if f.flags.order_version != order_version or f.flags.num_rapping != num_rapping:
                return False

        return True

    def add_files(self):
        os.chdir(self.dir_path)
        for f in os.listdir(self.dir_path):
            try:
                self.files.append(Filepart.open(f))
            except Exception as e:
                print("Error in", f + ':\n', str(e))
        if not self.check_formats():
            print("Not all files have the same format!")
        
# def auto_all(self, path: str) -> str:
#     files = add_files(path)
#     if len(files) == 0:
#         print("There are no files to work with")
#         exit(1)
#     if not check_formats(files):
#         print("Not all the files have the same format!")
#         exit(1)
#     files = check_checksums(files)
#     files = sort_ordering(files)
#     if not check_ordering(files):
#         print("You are missing some files in the middle!")
#         exit(1)    
#     return merge_files(files)

if __name__ == '__main__':
    print(os.getcwd())
    dir_path = os.path.abspath(input("Enter the directory for all the fileparts: "))
    Decoder(dir_path)