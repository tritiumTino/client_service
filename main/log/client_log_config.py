import logging
import sys


file_format = logging.Formatter("%(levelname)-10s %(asctime)s %(module)s %(message)s")
stream_format = logging.Formatter("%(levelname)-10s %(asctime)s %(message)s")

client_log = logging.getLogger('app.client')
client_log.setLevel(logging.INFO)

client_file_handler = logging.FileHandler('client.log')
client_file_handler.setFormatter(file_format)
client_file_handler.setLevel(logging.WARNING)

client_stream_handler = logging.StreamHandler(sys.stderr)
client_stream_handler.setFormatter(stream_format)
client_stream_handler.setLevel(logging.INFO)

client_log.addHandler(client_file_handler)
client_log.addHandler(client_stream_handler)
