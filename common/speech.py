import speech_recognition as sr
import pyttsx3
import smtplib
import time
import requests
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

def speak(text):
    engine = pyttsx3.init()
    engine.say(text)
    engine.runAndWait()

def post_to_web(keyword, text):
    try:
        requests.post("http://localhost:5000/api/log", json={"keyword": keyword, "text": text})
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

def recognize_speech(KEYWORDS, update_status, stop_event):
    recognizer = sr.Recognizer()
    microphone = sr.Microphone()

    print("Rauschen kalibrieren...")
    with microphone as source:
        recognizer.adjust_for_ambient_noise(source, duration=1)

    print("Spracherkennung gestartet.")

    while not stop_event.is_set():
        try:
            with microphone as source:
                print("Höre...")
                audio = recognizer.listen(source, timeout=5)

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
                        print("Beende Spracherkennung.")
                        stop_event.set()
                        return

        except sr.UnknownValueError:
            print("Konnte Sprache nicht erkennen.")
        except sr.RequestError as e:
            print(f"Spracherkennungsfehler: {e}")
        except Exception as e:
            print(f"Allgemeiner Fehler: {e}")

