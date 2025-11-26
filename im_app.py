import sys
from textual import on, work, timer
from textual.app import App, ComposeResult
from textual.containers import VerticalScroll
from textual.widgets import Footer, Header, Input, Markdown
from messenger import Messenger
from client import ClientMessenger
from server import ServerMessenger
from threading import Thread, Event


class OutMessage(Markdown):
    """Markdown for the user message."""

    BORDER_TITLE = "Me"


class InMessage(Markdown):
    """Markdown for the reply."""

    BORDER_TITLE = "You"


class IMApp(App):

    AUTO_FOCUS = "Input"

    BINDINGS = []

    CSS = """
    OutMessage {
        border: wide $primary;
        background: $primary 10%;
        color: $text;
        margin: 1;        
        margin-left: 8;
        padding: 1 2 0 2;
    }

    InMessage {
        border: wide $success;
        background: $success 10%;   
        color: $text;             
        margin: 1;      
        margin-right: 8; 
        padding: 1 2 0 2;
    }
    """

    def __init__(self, messenger: Messenger) -> None:
        self._messenger: Messenger = messenger
        self._inbox: list = []
        self._outbox: list = []
        self._thread_event: Event = Event()
        self._is_typing = False
        self._is_indicating = False
        self._typing_timer = None
        self._indicator_timer = None
        super().__init__()

    def compose(self) -> ComposeResult:
        yield Header()
        yield VerticalScroll(id="chat-view")
        yield Markdown(id="typing-indicator")
        yield Input(placeholder="Type your message here...")
        yield Footer()

    async def _on_exit_app(self) -> None:
        self.get_thread_event().set()
        await super()._on_exit_app()

    def on_mount(self) -> None:
        self.query_one("#chat-view").anchor()

    def on_load(self) -> None:
        self.inbox_listener()

    def get_messenger(self) -> Messenger:
        return self._messenger

    def get_inbox(self) -> list:
        return self._inbox

    def get_outbox(self) -> list:
        return self._outbox

    def get_thread_event(self) -> Event:
        return self._thread_event

    async def show_indicator(self) -> None:
        if self._indicator_timer is None:
            self._indicator_timer = self.set_timer(delay=3.0,
                                                   callback=self.hide_indicator,
                                                   pause=True)
        typing_indicator = self.query_one("#typing-indicator", Markdown)
        if not self._is_indicating:
            self._is_indicating = True
            await typing_indicator.update("You is typing...")
        self._indicator_timer.reset()
        self._indicator_timer.resume()

    async def hide_indicator(self) -> None:
        typing_indicator = self.query_one("#typing-indicator", Markdown)
        await typing_indicator.update("")
        self._is_indicating = False

    async def block_typing_signal(self) -> None:
        if self._typing_timer is None:
            self._typing_timer = self.set_timer(delay=0.5,
                                                callback=self.unblock_typing_signal,
                                                pause=True)
        if self._is_typing:
            return
        self._is_typing = True
        self.get_outbox().append("[typing]")
        self._typing_timer.reset()
        self._typing_timer.resume()

    def unblock_typing_signal(self) -> None:
        self._is_typing = False

    @on(Input.Changed)
    async def on_input_changed(self) -> None:
        await self.block_typing_signal()

    @on(Input.Submitted)
    async def on_input_submitted(self, input_event: Input.Submitted) -> None:
        """When the user hits return."""
        chat_view = self.query_one("#chat-view")
        input_event.input.clear()
        self.get_outbox().append(input_event.value)
        await chat_view.mount(OutMessage(input_event.value))

    @work(thread=True)
    def inbox_listener(self) -> None:
        """Get the response in a thread."""
        chat_view = self.query_one("#chat-view")
        while True:
            if self.get_thread_event().is_set():
                return
            if self._inbox:
                msg: str = self._inbox.pop(0)
                if msg.startswith("[typing]"):
                    self.call_from_thread(self.show_indicator)
                else:
                    self.call_from_thread(chat_view.mount, InMessage(msg))


if __name__ == "__main__":
    if len(sys.argv) == 2:
        app = None
        if sys.argv[1] == "server":
            app = IMApp(ServerMessenger())
        elif sys.argv[1] == "client":
            app = IMApp(ClientMessenger())
        else:
            print(f"Invalid argument(s): {sys.argv}")
            sys.exit()
        socket_thread = Thread(target=app.get_messenger().run,
                               args=[app.get_thread_event(),
                                     app.get_inbox(),
                                     app.get_outbox(), ],
                               daemon=True)
        socket_thread.start()
        app.run()
        sys.exit()
    print("Missing 1 argument")
