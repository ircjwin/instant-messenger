from socket import *
from messenger import Messenger


class ServerMessenger(Messenger):

    def __init__(self):
        self._server_send = None
        self._server_listen = None
        super().__init__()

    def setup(self):
        print("Waiting for client...", end="", flush=True)

        self._send_addr = ("127.0.0.1", 60442)
        self._listen_addr = ("127.0.0.1", 60441)
        self._server_send = socket()
        self._server_listen = socket()
        self._server_send.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
        self._server_listen.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
        self._server_send.bind(self._send_addr)
        self._server_listen.bind(self._listen_addr)
        self._server_send.listen(1)
        self._server_listen.listen(1)
        self._send_socket, _ = self._server_send.accept()
        self._listen_socket, _ = self._server_listen.accept()

        print("", end="\r")


if __name__ == "__main__":
    server_messenger = ServerMessenger()
    server_messenger.run()
