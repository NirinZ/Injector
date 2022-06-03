# %%
import Encoder as enc

di = enc.get_file_checksum(open(r"C:\Users\zniri\Desktop\Coding\Languages\Python\Python Projects\Injector\tm.txt",'rb'))
print(di)
by = enc.checksum_to_bytes(di)
#print(by.hex())

# %%
files = [5, 32 ,2 ,7 ,1, 0, 50]
for i in range(len(files)):
    for j in range(len(files) - i -1):
        if files[i] > files[j+i+1]:
           t =  files[i]
           files[i] = files[j+i+1]
           files[j+i+1] = t