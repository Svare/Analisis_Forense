#!/usr/bin/python3

from sys import argv

if __name__ == "__main__":

    if len(argv) < 2:
        print('Error: at least 2 arguments are expected')
        print('python3 hexedit.py bunch_of_bytes_name file1 [...]')
        exit()

    with open(argv[1], 'wb') as bunch_of_bytes_name:
        for file in argv[2:]:
            with open(file, 'rb') as curr_file:
                bunch_of_bytes_name.write(b'\x00'*1024*512) # Write 1/2 Byte of \x00
                bunch_of_bytes_name.write(curr_file.read()) # Write the bytes of the current file
                bunch_of_bytes_name.write(b'\x00'*1024*512) # Write 1/2 Byte of \x00