import hashlib
import socket
import struct
import select
import sys
import os


multicast_group = '224.3.29.71'
server_address = ( '', 10000 )
timeout = 0.2

# Create the socket
sock = socket.socket( socket.AF_INET, socket.SOCK_DGRAM )

# Bind to the server address
sock.bind( server_address )

# Tell the operating system to add the socket to the multicast group
# on all interfaces
group = socket.inet_aton( multicast_group )
mreq = struct.pack( '4sl', group, socket.INADDR_ANY )
sock.setsockopt( socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, mreq )

while True:
    data, addr = sock.recvfrom(1024)
    data = data.decode("utf-8")
    if data:
        print("File name:" + data)
        file_name = os.path.basename(data)

    f = open(file_name, 'wb')

    data, addr = sock.recvfrom(1024)
    data = data.decode("utf-8")
    if data:
        print("Hash:" + data)
        file_hash = data.strip()

    sock.sendto('OK'.encode('utf-8'), addr)

    print('Receiving...')
    while True:
        ready = select.select([sock], [], [], timeout)
        if ready[0]:
            data, addr = sock.recvfrom(1024)
            f.write(data)
            
        else:
            f.close()
            print("%s Finish!" % file_name)
            print( 'Received %s bytes from %s' % (os.path.getsize(file_name), addr))
            break
    
    # Send file hash to the multicast group
    with open(file_name, "rb") as f:
        if file_hash == hashlib.md5(f.read()).hexdigest():
            sock.sendto('1'.encode('utf-8'), addr)
        else:
            sock.sendto('0'.encode('utf-8'), addr)
    break  