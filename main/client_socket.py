from __future__ import annotations

import logging
from json import JSONDecodeError
from typing import Optional

import click as click
from server_socket import generate_socket, set_socket_settings
from datetime import datetime
import json
import log.client_log_config

logger = logging.getLogger('app.client')


def send_message(client_socket) -> None:
    msg = {
        # "action": "presence",
        "time": datetime.timestamp(datetime.now()),
        "type": "status",
        "user": {
                "account_name": "Tritium",
                "status": "Yep, I am here!"
        }
    }
    json_msg = json.dumps(msg)
    client_socket.send(json_msg.encode('utf-8'))


def receive_server_message(client_socket) -> bytes:
    server_answer = client_socket.recv(1024)
    return server_answer


def parse_server_message(server_answer) -> Optional[dict]:
    try:
        server_answer = json.loads(server_answer.decode('utf-8'))
        return server_answer
    except JSONDecodeError:
        logger.error('Not available to decode server answer')
        return None


@click.command()
@click.option('--addr', '-a', help='IP address of server')
@click.option('--port', '-p', default=7777, help='TCP-port of server')
def run(addr: str, port: int) -> None:
    """
    Create simple client socket.
    Provide optionally TCP port and IP address of server.
    """
    client_socket = generate_socket()
    set_socket_settings(client_socket)
    logger.info(f'Try to connect to server {addr}:{port}')
    client_socket.connect((addr, port))
    send_message(client_socket)
    server_answer = receive_server_message(client_socket)
    server_answer = parse_server_message(server_answer)
    if server_answer:
        logger.info(f'Receive answer from server: {server_answer}')
    client_socket.close()


if __name__ == '__main__':
    run()
