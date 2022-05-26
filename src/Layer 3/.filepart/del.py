# %%
import Encoder as enc

di = enc.get_file_checksum(open(r"C:\Users\zniri\Desktop\Coding\Languages\Python\Python Projects\Injector\tm.txt",'rb'))
print(di)
by = enc.checksum_to_bytes(di)
#print(by.hex())