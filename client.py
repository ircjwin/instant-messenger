from socket import socket
from messenger import Messenger


class ClientMessenger(Messenger):

    def setup(self):
        self._send_addr = ("127.0.0.1", 60441)
        self._listen_addr = ("127.0.0.1", 60442)
        self._send_socket = socket()
        self._listen_socket = socket()
        self._send_socket.connect(self._send_addr)
        self._listen_socket.connect(self._listen_addr)


if __name__ == "__main__":
    client_messenger = ClientMessenger()
    client_messenger.run()
