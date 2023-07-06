import io
import random as rd
from os.path import splitext, basename, exists, getsize

#################################################################
# This script contains a simple file decryption mechanism.      #
# The decryption is based on a password that is converted       #
# into a "seed" for the random function to generate an offset.  #
# The offset is then used to adjust each byte in the file.      #
# The encrypted file should have an ".enc" extension, and the   #
# output will be written to a new file. The script will also    #
# print out the progress of the decryption process.             #
#################################################################

def dec(file: str, offset, close: bool = True) -> str or io.BufferedRandom:
  # Check if the file exists
  if not exists(file):
    raise Exception(f'File {file} does not exist')

  # If it's an .enc file, remove the extension for the output filename
  dir = basename(file)
  if splitext(dir)[1] == ".enc":
    dir = splitext(dir)[0]

  # Open a new output file for writing decrypted data
  nf = open(dir + ' - Decrypted', 'wb+')

  size = getsize(file)
  num = 0  # Counter for decrypted bytes

  with open(file, 'rb+') as of:
    # Read and decrypt each byte from the file
    for i in of.read():
      # Subtract the offset from byte. If result is negative, add 256
      i = (i - offset + 256) % 256
      nf.write(i.to_bytes(1, 'little'))  # Convert the integer back to byte and write to the new file
      num += 1

      # Print progress every 100 bytes
      if num % 100 == 0:
        print("Decrypting the file... ", f'{100 * num / size:.1f}', "%", end='\r')

    print("\nDecryption completed.")

  # Close the output file if specified and return the filename, otherwise return the file object
  if close:
    nf.close()
    return nf.name
  else:
    nf.seek(0)
    return nf


def pass_to_offset(password):
  # Convert a password into an offset using a seeded random generator
  rd.seed(password)
  return rd.randrange(256)


def decrypt_file(file: str, password: str, close: bool = True) -> str or io.BufferedRandom:
  # Decrypt a file using a password
  return dec(file, pass_to_offset(password), close)


if __name__ == '__main__':
  # Get filename and password from the user
  file = input("Enter the file path: ")
  password = input("Enter the password: ")

  # Decrypt the file
  decrypt_file(file, password)

  print("Done!")
