import argparse
import hashlib
import socket
import struct
import time
import sys
from tqdm import tqdm
import os
from datetime import datetime

parser = argparse.ArgumentParser(
    description="File transfer UDP server"
)

parser.add_argument(
    "--file", default=1, type=int, help="file id to be send"
)

parser.add_argument(
    "--num_clients", default=1, type=int, help="number of conections to receive",
)

args = parser.parse_args()

args_dict = vars(args)
print("Argument list to program")
print(
    "\n".join(["--{0} {1}".format(arg, args_dict[arg]) for arg in args_dict])
)
print("\n\n")

multicast_group = ( '224.3.29.71', 10000 )

# Create the datagram socket
sock = socket.socket( socket.AF_INET, socket.SOCK_DGRAM )

# Set a timeout so the socket does not block indefinitely when trying
# to receive data.
# sock.settimeout( 0.2 )

# Set the time-to-live for message to 1 so they don't go past the
# the local network segment
ttl = struct.pack( 'b', 1 )
sock.setsockopt( socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, ttl)

buf = 1024
file_dict = {
    1: './data/file1.bin',
    2: './data/file2.bin'
}
file_name = file_dict[args.file]

try:
    now = datetime.now()
    dt_string = now.strftime("%d-%m-%Y---%H-%M-%S")
    log_name = "log"+dt_string
    log = open(log_name+".txt", "x")
    log.write("Prueba con fecha y hora de " + dt_string + "\n")
    tam = os.path.getsize(file_name)
    log.write("Archivo " + file_name + " de tamaño " + str(tam) + "\n")


    # Send filename to the multicast group
    sock.sendto(file_name.encode('utf-8'), multicast_group)
    print("Sending %s ..." % file_name)

    # Send file hash to the multicast group
    with open(file_name, "rb") as f:
        file_hash = hashlib.md5(f.read()).hexdigest()
    sock.sendto(file_hash.encode('utf-8'), multicast_group)

    # Look for responses from all recipients
    print( 'Esperando notificaciones de que los clientes están listos para recibir el archivo' )
    count = 0
    while True and count < args.num_clients:
        data, server = sock.recvfrom(1024)
        log.write("Llego cliente #"+str(count) + "\n")
        print( 'Recibido "%s" de "%s"' % ( data, server ))
        count += 1
    count = 0
    
    # Send data to the multicast group
    f = open(file_name, "rb")
    data = f.read(buf)
    pbar = tqdm(total=int(os.path.getsize(file_name)/buf))
    start = time.time()
    while(data):
        if(sock.sendto(data, multicast_group)):
            #  log.write("Enviando paquete " + str(count))
            count+=1
            data = f.read(buf)
            pbar.update(1)
    end = time.time()
    log.write("Tiempo en transferir " + str(end - start) + " segundos\n")
    f.close()
    pbar.close()

    # Look for responses from all recipients
    print( 'Esperando respuesta' )
    count = 0
    while True and count < args.num_clients:
        data, server = sock.recvfrom(1024)
        print( 'Recibido "%s" de "%s"' % ( data, server ))
        log.write('Cliente "%s" responde con integridad "%s"\n' % (count,data))
        count += 1
    log.close()
finally:
    print( 'Socket cerrado' )
    sock.close()
