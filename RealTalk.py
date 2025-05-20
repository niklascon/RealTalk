import speech_recognition as sr
import pyttsx3
import tkinter as tk
import sys
import threading
import customtkinter
import smtplib
import time
import requests
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from tkinter import messagebox

from flask import Flask, render_template, request, jsonify

recognition_status = False
KEYWORDS = ["hallo", "exit", "hilfe"]

# --- Flask Webserver ---
app = Flask(__name__)
last_result = {"keyword": "", "text": ""}

@app.route('/')
def welcome():
    return render_template('welcome.html')

@app.route('/current')
def current():
    return render_template('current.html', last_result=last_result)

@app.route('/overview')
def overview():
    return render_template('overview.html')

@app.route('/api/log', methods=['POST'])
def log_result():
    data = request.json
    last_result["keyword"] = data.get("keyword", "")
    last_result["text"] = data.get("text", "")
    return jsonify({"status": "ok"})

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
    recognizer = sr.Recognizer()
    microphone = sr.Microphone()

    print("Rauschen kalibrieren...")
    with microphone as source:
        recognizer.adjust_for_ambient_noise(source, duration=1)

    print("Spracherkennung gestartet.")

    while True:
        try:
            with microphone as source:
                print("Höre...")
                audio = recognizer.listen(source)

            recognized_text = recognizer.recognize_google(audio, language="de-DE,en-US").lower()
            print(f"Du hast gesagt: {recognized_text}")

            for keyword in KEYWORDS:
                if keyword in recognized_text:
                    print(f"Keyword '{keyword}' erkannt.")
                    speak(f"Du hast das Schlüsselwort {keyword} gesagt.")
                    send_email_to_self("Selbst-Erinnerung", f"Erkannt: {recognized_text}")
                    post_to_web(keyword, recognized_text)
                    update_status(True)

                    if keyword == "exit":
                        print("Beende Programm.")
                        return

        except sr.UnknownValueError:
            print("Konnte Sprache nicht erkennen.")
        except sr.RequestError as e:
            print(f"Spracherkennungsfehler: {e}")

def update_status(status):
    global recognition_status
    recognition_status = status
    if status:
        status_label.configure(text="🟢", fg_color="transparent")
    else:
        status_label.configure(text="🔴", fg_color="transparent")

def start_recognition():
    update_status(False)
    threading.Thread(target=recognize_speech, daemon=True).start()

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

def setup_gui():
    root = customtkinter.CTk()
    root.title("Spracherkennung")

    customtkinter.set_appearance_mode("dark")
    customtkinter.set_default_color_theme("dark-blue")

    root.geometry("450x300")
    root.resizable(False, False)

    text_box = customtkinter.CTkTextbox(root, wrap=tk.WORD, height=12, width=60)
    text_box.configure(font=("Helvetica", 13))
    text_box.pack(padx=15, pady=(15, 10), fill=tk.BOTH, expand=True)
    sys.stdout = OutputRedirector(text_box)

    input_frame = customtkinter.CTkFrame(master=root, fg_color="#2A2D2E", corner_radius=12)
    input_frame.pack(padx=15, pady=(0, 15), fill=tk.X)

    label = customtkinter.CTkLabel(input_frame, text="Keywords (kommagetrennt):", font=("Helvetica", 14, "bold"))
    label.pack(anchor="w", padx=10, pady=(10, 5))

    global keywords_entry
    keywords_entry = customtkinter.CTkEntry(input_frame, width=300, placeholder_text="z.B. hallo, exit")
    keywords_entry.insert(0, ", ".join(KEYWORDS))
    keywords_entry.pack(side=tk.LEFT, padx=(10,5), pady=(0,15))

    global status_label
    status_label = customtkinter.CTkLabel(input_frame, text="🔴", font=("Helvetica", 24))
    status_label.pack(side=tk.LEFT, padx=(5, 15), pady=(0,15))

    start_button = customtkinter.CTkButton(
        input_frame,
        text="▶️",
        width=50,
        font=("Helvetica", 18),
        command=start_recognition,
        fg_color="#1F6AA5",
        hover_color="#1C5F91"
    )
    start_button.pack(side=tk.LEFT, padx=(0, 15), pady=(0,15))

    root.mainloop()

if __name__ == "__main__":
    threading.Thread(target=start_flask, daemon=True).start()
    setup_gui()
