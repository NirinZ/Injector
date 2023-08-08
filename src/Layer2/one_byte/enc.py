import io
import random as rd
from os.path import exists, getsize, basename

#################################################################
# This script encrypts a given file using a user-provided       #
# password. The password is converted into an offset using a    #
# seeded random generator, and then this offset is applied to   #
# each byte in the file to encrypt it. The encrypted data is    #
# written to a new file with a '.enc' extension.                #
#################################################################

def encrypt(file_path: str, offset, close: bool = True) -> str or io.BufferedRandom:
    # Verify that the input file exists
    if not exists(file_path):
        raise Exception(f'File {file_path} does not exist')

    # Open a new file with .enc extension for storing the encrypted data
    encrypted_file = open(basename(file_path) + '.enc', 'wb+')

    # Get the size of the input file for progress calculation
    size = getsize(file_path)
    num = 0  # Counter for encrypted bytes

    # Open the input file in binary mode
    with open(file_path, 'rb') as input_file:
        # For each byte in the input file
        for byte in input_file.read():
            # Add the offset to the byte. If result is larger than 255, subtract 256
            byte = (byte + offset) % 256
            # Convert the integer back to byte and write to the encrypted file
            encrypted_file.write(byte.to_bytes(1, 'little'))
            num += 1

            # Print progress every 100 bytes
            if num % 100 == 0:
                print("Encrypting the file... ", f'{100 * num / size:.1f}', "%", end='\r')

        print("\nEncryption completed.")

    # Close the output file if specified and return the filename, otherwise return the file object
    if close:
        encrypted_file.close()
        return encrypted_file.name
    else:
        encrypted_file.seek(0)
        return encrypted_file


def pass_to_offset(password):
    # Convert a password into an offset using a seeded random generator
    rd.seed(password)
    return rd.randrange(256)


def encrypt_file(file_path: str, password: str, close: bool = True) -> str or io.BufferedRandom:
    # Encrypt a file using a password
    return encrypt(file_path, pass_to_offset(password), close)


if __name__ == '__main__':
    # Get filename and password from the user
    file_path = input("Enter the file path: ")
    password = input("Enter the password: ")

    # Encrypt the file
    encrypt_file(file_path, password)

    print("Encryption completed!")
