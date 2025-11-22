import sys
from select import select
from threading import Event, Thread


class Messenger:
    """
    Represents a socket that can send and receive messages

    Attributes:
            _send_socket (object):  Socket that sends messages
            _listen_socket (object):  Socket that receives messages
            _send_addr (tuple):  IP and Port for Server socket
            _listen_addr (tuple):  IP and Port for Server socket
    """

    def __init__(self):
        """
        Initializes a Messenger object.

        :param: N/A
        :return: N/A
        """
        self._send_socket = None
        self._listen_socket = None
        self._send_addr = None
        self._listen_addr = None

    def close_sockets(self):
        """
        Closes sockets.

        :param: N/A
        :return: N/A
        """
        self._send_socket.close()
        self._listen_socket.close()

    def send_msg(self, event):
        """
        Sends messages.

        :param event: Event object that signals termination
        :return: N/A
        """
        while True:
            if event.is_set():
                return

            # Checks for data from client to keep messages in order
            readable_sockets, _, _ = select([self._listen_socket], [], [], 0)
            if self._listen_socket not in readable_sockets:
                msg = sys.stdin.readline()
                # Uses escape A to move cursor up one line -> '\033[1A'
                print(f"\033[2AS: {msg}")
                print(f"\033[1A{' ' * len(msg)}\n", end="\r")
                self._send_socket.send(msg.encode())

                if msg.strip("\n") == "/q":
                    event.set()
                    return

    def listen_msg(self, event):
        """
        Receives messages.

        :param event: Event object that signals termination
        :return: N/A
        """
        while True:
            if event.is_set():
                return
            # Checks for client data to prevent recv() blocking execution
            readable_sockets, _, _ = select([self._listen_socket], [], [], 0)
            if self._listen_socket in readable_sockets:
                msg = self._listen_socket.recv(2048)
                decode_msg = msg.decode()
                strip_msg = decode_msg.strip("\n")
                if strip_msg == "/q":
                    event.set()
                    return

                print(f"\r\033[1AC: {strip_msg}\n")

    def setup(self):
        raise NotImplementedError

    def run(self):
        """
        Establishes socket connection and handles termination.

        :param: N/A
        :return: N/A
        """
        self.setup()

        print(f"Type /q to quit         \n"
              f"Enter message to send...\n")

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

        while not stop:
            stop = event.is_set()

        self.close_sockets()
        sys.exit()


if __name__ == "__main__":
    messenger = Messenger()
    messenger.run()
