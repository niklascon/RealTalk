import rumps
import os
import threading
import queue
from common.speech import recognize_speech

script_path = os.path.dirname(__file__)
rt_icon_path = "assets/icons/Realtalk_transparent.png"
rt_icon = os.path.join(script_path, rt_icon_path)

KEYWORDS = ["hallo", "exit", "hilfe"]

class MenuBarApp(rumps.App):
    def __init__(self):
        self.notification_queue = queue.Queue()

        self.start_item = rumps.MenuItem("Start Listening", callback=self.start_listening)
        self.stop_item = rumps.MenuItem("Stop Listening", callback=None)

        super().__init__(
            name="RealTalk",
            icon=rt_icon_path,
            menu=[
                self.start_item,
                self.stop_item,
                None,
            ],
            template=True
        )

        self.listening = False
        self.thread = None
        self.title = "🔴 Paused..."
        self.stop_event = threading.Event()

        # Startet alle 0.5s und prüft auf neue Events
        self.timer = rumps.Timer(self.check_queue, 0.5)
        self.timer.start()

    def start_listening(self, _):
        self.listening = True
        self.stop_event.clear()
        self.title = "🟢 Listening..."

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
        self.title = "🔴 Paused..."

        self.menu["Start Listening"].title = "Start Listening"
        self.menu["Start Listening"].set_callback(self.start_listening)
        self.menu["Stop Listening"].set_callback(None)

    def update_status(self, status: bool, keyword: str = ""):
        if status:
            print(f"🎧 KEYWORD erkannt → Flash vorbereiten: {keyword}")
            self.notification_queue.put(keyword)

    def check_queue(self, _):
        while not self.notification_queue.empty():
            keyword = self.notification_queue.get()
            print(f"📢 FLASH-ALERT für Schlüsselwort: {keyword}")

            print(f"[DEBUG] Current thread: {threading.current_thread().name}")
            rumps.notification(
                title="🎤 RealTalk",
                subtitle="Sprachbefehl erkannt",
                message=f"Schlüsselwort: '{keyword}' erkannt!"
            )


if __name__ == "__main__":
    MenuBarApp().run()