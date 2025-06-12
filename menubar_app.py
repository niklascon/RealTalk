import rumps
import os
import threading
import queue
import keyboard
from common.speech import recognize_speech

script_path = os.path.dirname(__file__)
rt_icon_path_listening = "assets/icons/RealTalk_transparent_white_green.png"
rt_icon_path_paused = "assets/icons/RealTalk_transparent_white_red.png"
rt_icon_path_white = "assets/icons/RealTalk_transparent_white.png"
rt_icon = os.path.join(script_path, rt_icon_path_paused)

KEYWORDS = ["exit", "scam", "scammen", "betrug", "passwort", "passwörter", "geld", "money", "finanzen",
"enkel", "enkelkind", "kind", "konto", "kontonummer", "iban", "bic", "bank", "überweisung", "onlinebanking", "bankdaten", "bankverbindung",
"zugangsdaten", "tan", "photo-tan", "push-tan", "chip-tan", "banking-app", "bankkonto", "sicherheitscode", "pin", "passwort", "passwörter", "login", "zugang", "authentifizierung", "verifizierung", "identität",
"zugriffsrechte", "sicherheitsfrage", "freigabe", "sperrung", "entsperren", "token", "code", "sms-code", "enkel", "enkelkind", "oma", "opa", "kind", "tochter", "sohn", "verwandt", "familie", "dringend",
"unfall", "verhaftet", "kaution", "geld", "überweisen", "zahlung", "zahlen", "betrag", "scam", "scammen", "betrug", "betrüger", "kriminell", "abzocke", "erpressung", "dringend", "sofort", "gefahr", "notfall", "schaden", "verlust", "support", "it-abteilung", "technik", "update", "fernzugriff", "teamviewer", "anydesk", "zugriff", "installieren",
"computer", "wartung", "sicherheitslücke", "hacker", "viren", "trojaner", "zugang geben", "daten", "ausweis", "personalausweis", "führerschein",
"kopie", "scan", "hochladen", "identitätsnachweis", "unterlagen", "persönlich", "vertraulich", "polizei", "kripo", "staatsanwaltschaft", "gericht", "finanzamt", "bundesbank", "ezb", "zoll", "behörde",
"regierung", "botschaft", "konsulat", "ermittlung", "verhör", "anzeige", "aktenzeichen", "anwalt", "notar", "beamter", "bankmitarbeiter", "berater", "microsoft", "it-support", "telekom", "versicherer",
"post", "inkasso", "stromanbieter", "internetprovider", "dringlichkeit", "sofort", "wichtig", "vertraulich", "zeitdruck", "frist", "mahnbescheid", "pfändung",
"geheim", "verheimlichen", "nicht erzählen", "keinem sagen", "nur du", "vertraue mir", "niemandem mitteilen", "dhl", "ups", "gls", "sendung", "paket", "zustellung", "versand", "lieferung", "versandkosten", "tracking",
"lieferprobleme", "paketdienst", "link", "verifizieren", "konto bestätigen",
"zahlung autorisieren", "weiterleitung", "eingabemaske", "anmeldung", "captcha", "online-zugang", "whatsapp", "telegram", "nachricht", "sms", "code erhalten", "code weiterleiten", "neue nummer", "alte nummer verloren",
"handy kaputt", "neue sim", "instagram", "facebook", "profil gehackt", "account gesperrt"]

class MenuBarApp(rumps.App):
    def __init__(self):
        self.notification_queue = queue.Queue()

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

        self.register_hotkey()

        self.listening = False
        self.thread = None
        self.stop_event = threading.Event()

        # Startet alle 0.5s und prüft auf neue Events
        self.timer = rumps.Timer(self.check_queue, 0.5)
        self.timer.start()

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
            print(f"🎧 KEYWORD erkannt → Flash vorbereiten: {keyword}")
            self.notification_queue.put(keyword)

    def check_queue(self, _):
        while not self.notification_queue.empty():
            keyword = self.notification_queue.get()
            print(f"📢 FLASH-ALERT für Schlüsselwort: {keyword}")

            print(f"[DEBUG] Current thread: {threading.current_thread().name}")
            '''
            rumps.notification(
                title="🎤 RealTalk",
                subtitle="Sprachbefehl erkannt",
                message=f"Schlüsselwort: '{keyword}' erkannt!"
            )
            '''
            rumps.alert(
                title="RealTalk",
                message="RealTalk has identified suspicious voice activity. Please end the call immediately and notify your security team.",
                ok="Acknowledge",
                icon_path=rt_icon_path_white
            )

    def register_hotkey(self):
        # Setzt globalen Hotkey auf z.B. STRG + ALT + B
        print("setze hotkey")
        keyboard.add_hotkey('b', self.trigger_manual_alert)

    def trigger_manual_alert(self):
        print("[MANUELLER ALERT] via Hotkey ausgelöst.")
        self.notification_queue.put("🛑 MANUELLER ALERT")

if __name__ == "__main__":
    MenuBarApp().run()