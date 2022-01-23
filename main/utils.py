from json import JSONDecodeError
from socket import socket, AF_INET, SOCK_STREAM, SO_REUSEADDR, SOL_SOCKET
from typing import Mapping, Any, Optional
import json

JSONType = Mapping[str, Any]


class ServerClientMixin:
    def __init__(self, addr: str, port: int, logger):
        self.addr = addr
        self.port = port
        self.logger = logger
        self.sock = self.get_socket()
        self.encoding = 'utf-8'

    @staticmethod
    def get_socket():
        sock = socket(AF_INET, SOCK_STREAM)
        sock.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
        return sock

    def parse_msg(self, msg: bytes) -> str:
        return msg.decode(self.encoding)

    def send_msg(self, msg: JSONType) -> None:
        message = json.dumps(msg).encode(self.encoding)
        self.sock.send(message)
        self.logger.info('Send message %s', msg)

    def receive_msg(self) -> Optional[str]:
        try:
            msg = self.parse_msg(self.sock.recv(1024))
        except JSONDecodeError as e:
            msg = None
            self.logger.error('Not available to decode server answer %s', e)
        return msg
