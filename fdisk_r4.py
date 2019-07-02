import json
from sys import argv

def get_config(json_config_file):
    with open(json_config_file, 'r') as config_file:
        return json.load(config_file)

def units_to_sectors(decode_me):

    ''' Regresa el numero de sectores que va a abarcar la particion (0) o el ultimo
        sector deseado (1). '''

    units = {'K': 1024, 'M': 1048576, 'G': 1073741824, 'T': 1099511627776}
    sector_size = 512

    if('+' in decode_me):
        if (decode_me.strip()[-1] in ['k', 'K', 'm', 'M', 'g', 'G', 't', 'T']):
            return (0, int((int(decode_me.strip()[1:-1]) * units[decode_me.strip().upper()[-1]]) / sector_size))
        else:
            return (1, int(decode_me.strip()[1:]))
    else:
        print("Error character \'+\' expected in " + decode_me)
        exit()

def big_to_little(number, byte_no):

    hex_num = hex(number)[2:]

    if len(hex_num) % 2 != 0:
        hex_num = '0' + hex_num

    if len(hex_num) / 2 <= byte_no:
        hex_num = '00' * (byte_no - len(hex_num) // 2) + hex_num

    hex_num = [bytes([int(hex_num[i:i+2], 16)]) for i in range(0, len(hex_num), 2)][-1::-1]

    return hex_num


def craft_pte(part_config, current_sector, end_sector):

    ''' Construye una entrada para la tabla de particiones regresa un arreglo
        de 16 bytes listos para ser escritos en la tabla de particiones. '''

    entry = []

    entry.append(b'\x00') # Byte 0
    entry.extend([b'\xff', b'\xff', b'\xff'][-1::-1]) # Bytes 1-3
    entry.extend(big_to_little(int(str(part_config[0]), 16), 1))
    entry.extend([b'\xff', b'\xff', b'\xff'][-1::-1]) # Bytes 5-7

    if part_config[1] == 'default':
        entry.extend(big_to_little(current_sector, 4)) # Bytes 5-7
    else:
        entry.extend(big_to_little(part_config[1], 4)) # Bytes 5-7
    
    if part_config[2] == 'default':
        entry.extend(big_to_little(end_sector - current_sector, 4))
        update_curr_sect = -1
    else:
        sectors = units_to_sectors(part_config[2])
        if sectors[0] == 0: # If size is specified
            entry.extend(big_to_little(sectors[1], 4))
            update_curr_sect = current_sector + sectors[1]
        else: # If final sector specified
            entry.extend(big_to_little(sectors[1] - current_sector, 4))
            update_curr_sect = sectors[1] + 1

    return(entry, update_curr_sect)


if __name__ == "__main__":

    config = get_config(argv[2])

    current_sector = 2048
    end_sector = units_to_sectors(config['size'])[1] - 1

    with open(argv[1], 'wb') as disk:
        
        disk.write(bytearray([0]*(units_to_sectors(config['size'])[1]*512))) # Format the file
        disk.seek(446) # Just after boot code ends

        for partition in [config['first'], config['second'], config['third'], config['extended']]:

            current_partition = craft_pte(partition, current_sector, end_sector)
            current_sector = current_partition[1]

            for byte in current_partition[0]:
                disk.write(byte)
        
        disk.write(b'\x55')
        disk.write(b'\xaa')