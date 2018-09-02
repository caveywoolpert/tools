import socket
import select
import ConfigParser
from threading import Thread

HOST = "127.0.0.1"
SERVER_SOCKETS = []
BACKENDS = None


class Client(Thread):
    def __init__(self, sock, addr, status):
        Thread.__init__(self)
        self.sock = sock
        self.addr = addr
        self.status = status
        self.start()

    @staticmethod
    def readlines(sock, recv_buffer=4096, delim='\n'):
        buffer = ''
        data = True
        while data:
            data = sock.recv(recv_buffer)
            buffer += data

            while buffer.find(delim) != -1:
                line, buffer = buffer.split('\n', 1)
                yield line
        return

    def run(self):
        for line in self.readlines(self.sock):
            print line
        self.sock.send("%s\n" % self.status)
        self.sock.shutdown(socket.SHUT_WR)


CONFIG = ConfigParser.ConfigParser()
try:
    CONFIG.readfp(open('agent.conf'))
    BACKENDS = CONFIG.items('Backends')
except Exception as err:
    print err.message
    print "Can't read the config agent.conf"
for backend in BACKENDS:
    serversocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_port = CONFIG.get('Backends', backend.__getitem__(0))
    serversocket.bind((HOST, int(server_port)))
    serversocket.listen(1)
    SERVER_SOCKETS.append(serversocket)

print 'server started and listening'
while True:
    readable, _, _ = select.select(SERVER_SOCKETS, [], [])
    ready_server = readable[0]
    connection, address = ready_server.accept()
    server_socket = str(connection.getsockname()[1])
    Client(connection, address, CONFIG.get('Statuses', server_socket))
