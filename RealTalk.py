import speech_recognition as sr
import pyttsx3
import tkinter as tk
import sys
import threading
import customtkinter
import smtplib
import time
import requests
import webbrowser
from collections import Counter
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from tkinter import messagebox
from flask import Flask, render_template, request, jsonify
from PIL import Image


logs = []

recognition_status = False
stop_recognition_flag = False
KEYWORDS = ["hallo", "exit", "hilfe"]

# --- Flask Webserver ---
app = Flask(__name__)
last_result = {"keyword": "", "text": ""}

@app.route('/')
def welcome():
    return render_template('welcome.html')

@app.route('/current')
def current():
    analysis = analyze_last_call(last_result["text"], last_result["keyword"])
    return render_template('current.html', last_result=last_result, analysis=analysis)

@app.route('/overview')
def overview():
    stats = analyze_logs(logs)
    return render_template('overview.html', stats=stats)


@app.route('/api/log', methods=['POST'])
def log_result():
    data = request.json
    keyword = data.get("keyword", "")
    text = data.get("text", "")
    timestamp = time.time()
    last_result["keyword"] = keyword
    last_result["text"] = text

    logs.append({
        "keyword": keyword,
        "text": text,
        "timestamp": timestamp
    })
    return jsonify({"status": "ok"})



def analyze_last_call(text, keyword):
    words = text.split()
    word_count = len(words)
    keyword_count = text.lower().count(keyword.lower()) if keyword else 0

    # Beispiel: Häufigkeit der Keywords in Text
    keyword_freq = {k: text.lower().count(k) for k in KEYWORDS}

    # Sentiment Dummy (nur beispielhaft)
    sentiment = "neutral"
    if "gut" in text.lower() or "super" in text.lower():
        sentiment = "positiv"
    elif "schlecht" in text.lower() or "problem" in text.lower():
        sentiment = "negativ"

    return {
        "word_count": word_count,
        "keyword_count": keyword_count,
        "keyword_freq": keyword_freq,
        "sentiment": sentiment,
    }


from collections import Counter
from datetime import datetime


def analyze_logs(logs):
    total_calls = len(logs)
    all_texts = " ".join(log["text"] for log in logs).lower()

    # Gesamt-Häufigkeit der Keywords über alle Logs
    keyword_counts = Counter()
    for kw in KEYWORDS:
        keyword_counts[kw] = all_texts.count(kw.lower())

    # Durchschnittliche Wortanzahl pro Erkennung
    word_counts = [len(log["text"].split()) for log in logs if log["text"]]
    avg_word_count = sum(word_counts) / len(word_counts) if word_counts else 0

    # Beispiel: Anrufe pro Tag (für die letzten 7 Tage)
    calls_per_day = Counter()
    for log in logs:
        day = datetime.fromtimestamp(log["timestamp"]).strftime("%Y-%m-%d")
        calls_per_day[day] += 1

    # Sortieren der Tage nach Datum absteigend, nur letzte 7 Tage
    last_7_days = sorted(calls_per_day.items(), reverse=True)[:7]

    return {
        "total_calls": total_calls,
        "keyword_counts": dict(keyword_counts),
        "avg_word_count": avg_word_count,
        "calls_per_day": last_7_days
    }


def start_flask():
    app.run(debug=False, use_reloader=False)

# --- Sprache ---
def speak(text):
    engine = pyttsx3.init()
    engine.say(text)
    engine.runAndWait()

def post_to_web(keyword, text):
    try:
        requests.post("http://localhost:5000/api/log", json={
            "keyword": keyword,
            "text": text
        })
    except Exception as e:
        print("Fehler beim Web-Post:", e)

def send_email_to_self(subject, body):
    sender_email = "maxi.schw@icloud.com"
    receiver_email = "maxi.schw@icloud.com"
    app_specific_password = "jwhj-safe-ojwh-evvf"

    msg = MIMEMultipart()
    msg['From'] = sender_email
    msg['To'] = receiver_email
    msg['Subject'] = subject
    msg.attach(MIMEText(body, 'plain'))

    try:
        with smtplib.SMTP_SSL("smtp.mail.me.com", 465) as server:
            time.sleep(1)
            server.login(sender_email, app_specific_password)
            server.sendmail(sender_email, receiver_email, msg.as_string())
            print("E-Mail gesendet.")
    except Exception as e:
        print(f"E-Mail-Fehler: {e}")

def recognize_speech():
    global stop_recognition_flag
    recognizer = sr.Recognizer()
    microphone = sr.Microphone()

    print("Rauschen kalibrieren...")
    with microphone as source:
        recognizer.adjust_for_ambient_noise(source, duration=1)

    print("Spracherkennung gestartet.")

    while not stop_recognition_flag:
        try:
            with microphone as source:
                print("Höre...")
                audio = recognizer.listen(source, timeout=5)

            recognized_text = recognizer.recognize_google(audio, language="de-DE,en-US").lower()
            print(f"Du hast gesagt: {recognized_text}")

            keyword_found = False
            for keyword in KEYWORDS:
                if keyword in recognized_text:
                    keyword_found = True
                    print(f"Keyword '{keyword}' erkannt.")

                    update_status(True)  # GUI-Update sofort starten

                    speak(f"Du hast das Schlüsselwort {keyword} gesagt.")  # blockiert, aber GUI schon aktualisiert
                    send_email_to_self("Selbst-Erinnerung", f"Erkannt: {recognized_text}")
                    post_to_web(keyword, recognized_text)

            # Falls du möchtest, dass "exit" das Programm beendet, kannst du das hier aktivieren:
            #                if keyword == "exit":
            #                    print("Beende Programm.")
            #                    stop_recognition_flag = True
            #                    return

            if not keyword_found:
                update_status(False)

        except sr.WaitTimeoutError:
            print("Timeout – keine Sprache erkannt.")
        except sr.UnknownValueError:
            print("Konnte Sprache nicht erkennen.")
        except sr.RequestError as e:
            print(f"Spracherkennungsfehler: {e}")

    print("Spracherkennung gestoppt.")

def blink_border():
    def _blink():
        for _ in range(3):  # 3 mal blinken
            border_frame.configure(fg_color="red")
            time.sleep(0.3)
            border_frame.configure(fg_color="transparent")
            time.sleep(0.3)
    threading.Thread(target=_blink, daemon=True).start()

def update_status(status):
    def gui_update():
        global recognition_status
        recognition_status = status

        if status:
            status_label.configure(text="🔴", fg_color="transparent")
            feedback_image_label.configure(image=red_img)
            feedback_image_label.image = red_img  # Wichtig: Referenz behalten
            blink_border()  # Rand blinken lassen
        else:
            status_label.configure(text="🟢", fg_color="transparent")
            feedback_image_label.configure(image=green_img)
            feedback_image_label.image = green_img  # Wichtig: Referenz behalten

    root.after(0, gui_update)  # GUI-Update im Hauptthread

def start_recognition():
    global stop_recognition_flag
    stop_recognition_flag = False
    update_status(False)
    threading.Thread(target=recognize_speech, daemon=True).start()

def stop_recognition():
    global stop_recognition_flag
    stop_recognition_flag = True
    update_status(False)
    print("Stopp angefordert.")

def update_keywords():
    global KEYWORDS
    input_text = keywords_entry.get().strip()
    if input_text:
        KEYWORDS = [kw.strip().lower() for kw in input_text.split(",") if kw.strip()]
        messagebox.showinfo("Aktualisiert", f"Neue Schlüsselwörter: {', '.join(KEYWORDS)}")
    else:
        messagebox.showwarning("Fehler", "Bitte gültige Schlüsselwörter eingeben.")

class OutputRedirector:
    def __init__(self, text_widget):
        self.text_widget = text_widget

    def write(self, text):
        self.text_widget.insert(tk.END, text)
        self.text_widget.see(tk.END)

    def flush(self):
        pass

def blink_border():
    def _blink():
        for _ in range(4):  # 4x blinken = ca. 2 Sekunden
            for frame in border_frames:
                frame.configure(fg_color="red")
            time.sleep(0.5)
            for frame in border_frames:
                frame.configure(fg_color="transparent")
            time.sleep(0.5)
    threading.Thread(target=_blink, daemon=True).start()


def open_website():
    # Ersetze den String durch deine gewünschte URL
    webbrowser.open_new_tab("http://127.0.0.1:5000")


def setup_gui():
    global root, border_frames
    root = customtkinter.CTk()
    root.title("Spracherkennung")

    customtkinter.set_appearance_mode("dark")
    customtkinter.set_default_color_theme("dark-blue")

    root.geometry("460x520")  # Startgröße
    root.resizable(True, True)  # Fenster dynamisch skalierbar

    global green_img, red_img, feedback_image_label, status_label

    green_img = customtkinter.CTkImage(
        light_image=Image.open("static/pictures/green_smiley.png"),
        size=(64, 64)
    )
    red_img = customtkinter.CTkImage(
        light_image=Image.open("static/pictures/red_smiley.png"),
        size=(64, 64)
    )

    border_frame = customtkinter.CTkFrame(root, fg_color="#2a2a2a", corner_radius=12)
    border_frame.pack(padx=12, pady=12, fill=tk.BOTH, expand=True)

    # Textbox etwas größer und flexibel
    text_box = customtkinter.CTkTextbox(border_frame, wrap=tk.WORD, height=12, width=62)
    text_box.configure(font=("Helvetica", 14))
    text_box.pack(padx=20, pady=(15, 10), fill=tk.BOTH, expand=True)
    sys.stdout = OutputRedirector(text_box)

    # Status-Label und Feedback-Bild vertikal, mit getauschter Reihenfolge
    feedback_frame = customtkinter.CTkFrame(border_frame, fg_color="transparent")
    feedback_frame.pack(pady=(5, 20))

    status_label = customtkinter.CTkLabel(feedback_frame, text="🟢", font=("Helvetica", 28))
    status_label.pack(pady=(0, 5))

    feedback_image_label = customtkinter.CTkLabel(feedback_frame, text="", image=green_img)
    feedback_image_label.pack()

    # --- Button-Leiste ---
    button_frame = customtkinter.CTkFrame(border_frame, fg_color="transparent")
    button_frame.pack(padx=10, pady=(0, 15))

    start_button = customtkinter.CTkButton(
        button_frame,
        text="▶️ Start",
        width=90,
        font=("Helvetica", 18, "bold"),
        command=start_recognition,
        fg_color="#1F6AA5",
        hover_color="#1C5F91"
    )
    start_button.pack(side=tk.LEFT, padx=(5, 12))

    stop_button = customtkinter.CTkButton(
        button_frame,
        text="⏹️ Stop",
        width=90,
        font=("Helvetica", 18, "bold"),
        command=stop_recognition,
        fg_color="#A52A2A",
        hover_color="#8B0000"
    )
    stop_button.pack(side=tk.LEFT, padx=(12, 12))

    web_button = customtkinter.CTkButton(
        button_frame,
        text="🌐 Webseite öffnen",
        width=160,
        font=("Helvetica", 16, "bold"),
        command=open_website,
        fg_color="#006400",
        hover_color="#005000"
    )
    web_button.pack(side=tk.LEFT, padx=(12, 5))

    root.mainloop()



if __name__ == "__main__":
    threading.Thread(target=start_flask, daemon=True).start()
    setup_gui()
