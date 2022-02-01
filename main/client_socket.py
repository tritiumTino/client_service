from __future__ import annotations

import logging
import threading
import time

import click as click
from datetime import datetime
import log.client_log_config
from utils import ClientVerifier, ServerClientMixin

logger = logging.getLogger('app.client')


class ClientSocket(ServerClientMixin, metaclass=ClientVerifier):
    def __init__(self, addr: str, port: int, logger, username: str = "Guest") -> None:
        super().__init__(addr, port, logger)
        self.username = username

    def connect(self) -> None:
        self.logger.info(f'Try to connect to server {self.addr}:{self.port}')
        self.sock.connect((self.addr, self.port))
        self.send_presence_message()

    def send_presence_message(self) -> None:
        msg = {
            "action": "presence",
            "time": datetime.timestamp(datetime.now()),
            "type": "status",
            "user": {
                "account_name": self.username,
                "status": "Yep, I am here!"
            }
        }
        self.send_msg(msg)

    def send_user_message(self) -> None:
        to_user = input('Введите получателя сообщения: ')
        message = input('Введите сообщение для отправки: ')
        msg = {
            "action": "msg",
            "time": datetime.timestamp(datetime.now()),
            "to": to_user,
            "from": self.username,
            "message": message
        }
        self.send_msg(msg)

    def send_exit_message(self) -> None:
        msg = {
            "action": "exit",
            "time": datetime.timestamp(datetime.now()),
            "from": self.username,
        }
        self.send_msg(msg)
        self.logger.info('Завершение работы по команде пользователя.')
        time.sleep(0.5)

    @staticmethod
    def show_answer(server_answer) -> None:
        print(server_answer)

    def get_server_message(self):
        while True:
            try:
                data = self.receive_msg()
                self.show_answer(data)
            except Exception as e:
                self.logger.critical(e)

    def send_chat_message(self) -> None:
        to_chat = input('Введите получателя сообщения: ')
        message = input('Введите сообщение для отправки: ')
        msg = {
            "action": "msg",
            "time": datetime.timestamp(datetime.now()),
            "to": f"#{to_chat}",
            "from": self.username,
            "message": message
        }
        self.send_msg(msg)

    @staticmethod
    def help_text():
        print('Поддерживаемые команды:')
        print('message - отправить сообщение. Кому и текст будет запрошены отдельно.')
        print('help - вывести подсказки по командам')
        print('exit - выход из программы')

    def user_actions(self):
        self.help_text()
        while True:
            command = input('Введите команду: ')
            if command == 'message':
                self.send_user_message()
            elif command == 'help':
                self.help_text()
            elif command == 'exit':
                self.send_exit_message()
                break
            else:
                print('Команда не распознана, попробойте снова. help - вывести поддерживаемые команды.')


@click.command()
@click.option('--addr', '-a', default='localhost', help='IP address of server')
@click.option('--port', '-p', default=7777, help='TCP-port of server')
def run(addr: str, port: int) -> None:
    """
    Create simple client socket.
    Provide optionally TCP port and IP address of server.
    """
    username = input('Ваше имя: ')
    client_socket = ClientSocket(addr, port, logger, username)

    client_socket.connect()

    user_interface = threading.Thread(target=client_socket.user_actions)
    user_interface.daemon = True
    user_interface.start()
    user_interface.join()

    receiver = threading.Thread(target=client_socket.get_server_message)
    receiver.daemon = True
    receiver.start()
    receiver.join()


if __name__ == '__main__':
    run()
