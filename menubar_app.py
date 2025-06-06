import rumps # type: ignore 
import os
import threading
from common.speech import recognize_speech


script_path = os.path.dirname(__file__)
rt_icon_path = "assets/icons/Realtalk_transparent.png"
rt_icon = os.path.join(script_path, rt_icon_path)

KEYWORDS = ["exit", "scam", "scammen", "betrug", "passwort", "passwörter", "daten", "datei", "geld", "money", "finanzen",
"enkel", "enkelkind", "kind", "konto", "kontonummer", "iban", "bic", "bank", "überweisung", "onlinebanking", "bankdaten", "bankverbindung",
"zugangsdaten", "tan", "photo-tan", "push-tan", "chip-tan", "banking-app", "bankkonto", "sicherheitscode", "pin", "passwort", "passwörter", "login", "zugang", "authentifizierung", "verifizierung", "identität",
"zugriffsrechte", "sicherheitsfrage", "freigabe", "sperrung", "entsperren", "token", "code", "sms-code", "enkel", "enkelkind", "oma", "opa", "kind", "tochter", "sohn", "verwandt", "familie", "notfall", "dringend",
"unfall", "hilfe", "verhaftet", "kaution", "geld", "überweisen", "zahlung", "zahlen", "betrag", "scam", "scammen", "betrug", "betrüger", "kriminell", "abzocke", "erpressung", "dringend", "sofort", "gefahr", "notfall", "schaden", "verlust", "support", "it-abteilung", "technik", "update", "fernzugriff", "teamviewer", "anydesk", "zugriff", "installieren",
"computer", "wartung", "sicherheitslücke", "hacker", "viren", "trojaner", "zugang geben", "daten", "datei", "dateien", "dokument", "dokumente", "ausweis", "personalausweis", "führerschein",
"kopie", "scan", "hochladen", "identitätsnachweis", "unterlagen", "persönlich", "vertraulich", "polizei", "kripo", "staatsanwaltschaft", "gericht", "finanzamt", "bundesbank", "ezb", "zoll", "behörde",
"regierung", "botschaft", "konsulat", "ermittlung", "verhör", "anzeige", "aktenzeichen", "anwalt", "notar", "beamter", "bankmitarbeiter", "berater", "microsoft", "it-support", "telekom", "versicherer",
"post", "inkasso", "stromanbieter", "internetprovider", "kundenservice", "kundendienst", "servicecenter", "dringlichkeit", "sofort", "wichtig", "vertraulich", "zeitdruck", "frist", "mahnbescheid", "pfändung",
"geheim", "verheimlichen", "nicht erzählen", "keinem sagen", "nur du", "vertraue mir", "niemandem mitteilen", "dhl", "ups", "gls", "sendung", "paket", "zustellung", "versand", "lieferung", "versandkosten", "tracking",
"lieferprobleme", "paketdienst", "formular", "link", "klick", "website", "eingeben", "bestätigen", "verifizieren", "konto bestätigen",
"zahlung autorisieren", "weiterleitung", "eingabemaske", "anmeldung", "captcha", "online-zugang", "whatsapp", "telegram", "nachricht", "sms", "code erhalten", "code weiterleiten", "neue nummer", "alte nummer verloren",
"handy kaputt", "neue sim", "instagram", "facebook", "profil gehackt", "account gesperrt"]

class MenuBarApp(rumps.App):
    def __init__(self):
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
            # Das geht so nicht, da update_status aus speech.py aus aufgerufen wird. rumps.alert geht nur aus der main raus
            rumps.alert("RealTalk", f"Du hast '{keyword}' gesagt.")

if __name__ == "__main__":
     MenuBarApp().run()