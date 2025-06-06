import rumps # type: ignore 
import os
import threading
from common.speech import recognize_speech


script_path = os.path.dirname(__file__)
rt_icon_path_listening = "assets/icons/Realtalk_transparent_green.png"
rt_icon_path_paused = "assets/icons/Realtalk_transparent_red.png"
rt_icon = os.path.join(script_path, rt_icon_path_paused)

KEYWORDS = ["hallo", "exit", "hilfe"]

class MenuBarApp(rumps.App):
    def __init__(self):
        self.start_item = rumps.MenuItem("Start Listening", callback=self.start_listening)
        self.stop_item = rumps.MenuItem("Stop Listening", callback=None)

        super().__init__(
            name="RealTalk",
            icon=rt_icon_path_paused,
            menu=[
                self.start_item,
                self.stop_item,
                None,
            ]
        )

        self.listening = False
        self.thread = None
        self.stop_event = threading.Event()

    def start_listening(self, _):
        self.listening = True
        self.stop_event.clear()
        self.icon = rt_icon_path_listening

        self.menu["Start Listening"].title = "🟢 Listening..."
        self.menu["Start Listening"].set_callback(None)
        self.menu["Stop Listening"].set_callback(self.stop_listening)

        self.thread = threading.Thread(
            target=recognize_speech,
            args=(KEYWORDS, self.update_status, self.stop_event),
            daemon=True
        )
        self.thread.start()

    def stop_listening(self, _):
        self.stop_event.set()
        self.listening = False
        self.icon = rt_icon_path_paused

        self.menu["Start Listening"].title = "Start Listening"
        self.menu["Start Listening"].set_callback(self.start_listening)
        self.menu["Stop Listening"].set_callback(None)

    def update_status(self, status: bool, keyword: str = ""):
        if status:
            # Das geht so nicht, da update_status aus speech.py aus aufgerufen wird. rumps.alert geht nur aus der main raus
            rumps.alert("RealTalk", f"Du hast '{keyword}' gesagt.")

if __name__ == "__main__":
     MenuBarApp().run()