import socket
import threading
from queue import Queue

HEADER = 1024
HOST = 'localhost'
PORT = 5000
s = None

MAX_CONNECTIONS = 5

user_info = {}

# create a socket
def create_socket():
    try:
        global s
        s = socket.socket()
    except socket.error as msg:
        print('Socket creation error: ' + str(msg))

# bind the socket
def bind_socket():
    try:
        global PORT
        global HOST
        global s
        s.bind((HOST, PORT))
        s.listen(MAX_CONNECTIONS)
        print('Binding with the port ' + str(PORT))
    except socket.error as msg:
        print('Socket binding error: ' + str(msg) + 'Retrying...')
        bind_socket()

# accepting multiple client connections
def accepting_connections():
    global s
    while True:
        try:
            conn, add = s.accept()
            s.setblocking(1)  # prevents timeout

            t = threading.Thread(target=threaded_client, args=[conn, add])
            t.daemon = True
            t.start()

            print('Connection request accepted from IP ' + str(add[0]) + ' on port ' + str(add[1]))

        except socket.error as msg:
            print('Error in accepting connections: ' + str(msg))

    s.close()

# handling individual clients
def threaded_client(connection, address):

    name = None

    while not name:
        name = connection.recv(HEADER).decode('utf-8')

        if not name:
            connection.send(bytes('Server : Select a valid username.', 'utf-8'))
        else:
            user_info[address[1]] = [name, connection]
            break

    connection.send(bytes(f'Server : Welcome to the server {user_info[address[1]][0]}!', 'utf-8'))
    broadcast(address,'Joined The Chat!')

    while True:
        cmd = connection.recv(HEADER).decode('utf-8')
        print(cmd)
        broadcast(address, cmd)
        if cmd == 'exit':
            del user_info[address[1]]
            break

    connection.close()

# broadcast a message to clients
def broadcast(address, cmd):
    for x in user_info:
        try:
            if cmd == 'exit':
                if x == address[1]:
                    user_info[x][1].send(bytes(cmd, 'utf-8'))
                else:
                    user_info[x][1].send(bytes(f'{user_info[address[1]][0]} left the server!', 'utf-8'))
            else:
                if x != address[1]:
                    user_info[x][1].send(bytes(f'{user_info[address[1]][0]} : {cmd}', 'utf-8'))

        except socket.error as msg:
            print('Error in broadcasting message: ' + str(msg))

create_socket()
bind_socket()
accepting_connections()