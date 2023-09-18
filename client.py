# Author:       Chris "C.J" Irwin
# GitHub:       ircjwin
# Email:        christopherjamesirwin@gmail.com
# Description:  This is a client that sends and receives messages with a
#               server. It is meant to be run in a terminal.


import sys
import select
from socket import *
from threading import Event, Thread


class ClientMessenger:
    """
    Represents a client socket that can send and receive messages

    Attributes:
            client_send (object):  Client socket that sends messages
            client_listen (object):  Client socket that receives messages
            server_send (tuple):  IP and Port for Server socket
            server_listen (tuple):  IP and Port for Server socket
    """

    def __init__(self):
        """
        Initializes a ClientMessenger object.

        :param: N/A
        :return: N/A
        """
        self._client_send = socket()
        self._client_listen = socket()
        self._server_send = ("127.0.0.1", 60442)
        self._server_listen = ("127.0.0.1", 60441)

    def close_sockets(self):
        """
        Closes Client sockets.

        :param: N/A
        :return: N/A
        """
        self._client_send.close()
        self._client_listen.close()

    def send_msg(self, event):
        """
        Sends Client messages.

        :param event: Event object that signals termination
        :return: N/A
        """
        while True:
            if event.is_set():
                break

            # Checks for data from server to keep messages in order
            sock_arr = [self._client_listen]
            recv_sockets, wl, xl = select.select(sock_arr, sock_arr, sock_arr)
            if self._client_listen not in recv_sockets:
                client_msg = sys.stdin.readline()
                # Uses escape A to move cursor up one line -> '\033[1A'
                print(f"\033[1AC: {client_msg}", end='\r', flush=True)
                self._client_send.send(client_msg.encode())

                if client_msg.strip("\n") == "/q":
                    event.set()
                    break

    def listen_msg(self, event):
        """
        ReceivesServer messages.

        :param event: Event object that signals termination
        :return: N/A
        """
        while True:
            if event.is_set():
                break
            # Checks for server data to prevent recv() blocking execution
            sock_arr = [self._client_listen]
            recv_sockets, wl, xl = select.select(sock_arr, sock_arr, sock_arr)
            if self._client_listen in recv_sockets:
                server_msg = self._client_listen.recv(2048)
                decode_msg = server_msg.decode()

                if decode_msg.strip("\n") == "/q":
                    event.set()
                    break

                print(f"S: {decode_msg}", end='\r', flush=True)

    def main(self):
        """
        Establishes Client-Server connection and handles termination.

        :param: N/A
        :return: N/A
        """
        self._client_send.connect(self._server_listen)
        self._client_listen.connect(self._server_send)

        print(f"Type /q to quit\n"
              f"Enter message to send...")

        event = Event()
        send_thread = Thread(target=self.send_msg,
                             args=[event, ],
                             daemon=True)
        listen_thread = Thread(target=self.listen_msg,
                               args=[event, ],
                               daemon=True)
        send_thread.start()
        listen_thread.start()
        stop = event.is_set()

        while stop is False:
            stop = event.is_set()

        self.close_sockets()
        sys.exit()


if __name__ == "__main__":
    messenger = ClientMessenger()
    messenger.main()
