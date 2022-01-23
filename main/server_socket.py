from __future__ import annotations

import inspect
import logging
from functools import wraps
from collections import OrderedDict
from select import select
from json import JSONDecodeError
from typing import Tuple

import click as click
import json
from utils import ServerClientMixin

import log.server_log_config

logger = logging.getLogger('app.server')
to_monitor: list = []


class ServerSocket(ServerClientMixin):
    def __init__(self, *args) -> None:
        super().__init__(*args)
        self.to_monitor = []

    def set_settings(self) -> None:
        self.sock.bind((self.addr, self.port))
        self.sock.listen(5)
        self.sock.settimeout(0.2)

    def accept_connection(self) -> None:
        client_socket, client_addr = self.sock.accept()
        logger.info(f'Connection from {client_addr}')
        self.to_monitor.append(client_socket)


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


def form_answer(data: str) -> Tuple[bytes, bool, bool]:
    is_mass_msg = False
    is_user_msg = False
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
        return server_answer, is_mass_msg, is_user_msg

    try:
        client_action = client_data['action']
        to_user = client_data.get("to", False)
    except KeyError:
        logger.error('No action in client message')
        return server_answer, is_mass_msg, is_user_msg

    if client_action == 'presence':
        server_answer = json.dumps(
            {
                "response": 200,
                "alert": 'I see you'
            }
        ).encode('utf-8')

    elif client_action == 'msg' and "#" not in to_user:
        is_mass_msg = False
        is_user_msg = True
        server_answer = json.dumps(
            {
                "response": 200,
                "from": client_data["from"],
                "to": to_user,
                "message": client_data.get("message")
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

    return server_answer, is_mass_msg, is_user_msg


def write_responses(requests, w_clients):
    for sock in w_clients:
        if sock in requests:
            try:
                resp, is_mass_msg, is_user_msg = form_answer(requests[sock])
                logger.info("Answer: %s", resp.decode('utf-8'))
                if not is_mass_msg and not is_user_msg:
                    sock.send(resp)
                elif not is_mass_msg:
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
    
    server_socket = ServerSocket(addr, port, logger)
    server_socket.set_settings()
    while True:
        try:
            server_socket.accept_connection()
        except OSError as e:
            pass  # timeout вышел
        finally:
            wait = 10
            r = []
            w = []
            try:
                r, w, e = select(server_socket.to_monitor, server_socket.to_monitor, [], wait)
            except:
                pass

            requests = read_requests(r)
            if requests:
                write_responses(requests, w)


if __name__ == '__main__':
    run()
