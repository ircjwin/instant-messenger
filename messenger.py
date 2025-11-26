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
        self._inbox: list | None = None
        self._outbox: list | None = None

    def close_sockets(self) -> None:
        """
        Closes sockets.

        :param: N/A
        :return: N/A
        """
        self._send_socket.close()
        self._listen_socket.close()

    def send_msg(self, event: Event) -> None:
        """
        Sends messages.

        :param event: Event object that signals termination
        :return: N/A
        """
        while True:
            if event.is_set():
                return

            if self._outbox:
                msg = self._outbox.pop(0)
                self._send_socket.send(msg.encode())

    def listen_msg(self, event: Event) -> None:
        """
        Receives messages.

        :param event: Event object that signals termination
        :return: N/A
        """
        while True:
            if event.is_set():
                return

            msg = self._listen_socket.recv(2048)
            if len(msg) == 0:
                event.set()
                return
            decode_msg = msg.decode()
            self._inbox.append(decode_msg)

    @abstractmethod
    def setup(self) -> None:
        pass

    def run(self, event: Event, inbox: list, outbox: list) -> None:
        """
        Establishes socket connection and handles termination.

        :param: N/A
        :return: N/A
        """
        self._inbox = inbox
        self._outbox = outbox
        self.setup()

        send_thread = Thread(target=self.send_msg,
                             args=[event, ],
                             daemon=True)
        listen_thread = Thread(target=self.listen_msg,
                               args=[event, ],
                               daemon=True)
        send_thread.start()
        listen_thread.start()
        event.wait()
        self.close_sockets()
        sys.exit()
