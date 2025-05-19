import speech_recognition as sr
import pyttsx3
import tkinter as tk
import sys
import threading
import customtkinter
import smtplib
import time
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from tkinter import messagebox

# Initialize text-to-speech (Optional)
def speak(text):
    engine = pyttsx3.init()
    engine.say(text)
    engine.runAndWait()

# Global variable to store keywords
KEYWORDS = ["input keywords..."]

# Custom Output Redirector
class OutputRedirector:
    def __init__(self, text_widget):
        self.text_widget = text_widget

    def write(self, text):
        self.text_widget.insert(tk.END, text)
        self.text_widget.see(tk.END)  # Scroll to the latest output

    def flush(self):
        pass  # Required for compatibility with sys.stdout

def send_email_to_self(subject, body):
    # Your iCloud email and app-specific password
    sender_email = "maxi.schw@icloud.com"
    receiver_email = "maxi.schw@icloud.com"  # Sending to yourself
    app_specific_password = "jwhj-safe-ojwh-evvf"

    # Set up the email content
    msg = MIMEMultipart()
    msg['From'] = sender_email
    msg['To'] = receiver_email
    msg['Subject'] = subject

    # Email body
    msg.attach(MIMEText(body, 'plain'))

    # Connect to iCloud SMTP server
    try:
        with smtplib.SMTP_SSL("smtp.mail.me.com", 465) as server:
            time.sleep(1) 
            server.login(sender_email, app_specific_password)
            server.sendmail(sender_email, receiver_email, msg.as_string())
            print("Email sent successfully!")
    except Exception as e:
        print(f"Failed to send email: {e}")

# Speech recognition function
def recognize_speech():
    recognizer = sr.Recognizer()
    microphone = sr.Microphone()

    print("Adjusting for ambient noise... Please wait.")
    with microphone as source:
        recognizer.adjust_for_ambient_noise(source, duration=1)
    print("Listening for keywords...")

    while True:
        try:
            with microphone as source:
                print("Listening...")
                audio = recognizer.listen(source)
    
            # Recognize speech using Google Web Speech API
            recognized_text = recognizer.recognize_google(audio, language="de-DE,en-US").lower()
            print(f"You said: {recognized_text}")

            # Check for keywords
            for keyword in KEYWORDS:
                if keyword in recognized_text:
                    print(f"Keyword '{keyword}' detected!")
                    speak(f"You said the keyword {keyword}.")
                    send_email_to_self("Self Reminder", "This is a test message to myself!")
                    
                    if keyword == "exit":
                        print("Exiting program.")
                        return

        except sr.UnknownValueError:
            print("Sorry, could not understand the audio.")
        except sr.RequestError as e:
            print(f"Could not request results from the speech recognition service; {e}")

# Start speech recognition in a separate thread
def start_recognition():
    recognition_thread = threading.Thread(target=recognize_speech)
    recognition_thread.daemon = True
    recognition_thread.start()

# Function to update keywords
def update_keywords():
    global KEYWORDS
    keywords_input = keywords_entry.get().strip()
    if keywords_input:
        KEYWORDS = [kw.strip().lower() for kw in keywords_input.split(",") if kw.strip()]
        messagebox.showinfo("Keywords Updated", f"Keywords have been updated to: {', '.join(KEYWORDS)}")
    else:
        messagebox.showwarning("Input Error", "Please enter valid keywords.")

# GUI Setup
def setup_gui():
    root = customtkinter.CTk()
    root.title("Speech Recognition Output")

    customtkinter.set_appearance_mode("System")
    customtkinter.set_default_color_theme("dark-blue")
    # Position the window in the top-right corner
    window_width, window_height = 400, 200
    screen_width = root.winfo_screenwidth()
    x_position = screen_width - window_width - 10
    y_position = 10
    root.geometry(f"{window_width}x{window_height}+{x_position}+{y_position}")

    # Disable resizing
    root.resizable(True, True)

    # Output text box
    text_box = customtkinter.CTkTextbox(root, wrap=tk.WORD, height=10, width=50)
    text_box.configure(font=("Sans Serif", 12, "bold"))
    text_box.pack(fill=tk.BOTH, expand=True, pady=(5, 0))

    # Redirect print statements to the text box
    sys.stdout = OutputRedirector(text_box)

    # Frame to hold input and button
    input_frame = customtkinter.CTkFrame(master=root, fg_color= "transparent")
    input_frame.pack(pady = 20)

    global keywords_entry
    keywords_entry = customtkinter.CTkEntry(input_frame, width=200, fg_color= "transparent", font=("Sans Serif", 12, "bold") )
    keywords_entry.insert(0, ", ".join(KEYWORDS))  # Pre-fill with current keywords
    keywords_entry.pack(pady = 5)


    # Update button
    update_button = customtkinter.CTkButton(input_frame, text="Update Keywords", command=update_keywords)
    update_button.configure(font=("Sans Serif", 12, "bold"))
    update_button.pack(pady = 5)

    # Start recognition button
    start_button = customtkinter.CTkButton(input_frame, text="Start Recognition", command=start_recognition)
    start_button.configure(font=("Sans Serif", 12, "bold"))
    start_button.pack(pady = 5)

    # Run the GUI event loop
    root.mainloop()

# Run the GUI setup
if __name__ == "__main__":
    setup_gui()
