import os
from subprocess import Popen, CREATE_NEW_CONSOLE

path = os.path.abspath("client_socket.py")


def create_clients(count: int):
    for i in range(count):
        with Popen(["python", path], creationflags=CREATE_NEW_CONSOLE) as client:
            print(f'Client #{i} is running with {client.pid} pid')
