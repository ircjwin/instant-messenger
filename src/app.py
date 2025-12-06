import sys
from textual import on, work, timer
from textual.app import App, ComposeResult
from textual.containers import VerticalScroll
from textual.widgets import Footer, Header, Input, Markdown
from threading import Thread, Event
from messenger import Messenger
from client import ClientMessenger
from server import ServerMessenger


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
        self._thread_event: Event = Event()
        self._is_indicating = False
        self._indicator_timer = None
        super().__init__()

    def compose(self) -> ComposeResult:
        yield Header()
        yield VerticalScroll(id="chat-view")
        yield Markdown(id="typing-indicator")
        yield Input(placeholder="Type your message here...")
        yield Footer()

    def on_mount(self) -> None:
        self.query_one("#chat-view").anchor()

    def on_load(self) -> None:
        socket_thread = Thread(target=self._messenger.run,
                               args=[self._thread_event,
                                     self.listen, ],
                               daemon=True)
        socket_thread.start()

    async def _on_exit_app(self) -> None:
        self._thread_event.set()
        await super()._on_exit_app()

    @work
    async def show_indicator(self) -> None:
        if self._indicator_timer is None:
            self._indicator_timer = self.set_timer(delay=1.0,
                                                   callback=self.hide_indicator,
                                                   pause=True)
        typing_indicator = self.query_one("#typing-indicator", Markdown)
        if not self._is_indicating:
            self._is_indicating = True
            await typing_indicator.update("You is typing...")
        self._indicator_timer.reset()
        self._indicator_timer.resume()

    @work
    async def hide_indicator(self) -> None:
        if not self._is_indicating:
            return
        typing_indicator = self.query_one("#typing-indicator", Markdown)
        await typing_indicator.update("")
        self._indicator_timer.stop()
        self._indicator_timer = None
        self._is_indicating = False

    @work
    async def listen(self, msg: str):
        if msg.startswith("[typing]"):
            self.show_indicator()
            return
        self.hide_indicator()
        chat_view = self.query_one("#chat-view")
        await chat_view.mount(InMessage(msg))

    @on(Input.Changed)
    def on_input_changed(self, input_event: Input.Changed) -> None:
        if input_event.value == "":
            return
        self._messenger.send("[typing]")

    @on(Input.Submitted)
    async def on_input_submitted(self, input_event: Input.Submitted) -> None:
        """When the user hits return."""
        if input_event.value == "":
            return
        chat_view = self.query_one("#chat-view")
        input_event.input.clear()
        self._messenger.send(input_event.value)
        await chat_view.mount(OutMessage(input_event.value))


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
        app.run()
        sys.exit()
    print("Missing 1 argument")
