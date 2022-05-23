import Encoder as enc

di = enc.get_file_checksum(open(r"C:\Users\zniri\Desktop\Coding\Languages\Python\Python Projects\Injector\t.txt",'rb'))
print(enc.checksum_to_bytes(di).hex())