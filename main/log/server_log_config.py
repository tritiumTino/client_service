import logging
import sys

from logging.handlers import TimedRotatingFileHandler

file_format = logging.Formatter("%(levelname)-10s %(asctime)s %(module)s %(message)s")
stream_format = logging.Formatter("%(levelname)-10s %(asctime)s %(message)s")

server_log = logging.getLogger('app.server')
server_log.setLevel(logging.INFO)

server_file_handler = TimedRotatingFileHandler('server.log', when='midnight')
server_file_handler.setFormatter(file_format)
server_file_handler.setLevel(logging.WARNING)

server_stream_handler = logging.StreamHandler(sys.stderr)
server_stream_handler.setFormatter(stream_format)
server_stream_handler.setLevel(logging.INFO)

server_log.addHandler(server_file_handler)
server_log.addHandler(server_stream_handler)
