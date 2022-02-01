import ipaddress
import platform
import subprocess
from json import JSONDecodeError
from socket import socket, AF_INET, SOCK_STREAM, SO_REUSEADDR, SOL_SOCKET
from typing import Mapping, Any, Optional, List, Dict
import json

from tabulate import tabulate

JSONType = Mapping[str, Any]


class ClientVerifier(type):
    def __init__(self, clsname, bases, clsdict):
        for key, value in clsdict.items():
            if key.startswith("__"):
                continue

            if hasattr(value, "__call__"):
                if value in ("listen", "accept"):
                    raise TypeError("Client socket must not have `listen` or `accept` methods")

        type.__init__(self, clsname, bases, clsdict)


class PortDescriptor:
    def __set_name__(self, owner, name):
        self._property_name = name

    def __set__(self, instance, value):
        if isinstance(value, int) and value >= 0:
            instance.__dict__[self._property_name] = value
        else:
            instance.__dict__[self._property_name] = 7777

    def __get__(self, instance, owner):
        if instance is None:
            return self
        return instance.__dict__[self._property_name]


class ServerClientMixin:
    port = PortDescriptor()

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


def ping(host) -> bool:
    param = '-n' if platform.system().lower() == 'windows' else '-c'
    command = ['ping', param, '1', host]

    return subprocess.call(command) == 0


def range_ping(host_from: str, host_to: str) -> Optional[Dict[ipaddress.IPv4Address, str]]:
    hosts_dict: Dict[ipaddress.IPv4Address, str] = {}
    try:
        host_from, host_to = ipaddress.ip_address(host_from), ipaddress.ip_address(host_to)
    except Exception as e:
        print(e)
    else:
        if host_from > host_to:
            return
        while host_from <= host_to:
            hosts_dict[host_from] = "Reachable" if ping(host_from) == 0 else "Unreachable"
            host_from += 1
        return hosts_dict


def host_ping(addr_list: List[str]) -> None:
    for addr in addr_list:
        ip4 = ipaddress.ip_address(addr)
        print(addr, " Узел доступен" if ping(ip4) == 0 else " Узел доступен")


def host_range_ping(host_from: str, host_to: str) -> None:
    hosts_dict = range_ping(host_from, host_to)
    for ip_addr, status in hosts_dict.items():
        print(f'{ip_addr}: {status}')


def host_range_ping_tab(host_from: str, host_to: str) -> None:
    hosts_dict = range_ping(host_from, host_to)
    disabled_hosts, active_hosts = [], []
    for host, status in hosts_dict.items():
        if status == "Reachable":
            active_hosts.append(host)
        else:
            disabled_hosts.append(host)
    headers = ("Reachable", "Unreachable")
    print(tabulate(active_hosts, headers=headers[0]))
    print(tabulate(disabled_hosts, headers=headers[1]))
