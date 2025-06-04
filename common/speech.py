import whisper
import pyttsx3
import pyaudio
import wave
import numpy as np
import tempfile
import threading


def speak(text):
    engine = pyttsx3.init()
    engine.say(text)
    engine.runAndWait()

# def post_to_web(keyword, text):
#    try:
#        requests.post("http://localhost:5000/api/log", json={"keyword": keyword, "text": text})
#    except Exception as e:
#        print("Fehler beim Web-Post:", e)

def record_audio_chunk(seconds=5, sample_rate=16000, channels=1):
    chunk = 1024
    format = pyaudio.paInt16
    p = pyaudio.PyAudio()

    stream = p.open(format=format,
                    channels=channels,
                    rate=sample_rate,
                    input=True,
                    frames_per_buffer=chunk)

    print("🎙️ Aufnahme läuft...")

    frames = []
    for _ in range(0, int(sample_rate / chunk * seconds)):
        data = stream.read(chunk)
        frames.append(data)

    stream.stop_stream()
    stream.close()
    p.terminate()

    return b''.join(frames), sample_rate

def recognize_speech(KEYWORDS, update_status, stop_event):
    model = whisper.load_model("base")  # oder "tiny", "small" für schnellere Ergebnisse

    print("🧠 Whisper-Spracherkennung gestartet.")

    while not stop_event.is_set():
        try:
            audio_data, sample_rate = record_audio_chunk(seconds=4)

            # Temporäre WAV-Datei schreiben
            with tempfile.NamedTemporaryFile(suffix=".wav", delete=True) as temp_wav:
                wf = wave.open(temp_wav.name, 'wb')
                wf.setnchannels(1)
                wf.setsampwidth(2)  # 16-bit = 2 bytes
                wf.setframerate(sample_rate)
                wf.writeframes(audio_data)
                wf.close()

                result = model.transcribe(temp_wav.name, language="de")
                recognized_text = result["text"].strip().lower()
                print(f"Du hast gesagt: {recognized_text}")

                for keyword in KEYWORDS:
                    if keyword in recognized_text:
                        print(f"Keyword '{keyword}' erkannt.")
                        speak(f"Du hast das Schlüsselwort {keyword} gesagt.")
                        update_status(True)

                        if keyword == "exit":
                            print("Beende Spracherkennung.")
                            stop_event.set()
                            return

        except Exception as e:
            print(f"Fehler bei der Spracherkennung: {e}")

