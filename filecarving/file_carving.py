import json
from sys import argv
from time import time

# EXE 4D5A [MZ]
# ZIP 504B0304 [PK]
# PNG 89504E47 [.PNG]
# JPG/JPEG FFD8
# MP3 494433 [ID3]

def get_config(json_config_file):

    '''Lee un archvo json y retorna el json decodificado.'''

    with open(json_config_file, 'r') as config_file:
        return json.load(config_file)

def units_to_bytes(decode_me):

    '''Obtiene el numero de bytes a partir de una cadena con unidades
        especificas. Ej. 1K -> 1024'''

    units = {'K': 1024, 'M': 1048576, 'G': 1073741824, 'T': 1099511627776}

    if (decode_me.strip()[-1] in ['k', 'K', 'm', 'M', 'g', 'G', 't', 'T']):
        return int(decode_me.strip()[:-1]) * units[decode_me.strip().upper()[-1]]
    else:
        print('F unit Expected [K,M,G,T]')
        exit()

if __name__ == "__main__":

    conf = get_config(argv[1]) # Lee la configuracion del JSON

    ### Variables Globales ###

    magic_number = {'exe': b'\x4d\x5a', 'zip': b'\x50\x4B\x03\x04',
                    'png': b'\x89\x50\x4E\x47', 'jpg': b'\xFF\xD8',
                    'mp3': b'\x49\x44\x33'} # Guarda todos los numeros magicos utilizados
    curr_file_type = None # Para llevar control de que tipo de archivo estamso recuperando
    counter = None # Contador para ver cuantos bytes hemos escrito
    curr_state = "start" # Para la maquina de estados
    next_state = "start" # Para la maquina de estados

    ### Maquina de Estados ###

    # Se abre en modo lectura el archivo del cual queremos recuperar archivos
    with open(argv[2], 'rb') as disk:

        while True:

            curr_state = next_state

            if curr_state == "start": # Revision de Estado
               
                curr_byte = disk.read(1)
                
                if curr_byte == b'\x4D' and conf['exe'][0] == True:
                    next_state = "exe_4D"
                elif curr_byte == b'\x50' and conf['zip'][0] == True:
                    next_state = "zip_50"
                elif curr_byte == b'\x89' and conf['png'][0] == True:
                    next_state = "png_89"
                elif curr_byte == b'\xFF' and conf['jpg'][0] == True:
                    next_state = "jpg_FF"
                elif curr_byte == b'\x49' and conf['mp3'][0] == True:
                    next_state = "mp3_49"
                elif curr_byte == b'': # if EOF is reached break the while
                    break
                else:
                    next_state = "start"

            elif curr_state == "exe_4D": # Revision de Estado

                curr_byte = disk.read(1)
                if curr_byte == b'\x5A':
                    print('exe')
                    next_state = "craft_file"
                    curr_file_type = "exe"
                else:
                    disk.seek(-1, 1)
                    next_state = "start"

            elif curr_state == "zip_50": # Revision de Estado

                curr_byte = disk.read(3)
                if curr_byte == b'\x4B\x03\x04':
                    print('zip')
                    next_state = "craft_file"
                    curr_file_type = "zip"
                else:
                    disk.seek(-3, 1)
                    next_state = "start"

            elif curr_state == "png_89": # Revision de Estado

                curr_byte = disk.read(3)
                if curr_byte == b'\x50\x4E\x47':
                    print('png')
                    next_state = "craft_file"
                    curr_file_type = "png"
                else:
                    disk.seek(-3, 1)
                    next_state = "start"

            elif curr_state == "jpg_FF": # Revision de Estado
                
                curr_byte = disk.read(1)
                if curr_byte == b'\xD8':
                    print('jpg')
                    next_state = "craft_file"
                    curr_file_type = "jpg"
                else:
                    disk.seek(-1, 1)
                    next_state = "start"

            elif curr_state == "mp3_49": # Revision de Estado

                curr_byte = disk.read(2)
                if curr_byte == b'\x44\x33':
                    print('mp3')
                    next_state = "craft_file"
                    curr_file_type = "mp3"
                else:
                    disk.seek(-2, 1)
                    next_state = "start"

            elif curr_state == "craft_file": # Revision de Estado

                counter = units_to_bytes(conf[curr_file_type][1]) if conf[curr_file_type][1] != '' else conf['default']
                
                with open(str(time()).replace('.', '_') + '.' + curr_file_type, 'wb') as curr_file:
                    curr_file.write(magic_number[curr_file_type])

                    if curr_file_type in ['exe', 'mp3']:

                            curr_file.write(disk.read(counter))

                    elif curr_file_type in ['zip', 'png', 'jpg']:

                        written_bytes = 0

                        if conf[curr_file_type][1] != '': # if a size was specified
                            curr_file.write(disk.read(counter))
                        else: # if no size was specified go till u find ending bytes
                            while True:
                                
                                if written_bytes == 1024*1024*20:
                                    print('Emergency Break')
                                    break

                                curr_byte = disk.read(1)

                                if curr_file_type == 'zip' and curr_byte == b'\x50':
                                    tmp_bytes = disk.read(3)
                                    if tmp_bytes == b'\x4B\x05\x06':
                                        curr_file.write(b'\x50\x4B\x05\x06')
                                        break
                                    else:
                                        disk.seek(-3, 1)
                                        curr_file.write(curr_byte)
                                        written_bytes += 1
                                elif curr_file_type == 'png' and curr_byte == b'\x49':
                                    tmp_bytes = disk.read(3)
                                    if tmp_bytes == b'\x45\x4E\x44':
                                        curr_file.write(b'\x49\x45\x4E\x44')
                                        break
                                    else:
                                        disk.seek(-3, 1)
                                        curr_file.write(curr_byte)
                                        written_bytes += 1
                                elif curr_file_type == 'jpg' and curr_byte == b'\xff':
                                    tmp_bytes = disk.read(1)
                                    if tmp_bytes == b'\xd9':
                                        curr_file.write(b'\xff\xd9')
                                        break
                                    else:
                                        disk.seek(-1, 1)
                                        curr_file.write(curr_byte)
                                        written_bytes += 1
                                else:
                                    curr_file.write(curr_byte)
                                    written_bytes += 1

                next_state = "start"

            else: # Revision de Estado
                print('404 State Not Found! Something Went Wrong')
                exit()