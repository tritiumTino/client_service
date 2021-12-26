from __future__ import annotations
import socket
import click as click
import json


def generate_socket():
    return socket.socket(socket.AF_INET, socket.SOCK_STREAM)


def set_socket_settings(socket_obj) -> None:
    socket_obj.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)


def receive_client_message(client_socket, client_addr) -> bytes:
    data = client_socket.recv(1024)
    print(f'Receive message from {client_addr}')
    return data


def form_answer(data: bytes) -> bytes:
    client_data = json.loads(data.decode('utf-8'))
    client_action = client_data['action']

    if client_action == 'presence':
        server_msg = json.dumps(
            {
                "response": 200,
                "alert": 'I see you'
            }
        ).encode('utf-8')
    else:
        server_msg = json.dumps(
            {
                "response": 500,
                "alert": 'What are you doing?'
            }
        ).encode('utf-8')

    return server_msg


def send_message(client_socket, server_msg) -> None:
    client_socket.send(server_msg)


@click.command()
@click.option('--addr', '-a', default='', help='IP address to listen to')
@click.option('--port', '-p', default=7777, help='TCP-port')
def run(addr: str, port: int) -> None:
    """
    Create simple server socket.
    Provide optionally TCP port bind with and IP address to listen to.
    """
    server_socket = generate_socket()
    set_socket_settings(server_socket)
    server_socket.bind((addr, port))
    server_socket.listen()

    while True:
        client_socket, client_addr = server_socket.accept()
        print(f'Connection from {client_addr}')
        client_data = receive_client_message(client_socket, client_addr)
        server_msg = form_answer(client_data)
        send_message(client_socket, server_msg)
        client_socket.close()


if __name__ == '__main__':
    run()
