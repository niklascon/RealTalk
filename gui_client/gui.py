import sys
import threading
import tkinter as tk
import customtkinter as ctk
from tkinter import messagebox
from common.speech import recognize_speech  # Import aus common

#Theme vor der Fenstererzeugung konfigurieren 
ctk.set_appearance_mode("dark")      # "light" oder "dark"
ctk.set_default_color_theme("dark-blue")  # "blue", "green" etc.

KEYWORDS = ["hallo", "exit", "hilfe"]

class App:
    def __init__(self):
        self.recognition_status = False
        self.stop_event = threading.Event()

        #fenster erzeugen
        self.root = ctk.CTk()
        self.root.title("Spracherkennung")
        self.root.geometry("450x300")
        self.root.resizable(False, False)

        #Test label prüfen 
        test_lbl = ctk.CTkLabel(self.root, text="🟢 GUI läuft!", font=("Helvetica", 16))
        test_lbl.pack(pady=10)

        #Textbox
        self.text_box = ctk.CTkTextbox(self.root, wrap=tk.WORD, height=12, width=60)
        self.text_box.configure(font=("Helvetica", 13))
        self.text_box.pack(padx=15, pady=(15, 10), fill=tk.BOTH, expand=True)
        sys.stdout = self.OutputRedirector(self.text_box)

        #Input Frame 
        input_frame = ctk.CTkFrame(master=self.root, fg_color="#2A2D2E", corner_radius=12)
        input_frame.pack(padx=15, pady=(0, 15), fill=tk.X)

        #Label + Entry + Status + Button
        ctk.CTkLabel(input_frame, text="Keywords (kommagetrennt):", 
                     font=("Helvetica", 14, "bold")).pack(anchor="w", padx=10, pady=(10,5))

        self.keywords_entry = ctk.CTkEntry(input_frame, width=300, placeholder_text="z.B. hallo, exit")
        self.keywords_entry.insert(0, ", ".join(KEYWORDS))
        self.keywords_entry.pack(side=tk.LEFT, padx=(10,5), pady=(0,15))

        self.status_label = ctk.CTkLabel(input_frame, text="🔴", font=("Helvetica", 24))
        self.status_label.pack(side=tk.LEFT, padx=(5, 15), pady=(0,15))

        ctk.CTkButton(
            input_frame,
            text="▶️",
            width=50,
            font=("Helvetica", 18),
            command=self.start_recognition,
            fg_color="#1F6AA5",
            hover_color="#1C5F91"
        ).pack(side=tk.LEFT, padx=(0, 15), pady=(0,15))

    def OutputRedirector(self, text_widget):
        class Redirector:
            def __init__(self, widget):
                self.widget = widget
            def write(self, text):
                self.widget.insert(tk.END, text)
                self.widget.see(tk.END)
            def flush(self):
                pass
        return Redirector(text_widget)

    def update_status(self, status: bool):
        self.recognition_status = status
        symbol = "🟢" if status else "🔴"
        self.status_label.configure(text=symbol, fg_color="transparent")

    def start_recognition(self):
        self.update_status(False)
        self.stop_event.clear()
        threading.Thread(
            target=recognize_speech,
            args=(KEYWORDS, self.update_status, self.stop_event),
            daemon=True
        ).start()

    def run(self):
        self.root.mainloop()

if __name__ == "__main__":
    App().run()

