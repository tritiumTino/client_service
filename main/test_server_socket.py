import unittest
import socket

from server_socket import (
    form_answer,
    generate_socket,
    set_socket_settings
)


class ServerSocketTestCase(unittest.TestCase):
    def setUp(self):
        self.socket_obj = generate_socket()
        set_socket_settings(self.socket_obj)
        self.encoding = 'utf-8'
        self.msg = '{"action": "presence", "time": 1640711375.035588, "type": "status", ' \
                   '"user": {"account_name": "Tritium", "status": "Yep, I am here!"}}'.encode(self.encoding)
        self.answer_for_presence = b'{"response": 200, "alert": "I see you"}'
        self.answer_for_else = b'{"response": 500, "alert": "What are you doing?"}'

    def test_create_socket(self):
        self.assertTrue(self.socket_obj is not None)
        self.socket_obj.close()

    def test_socket_type(self):
        self.assertTrue(isinstance(self.socket_obj, socket.socket))
        self.socket_obj.close()

    def test_form_answer_for_presence(self):
        result = form_answer(self.msg)
        self.assertEqual(result, self.answer_for_presence)
        self.socket_obj.close()

    def test_another_answer(self):
        result = form_answer(b'{"action": "test"}')
        self.assertEqual(result, self.answer_for_else)
        self.socket_obj.close()


if __name__ == '__main__':
    unittest.main()
