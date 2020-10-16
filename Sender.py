import socket
import struct
import sys

message = 'Mensaje En Multidifusión'
multicast_group = ( '224.3.29.71', 10000 )

# Create the datagram socket
sock = socket.socket( socket.AF_INET, socket.SOCK_DGRAM )

# Set a timeout so the socket does not block indefinitely when trying
# to receive data.
sock.settimeout( 0.2 )

# Set the time-to-live for message to 1 so they don't go past the
# the local network segment
ttl = struct.pack( 'b', 1 )
sock.setsockopt( socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, ttl )

try:

    # Send data to the multicast group
    print( 'Enviando "%s"' % message )

    sent = sock.sendto( message.encode( "ascii" ), multicast_group )

    # Look for responses from all recipients
    while True:
        print( 'Esperando respuesta' )
        try:
            data, server = sock.recvfrom( 16 )
        except socket.timeout:
            print( 'Time out, no se recibieron mas respuestas')
            break
        else:
            print( 'Recibido "%s" de "%s"' % ( data, server ))

finally:
    print( 'Socket cerrado' )
    sock.close()
