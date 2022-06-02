import pyperclip

by = b''
for st in input("Enter bytes: ").split(" "):
    by += int(st,16).to_bytes(1, 'little')
pyperclip.copy(str(by))
print(by)

