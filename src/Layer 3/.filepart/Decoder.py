import Encoder
from Encoder import Filepart
import os


def merge_files(files: list):
    if len(files) == 0:
        return
    out_file = open(files[0].group, 'wb+')

    for f in files:
        f.fix_pointer()

    for f in files:
        data = f.file.read(2 ** 10)
        while data != b'':
            out_file.write(data)
            data = f.file.read(2 ** 10)

    for f in files:
        f.fix_pointer()

    if not files[-1].flags.is_last:
        new_file = Filepart.create(out_file, files[-1].flags)
    else:
        out_file.close()

    
def check_ordering(files: list) -> bool:
    if len(files) == 0:
        return True
    order_version: Encoder.Ordering = files[0].flags.order_version

    if order_version == Encoder.Ordering.PART_NUM1 or order_version == Encoder.Ordering.PART_NUM3:
        num: int = 0
        for f in files:
            if num != f.order:
                return False
            num += 1
        return True

    elif order_version == Encoder.Ordering.OFFSET5 or order_version == Encoder.Ordering.OFFSET6:
        offset: int = 0
        for f in files:
            if offset < f.order:
                return False
            if offset > f.order:
                raise Exception("There is still no support for offset overlaping...")
            offset += f.data_size
        return True
    
def sort_ordering(files: list) -> list:
    for i in range(len(files)):
        for j in range(len(files) - i -1):
            if files[i] > files[j+i+1]:
                t =  files[i]
                files[i] = files[j+i+1]
                files[j+i+1] = t
    return files

def check_checksums(files: list) -> list:
    if len(files) == 0:
        return list
    for i in range(len(files)):
        if files[i].flags.checksum_type == Encoder.Checksum.CHECKSUM4:
            checksum = Encoder.get_file_checksum(files[i].file, files[i].header_length)[:8]
            if files[i].checksum != checksum:
                print(f"File {files[i].name} have mismatching checksum!")
                files.pop(i)
    return files

def check_formats(files: list) -> bool:
    if len(files) == 0:
        return True
    order_version: Encoder.Ordering = files[0].flags.order_version
    num_rapping: Encoder.NumRapping = files[0].flags.num_rapping
    
    for f in files:
        if f.flags.order_version != order_version or f.flags.num_rapping != num_rapping:
            return False

    return True

def add_files(path: str) -> list:
    files = []
    os.chdir(dir_path)
    for f in os.listdir(dir_path):
        try:
            files.append(Filepart.open(f))
        except Exception as e:
            print("Error in", f + ':\n', str(e))
    if not check_formats(files):
        print("Not all files have the same format!")
    return files
    
def auto_all(path: str):
    files = add_files(path)
    if len(files) == 0:
        print("There are no files to work with")
        return
    if not check_formats(files):
        print("Not all the files have the same format!")
        return
    files = check_checksums(files)
    files = sort_ordering(files)
    if not check_ordering(files):
        print("You are missing some files in the middle!")
        return
    merge_files(files)

if __name__ == '__main__':
    print(os.getcwd())
    dir_path = os.path.abspath(input("Enter the directory for all the fileparts: "))
    auto_all(dir_path)