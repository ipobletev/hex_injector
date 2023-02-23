from enum import Enum
import os
import argparse

# Example to use
# python hex_injector.py -r -dir .pio/build/wiscore_rak4631/firmware.hex -addr 0x64b24 -data 25
# python hex_injector.py -dir .pio/build/wiscore_rak4631/firmware.hex -addr 0x64b24 -data 000102030405060708090A0B0C0DAAAAAAAAAAAAAAAAAAAAAAAAAAAABB
# python hex_injector.py -r -dir .pio/build/wiscore_rak4631/firmware.hex -addr 0x64b24 -data 25

# Hex record type
class record_type(Enum):
    data                    = "00",
    end_of_line             = "01",
    ext_seg_addr            = "02",
    start_seg_addr          = "03",
    extended_linear_addr    = "04",
    start_linear_addr       = "05"

# Calculatee checksum from hex file
def CheckSum8_2complement(string_hex):
    # Convertir string hex en lista de bytes
    bytes_hex = bytes.fromhex(string_hex)
    
    # Sumar los valores de cada byte
    suma = sum(bytes_hex)
    
    # Tomar el complemento a 2
    complemento = (~suma + 1) & 0xFF
    
    # Convertir a string hex y tomar los últimos 2 caracteres
    if(complemento <16):
        checksum = hex(complemento)[-1:].upper()
        checksum = checksum.zfill(2)
    else:
        checksum = hex(complemento)[-2:].upper()
    
    # Agregar un cero a la izquierda si el string tiene solo un dígito
    
    
    return checksum

def hex_read(file_path, target_address, lend_toread):
    
    with open(file_path, 'r+') as f:
        # Leer los datos del archivo y almacenarlos en una lista
        data = f.readlines()

        # Buscar la dirección específica en la lista
        for i, line in enumerate(data):

            recordtype = line[7:9]

            if((recordtype == record_type.ext_seg_addr.value[0])):
                
                byte_count = int(line[1:3], 16)                
                data_addr_segment = int(line[9:13],16)
                address_offset = data_addr_segment * 16
                # print(hex(address_offset))

            # Extraer los campos de la línea
            if(recordtype == record_type.data.value[0]):

                addr_data = int(line[3:7],16)
                address = address_offset + addr_data

                # print(hex(address),i,hex(addr_data),hex(address_offset))
                # print(line)
                target_address_int = int(target_address[2:],16)
                if(target_address_int>=address and target_address_int<=address+16):
                    
                    print("Physical addr to read: ", hex(address) ," in ", hex(target_address_int))

                    # Offset address to write in the first block
                    offset_address = (target_address_int - address)*2
                        
                    # Calculo cuantos bloques tengo que escribir
                    size_data = int(lend_toread)*2
                    block_cont = int(((offset_address+size_data)/(16*2))+1)
                    cont_data = size_data
                    last_data_readed=0
                    data_read_buf=""
                    # Read for each block
                    for itera in range(block_cont):
                        
                        print("---------- line", i+itera+1," physical addr: ",hex(address+(16*itera)))
                        #fix data to write in this bock. offset is used only one time.
                        if((cont_data + offset_address) > (16*2)):
                            data_toread_thisbock = (16*2) - offset_address

                        elif((cont_data + offset_address) <= (16*2)):                       
                            data_toread_thisbock = cont_data

                        print("From: ",data[i+itera][:-1])

                        if(itera == 0):            
                            data_read_buf += data[i+itera][9+offset_address:9+offset_address+data_toread_thisbock] 
                        else: 
                            data_read_buf += data[i+itera][9:9+data_toread_thisbock]

                        # Update cont data and value wrote
                        cont_data -= data_toread_thisbock
                        last_data_readed+= int(data_toread_thisbock)
                        offset_address=0

                        if(cont_data <= 0):
                            print("\nData:",data_read_buf)
                            break
    
# Inject data
def hexinjector_tofile(file_path, target_address, new_value):

    # Abrir el archivo .hex en modo lectura y escritura
    with open(file_path, 'r+') as f:
        # Leer los datos del archivo y almacenarlos en una lista
        data = f.readlines()

        # Buscar la dirección específica en la lista
        for i, line in enumerate(data):

            recordtype = line[7:9]

            if((recordtype == record_type.ext_seg_addr.value[0])):
                
                byte_count = int(line[1:3], 16)                
                data_addr_segment = int(line[9:13],16)
                address_offset = data_addr_segment * 16
                # print(hex(address_offset))

            # Extraer los campos de la línea
            if(recordtype == record_type.data.value[0]):

                addr_data = int(line[3:7],16)
                address = address_offset + addr_data

                # print(hex(address),i,hex(addr_data),hex(address_offset))
                # print(line)
                target_address_int = int(target_address[2:],16)
                if(target_address_int>=address and target_address_int<=address+16):
                    
                    print("Physical addr to work: ", hex(address) ," in ", hex(target_address_int))
                    print("Change data to:")

                    # Offset address to write in the first block
                    offset_address = (target_address_int - address)*2
                        
                    # Calculo cuantos bloques tengo que escribir
                    size_data = len(new_value)
                    block_cont = int(((offset_address+size_data)/(16*2))+1)

                    cont_data = size_data
                    last_value_wrote=0

                    # Armo trama para cada bloque
                    for itera in range(block_cont):
                        
                        print("---------- line", i+itera+1," physical addr: ",hex(address+(16*itera)))
                        #fix data to write in this bock. offset is used only one time.
                        if((cont_data + offset_address) > (16*2)):
                            data_write_thisbock = (16*2) - offset_address

                        elif((cont_data + offset_address) <= (16*2)):                       
                            data_write_thisbock = cont_data

                        # Equivalent to line, but with the others data line
                        # data[i+itera]
                        # Armo trama para el bloque  
                        if(itera == 0):            
                            new_data = data[i+itera][1:9+offset_address] + new_value[:int(data_write_thisbock)] + data[i+itera][9+offset_address+int(data_write_thisbock):-3]
                        else: 
                            new_data = data[i+itera][1:9] + new_value[last_value_wrote:last_value_wrote+int(data_write_thisbock)] + data[i+itera][9+int(data_write_thisbock):-3]
                        new_checksum = CheckSum8_2complement(new_data)    
                        new_data += new_checksum
                        new_data = ":" + new_data + "\n"

                        print("From: ",data[i+itera][:-1])
                        print("To  : ",new_data)

                        # Store the new data
                        data[i+itera] = new_data

                        # Update cont data and value wrote
                        last_value_wrote += int(data_write_thisbock)
                        cont_data -= data_write_thisbock
                        offset_address=0

                        if(cont_data <= 0):
                            break

                    break

    # Write in hex file
    with open(file_path, "w") as archivo:
        archivo.writelines(data)            

def parse_opt():
    parser = argparse.ArgumentParser()
    ### For batch programming
    parser.add_argument('-w', action="store_true", help="Write batch to address")
    parser.add_argument('-r', action="store_true", help="Read batch from address")
    parser.add_argument('-dir', type=str, default='',help="Path to hexfile ")
    parser.add_argument("-addr", type=str, default='',help="Physical address (real in mcu) to write")
    parser.add_argument("-data", type=str, default='',help="Data to inject, in w is the data to inject, in read is the cont hex data to read")

    return parser.parse_args()

if __name__ == "__main__":

    os.system("cls")

    opt =  parse_opt()
     
    print("\n######################################\n")

    if(opt.w):
        hexinjector_tofile(opt.dir,opt.addr,opt.data)
    elif(opt.r):
        hex_read(opt.dir,opt.addr,opt.data)

    print("\n######################################\n")
    print("Programa Finalizado")
    print("\n######################################\\n")

