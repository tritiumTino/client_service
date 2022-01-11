from __future__ import annotations

import inspect
import logging
from functools import wraps
from socket import socket, AF_INET, SOCK_STREAM, SO_REUSEADDR, SOL_SOCKET
from json import JSONDecodeError
from typing import Optional

import click as click
import json

import log.server_log_config

logger = logging.getLogger('app.server')


def log(logger):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            logger.info(
                'Function %s was called with args: %s',
                func.__name__,
                str(*args) + str(**kwargs),
            )
            logger.info(
                'Function %s was called from %s',
                func.__name__,
                inspect.stack()[1][3]
            )
            result = func(*args, **kwargs)
            return result
        return wrapper
    return decorator


def generate_socket():
    return socket(AF_INET, SOCK_STREAM)


def set_socket_settings(socket_obj) -> None:
    socket_obj.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)


@log(logger)
def receive_client_message(client_socket) -> bytes:
    data = client_socket.recv(1024)
    return data


@log(logger)
def form_answer(data: bytes) -> Optional[bytes]:
    bad_request = json.dumps(
            {
                "response": 500,
                "alert": 'What are you doing?'
            }
        ).encode('utf-8')

    try:
        client_data = json.loads(data.decode('utf-8'))
    except JSONDecodeError:
        logger.error('Unavailable format of client message')
        return bad_request

    try:
        client_action = client_data['action']
    except KeyError:
        logger.error('No action in client message')
        return bad_request

    if client_action == 'presence':
        server_msg = json.dumps(
            {
                "response": 200,
                "alert": 'I see you'
            }
        ).encode('utf-8')
        return server_msg
    else:
        return bad_request


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
        logger.info(f'Connection from {client_addr}')
        client_data = receive_client_message(client_socket)
        logger.info(f'Receive message from {client_addr}')
        server_msg = form_answer(client_data)
        send_message(client_socket, server_msg)
        client_socket.close()


if __name__ == '__main__':
    run()
