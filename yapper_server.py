import socket, sys, select

from yapper_server_class import Server

arguments = len(sys.argv) - 1
if arguments == 1:
    hostAddr = sys.argv[1]
else:
    hostAddr = '127.0.0.1'

s = Server()
s.run(hostAddr)
