from __future__ import annotations

import inspect
import logging
import threading
import time
from functools import wraps
from json import JSONDecodeError
from typing import Optional

import click as click
from server_socket import generate_socket, set_socket_settings
from datetime import datetime
import json
import log.client_log_config

logger = logging.getLogger('app.client')


class Log:
    def __init__(self, logger):
        self.logger = logger

    def __call__(self, func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            logger.info(
                'Function %s was called with args: %s and kwargs: %s',
                func.__name__,
                args,
                kwargs
            )
            logger.info(
                'Function %s was called from %s',
                func.__name__,
                inspect.stack()[1][3]
            )
            result = func(*args, **kwargs)
            return result
        return wrapper


def help_text():
    print('Поддерживаемые команды:')
    print('message - отправить сообщение. Кому и текст будет запрошены отдельно.')
    print('help - вывести подсказки по командам')
    print('exit - выход из программы')


def user_actions(socket, username):
    print(help_text())
    while True:
        command = input('Введите команду: ')
        if command == 'message':
            send_user_message(socket, username)
        elif command == 'help':
            print(help_text())
        elif command == 'exit':
            send_exit_message(socket, username)
            print('Завершение соединения.')
            logger.info('Завершение работы по команде пользователя.')
            time.sleep(0.5)
            break
        else:
            print('Команда не распознана, попробойте снова. help - вывести поддерживаемые команды.')


@Log(logger)
def send_client_message(client_socket, message) -> None:
    json_msg = json.dumps(message)
    client_socket.send(json_msg.encode('utf-8'))


def send_presence_message(client_socket, username) -> None:
    msg = {
        "action": "presence",
        "time": datetime.timestamp(datetime.now()),
        "type": "status",
        "user": {
                "account_name": username,
                "status": "Yep, I am here!"
        }
    }
    send_client_message(client_socket, msg)


def send_chat_message(client_socket, username, message) -> None:
    msg = {
        "action": "msg",
        "time": datetime.timestamp(datetime.now()),
        "to": "#room_name",
        "from": username,
        "message": message
    }
    send_client_message(client_socket, msg)


def send_user_message(client_socket, username="Guest") -> None:
    to_user = input('Введите получателя сообщения: ')
    message = input('Введите сообщение для отправки: ')
    msg = {
        "action": "msg",
        "time": datetime.timestamp(datetime.now()),
        "to": to_user,
        "from": username,
        "message": message
    }
    send_client_message(client_socket, msg)


def send_exit_message(socket, username="Guest"):
    msg = {
        "action": "exit",
        "time": datetime.timestamp(datetime.now()),
        "from": username,
    }
    send_client_message(socket, msg)


def get_server_message(socket):
    while True:
        try:
            data = parse_server_message(receive_server_message(socket))
            show_answer(data)
        except Exception as e:
            logger.critical(e)


@Log(logger)
def receive_server_message(client_socket) -> bytes:
    server_answer = client_socket.recv(1024)
    return server_answer


@Log(logger)
def parse_server_message(server_answer) -> Optional[dict]:
    try:
        server_answer = server_answer.decode('utf-8')
        if '}{' in server_answer:
            server_answer = server_answer.replace('}{', '} , {').split(" , ")
            server_answer = [json.loads(answer) for answer in server_answer]
        return server_answer
    except JSONDecodeError as e:
        logger.error('Not available to decode server answer %s', e)
        return None


def show_answer(server_answer) -> None:
    print(server_answer)


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

    username = input('Ваше имя: ')
    send_presence_message(client_socket, username)
    data = client_socket.recv(1024)
    logger.info(data.decode('utf-8'))

    user_interface = threading.Thread(target=user_actions, args=(client_socket, username))
    user_interface.daemon = True
    user_interface.start()

    receiver = threading.Thread(target=get_server_message, args=(client_socket,))
    receiver.daemon = True
    receiver.start()


if __name__ == '__main__':
    run()
