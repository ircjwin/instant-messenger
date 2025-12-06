import sys
from socket import *
from select import select
from threading import Event, Thread
from abc import ABCMeta, abstractmethod


class Messenger(metaclass=ABCMeta):
    """
    Represents a socket that can send and receive messages

    Attributes:
            _send_socket (object):  Socket that sends messages
            _listen_socket (object):  Socket that receives messages
            _send_addr (tuple):  IP and Port for Server socket
            _listen_addr (tuple):  IP and Port for Server socket
    """

    def __init__(self) -> None:
        """
        Initializes a Messenger object.

        :param: N/A
        :return: N/A
        """
        self._send_socket: socket | None = None
        self._listen_socket: socket | None = None
        self._send_addr: tuple | None = None
        self._listen_addr: tuple | None = None

    def close_sockets(self) -> None:
        """
        Closes sockets.

        :param: N/A
        :return: N/A
        """
        self._send_socket.close()
        self._listen_socket.close()

    def send(self, msg: str) -> None:
        """
        Sends messages.

        :param msg: String to send over socket.
        :return: N/A
        """
        self._send_socket.send(msg.encode())

    def listen(self, event: Event, publisher) -> None:
        """
        Receives messages.

        :param event: Event object that signals termination
        :param publisher: Callback for frontend listener
        :return: N/A
        """
        while True:
            if event.is_set():
                return
            readable_sockets, _, _ = select([self._listen_socket], [], [], 0)
            if self._listen_socket not in readable_sockets:
                continue
            msg = self._listen_socket.recv(2048)
            if len(msg) == 0:
                event.set()
                return
            decode_msg = msg.decode()
            publisher(decode_msg)

    @abstractmethod
    def setup(self) -> None:
        pass

    def run(self, event: Event, publisher) -> None:
        """
        Establishes socket connection and handles termination.

        :param: N/A
        :return: N/A
        """
        self.setup()
        listen_thread = Thread(target=self.listen,
                               args=[event, publisher],
                               daemon=True)
        listen_thread.start()
        event.wait()
        self.close_sockets()
        sys.exit()
