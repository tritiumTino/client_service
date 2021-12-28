import unittest
import socket

from client_socket import (
    parse_server_message,
    generate_socket,
    set_socket_settings
)


class ClientSocketTestCase(unittest.TestCase):
    def setUp(self):
        self.socket_obj = generate_socket()
        set_socket_settings(self.socket_obj)
        self.server_msg = '{"response": 200, "alert": "I see you"}'
        self.encoding = 'utf-8'

    def test_create_socket(self):
        self.assertTrue(self.socket_obj is not None)
        self.socket_obj.close()

    def test_socket_type(self):
        self.assertTrue(isinstance(self.socket_obj, socket.socket))
        self.socket_obj.close()

    def test_parse_server_message(self):
        result = parse_server_message(self.server_msg.encode(self.encoding))
        self.assertEqual(result, {'response': 200, 'alert': 'I see you'})
        self.socket_obj.close()

    def test_parsed_message_type(self):
        result = parse_server_message(self.server_msg.encode(self.encoding))
        self.assertTrue(type(result) == dict)
        self.socket_obj.close()


if __name__ == '__main__':
    unittest.main()
