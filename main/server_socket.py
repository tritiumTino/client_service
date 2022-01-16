from __future__ import annotations

import inspect
import logging
from functools import wraps
from collections import OrderedDict
from socket import socket, AF_INET, SOCK_STREAM, SO_REUSEADDR, SOL_SOCKET, SocketType
from select import select
from json import JSONDecodeError
from typing import Optional, Tuple

import click as click
import json

import log.server_log_config

logger = logging.getLogger('app.server')
to_monitor: list = []


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


def set_socket_settings(socket_obj: SocketType) -> None:
    socket_obj.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)


def accept_connection(server_socket: SocketType) -> None:
    client_socket, client_addr = server_socket.accept()
    logger.info(f'Connection from {client_addr}')
    to_monitor.append(client_socket)


def read_requests(r_clients):
    responses = OrderedDict()

    for sock in r_clients:
        try:
            data = sock.recv(1024).decode('utf-8')
            responses[sock] = data
        except Exception as e:
            logger.warning(e)
            to_monitor.remove(sock)
    return responses


@log(logger)
def form_answer(data: str) -> Tuple[bytes, bool]:
    is_mass_msg = False
    server_answer = json.dumps(
            {
                "response": 500,
                "alert": 'What are you doing?'
            }
        ).encode('utf-8')

    try:
        client_data = json.loads(data)
    except JSONDecodeError:
        logger.error('Unavailable format of client message')
        return server_answer, is_mass_msg

    try:
        client_action = client_data['action']
    except KeyError:
        logger.error('No action in client message')
        return server_answer, is_mass_msg

    if client_action == 'presence':
        server_answer = json.dumps(
            {
                "response": 200,
                "alert": 'I see you'
            }
        ).encode('utf-8')

    elif client_action == 'msg':
        is_mass_msg = True
        server_answer = json.dumps(
            {
                "response": 200,
                "message": f'{client_data.get("from")}: {client_data.get("message")}'
            }
        ).encode('utf-8')

    return server_answer, is_mass_msg


def write_responses(requests, w_clients):
    for sock in w_clients:
        if sock in requests:
            try:
                resp, is_mass_msg = form_answer(requests[sock])
                logger.info("Answer: %s", resp.decode('utf-8'))
                if not is_mass_msg:
                    sock.send(resp)
                else:
                    for sock_to_write in w_clients:
                        if sock_to_write is not sock:
                            sock_to_write.send(resp)
            except Exception as e:
                logger.warning(e)
                sock.close()
                to_monitor.remove(sock)


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
    server_socket.listen(5)
    server_socket.settimeout(0.2)
    while True:
        try:
            client_socket, addr = server_socket.accept()
        except OSError as e:
            pass  # timeout вышел
        else:
            logger.info("Получен запрос на соединение от %s", addr)
            to_monitor.append(client_socket)
        finally:
            wait = 10
            r = []
            w = []
            try:
                r, w, e = select(to_monitor, to_monitor, [], wait)
            except:
                pass

            requests = read_requests(r)
            if requests:
                write_responses(requests, w)


if __name__ == '__main__':
    run()
