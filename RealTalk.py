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
from PIL import Image

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

def setup_gui():
    global root, border_frames
    root = customtkinter.CTk()
    root.title("Spracherkennung")

    customtkinter.set_appearance_mode("dark")
    customtkinter.set_default_color_theme("dark-blue")

    root.geometry("450x480")
    root.resizable(False, False)

    global green_img, red_img, feedback_image_label, status_label

    green_img = customtkinter.CTkImage(light_image=Image.open("static/pictures/green_smiley.png"), size=(64, 64))
    red_img = customtkinter.CTkImage(light_image=Image.open("static/pictures/red_smiley.png"), size=(64, 64))

    # 4 schmale Rahmen rund ums Fenster: links, rechts, oben, unten
    border_frames = []
    border_frames.append(customtkinter.CTkFrame(root, width=10, fg_color="transparent"))
    border_frames[-1].pack(side="left", fill="y")
    border_frames.append(customtkinter.CTkFrame(root, width=10, fg_color="transparent"))
    border_frames[-1].pack(side="right", fill="y")
    border_frames.append(customtkinter.CTkFrame(root, height=10, fg_color="transparent"))
    border_frames[-1].pack(side="top", fill="x")
    border_frames.append(customtkinter.CTkFrame(root, height=10, fg_color="transparent"))
    border_frames[-1].pack(side="bottom", fill="x")

    # Textbox zur Ausgabe
    text_box = customtkinter.CTkTextbox(root, wrap=tk.WORD, height=12, width=60)
    text_box.configure(font=("Helvetica", 13))
    text_box.pack(padx=15, pady=(10, 10), fill=tk.BOTH, expand=True)
    sys.stdout = OutputRedirector(text_box)

    # Feedback-Bild initial mit grünem Smiley
    feedback_image_label = customtkinter.CTkLabel(root, text="", image=green_img)
    feedback_image_label.pack(pady=(0, 10))

    # Status-Label (Status-Icon) jetzt direkt im Hauptfenster
    status_label = customtkinter.CTkLabel(root, text="🟢", font=("Helvetica", 24))
    status_label.pack(pady=(0, 15))

    # --- Button-Leiste ---
    button_frame = customtkinter.CTkFrame(master=root, fg_color="transparent")
    button_frame.pack(padx=15, pady=(0, 15))

    start_button = customtkinter.CTkButton(
        button_frame,
        text="▶️ Start",
        width=80,
        font=("Helvetica", 18),
        command=start_recognition,
        fg_color="#1F6AA5",
        hover_color="#1C5F91"
    )
    start_button.pack(side=tk.LEFT, padx=(5, 10))

    stop_button = customtkinter.CTkButton(
        button_frame,
        text="⏹️ Stop",
        width=80,
        font=("Helvetica", 18),
        command=stop_recognition,
        fg_color="#A52A2A",
        hover_color="#8B0000"
    )
    stop_button.pack(side=tk.LEFT, padx=(10, 5))

    root.mainloop()


if __name__ == "__main__":
    threading.Thread(target=start_flask, daemon=True).start()
    setup_gui()
