# Author:       Chris "C.J" Irwin
# GitHub:       ircjwin
# Email:        christopherjamesirwin@gmail.com
# Description:  This is a server that sends and receives messages with a
#               client. It is meant to be run in a terminal.


import sys
import select
from socket import *
from threading import Event, Thread


class ServerMessenger:
    """
    Represents a client socket that can send and receive messages

    Attributes:
            client_send (object):  Client socket that sends messages
            client_listen (object):  Client socket that receives messages
            server_send (object):  Server socket that sends messages
            server_listen (object):  Server socket that receives messages
            send_port (tuple):  IP and Port for Server socket
            listen_port (tuple):  IP and Port for Server socket
    """

    def __init__(self):
        """
        Initializes a ServerMessenger object.

        :param: N/A
        :return: N/A
        """
        self._client_send = None
        self._client_listen = None
        self._server_send = socket()
        self._server_listen = socket()
        self._send_port = ("127.0.0.1", 60442)
        self._listen_port = ("127.0.0.1", 60441)

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
        Sends Server messages.

        :param event: Event object that signals termination
        :return: N/A
        """
        while True:
            if event.is_set():
                break

            # Checks for data from client to keep messages in order
            sock_arr = [self._client_send]
            recv_sockets, wl, xl = select.select(sock_arr, sock_arr, sock_arr)
            if self._client_send not in recv_sockets:
                server_msg = sys.stdin.readline()
                # Uses escape A to move cursor up one line -> '\033[1A'
                print(f"\033[1AS: {server_msg}", end='\r')
                self._client_listen.send(server_msg.encode())

                if server_msg.strip("\n") == "/q":
                    event.set()
                    break

    def listen_msg(self, event):
        """
        Receives Client messages.

        :param event: Event object that signals termination
        :return: N/A
        """
        while True:
            if event.is_set():
                break
            # Checks for client data to prevent recv() blocking execution
            sock_arr = [self._client_send]
            recv_sockets, wl, xl = select.select(sock_arr, sock_arr, sock_arr)
            if self._client_send in recv_sockets:
                client_msg = self._client_send.recv(2048)
                decode_msg = client_msg.decode()

                if decode_msg.strip("\n") == "/q":
                    event.set()
                    break

                print(f"C: {decode_msg}", end='\r', flush=True)

    def main(self):
        """
        Establishes Client-Server connection and handles termination.

        :param: N/A
        :return: N/A
        """
        print("Waiting for client...", end='', flush=True)

        self._server_send.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
        self._server_listen.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
        self._server_send.bind(self._send_port)
        self._server_listen.bind(self._listen_port)
        self._server_send.listen(1)
        self._server_listen.listen(1)
        self._client_send, send_addr = self._server_listen.accept()
        self._client_listen, listen_addr = self._server_send.accept()

        print("", end='\r', flush=True)
        print(f"Type /q to quit       \n"
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
    messenger = ServerMessenger()
    messenger.main()
