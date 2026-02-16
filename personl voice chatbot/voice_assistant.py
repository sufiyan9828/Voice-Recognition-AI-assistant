import tkinter as tk
import customtkinter as ctk
import speech_recognition as sr
import pyttsx3
import datetime
import wikipedia
import webbrowser
import os
import threading
from PIL import Image

# Set the theme for CustomTkinter
ctk.set_appearance_mode("System")  # Modes: "System" (standard), "Dark", "Light"
ctk.set_default_color_theme("blue")  # Themes: "blue" (standard), "green", "dark-blue"


class VoiceAssistantApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        # Configure window
        self.title("Voice Assistant")
        self.geometry("600x500")

        # Initialize core components
        self.engine = pyttsx3.init("sapi5")
        self.voices = self.engine.getProperty("voices")
        # Set to female voice if available
        try:
            self.engine.setProperty("voice", self.voices[1].id)
        except IndexError:
            self.engine.setProperty("voice", self.voices[0].id)

        self.is_listening = False

        # GUI Layout
        self.create_widgets()

        # Start the greeting in a separate thread so it doesn't block UI
        threading.Thread(target=self.wish_me, daemon=True).start()

    def create_widgets(self):
        # Title Label
        self.label_title = ctk.CTkLabel(
            self, text="AI Voice Assistant", font=ctk.CTkFont(size=24, weight="bold")
        )
        self.label_title.pack(pady=20)

        # Chat History (Scrollable Textbox)
        self.textbox = ctk.CTkTextbox(
            self, width=500, height=300, font=ctk.CTkFont(size=14)
        )
        self.textbox.pack(pady=10)
        self.textbox.configure(state="disabled")  # Read-only initially

        # Status Label
        self.label_status = ctk.CTkLabel(
            self, text="Ready", font=ctk.CTkFont(size=14, slant="italic")
        )
        self.label_status.pack(pady=5)

        # Action Buttons
        self.frame_buttons = ctk.CTkFrame(self)
        self.frame_buttons.pack(pady=20)

        self.btn_listen = ctk.CTkButton(
            self.frame_buttons, text="Start Listening", command=self.toggle_listening
        )
        self.btn_listen.grid(row=0, column=0, padx=10)

        self.btn_clear = ctk.CTkButton(
            self.frame_buttons,
            text="Clear Chat",
            fg_color="gray",
            command=self.clear_chat,
        )
        self.btn_clear.grid(row=0, column=1, padx=10)

        self.btn_exit = ctk.CTkButton(
            self.frame_buttons,
            text="Exit",
            fg_color="red",
            hover_color="darkred",
            command=self.close_app,
        )
        self.btn_exit.grid(row=0, column=2, padx=10)

    def log(self, message, is_user=False):
        """Append text to the textbox."""
        self.textbox.configure(state="normal")
        if is_user:
            self.textbox.insert("end", f"You: {message}\n\n")
        else:
            self.textbox.insert("end", f"Assistant: {message}\n\n")
        self.textbox.see("end")  # Auto-scroll to bottom
        self.textbox.configure(state="disabled")

    def speak(self, text):
        """Speak text and log it to GUI."""
        self.label_status.configure(text="Speaking...")
        self.log(text)
        self.engine.say(text)
        self.engine.runAndWait()
        self.label_status.configure(text="Ready")

    def wish_me(self):
        hour = int(datetime.datetime.now().hour)
        if 0 <= hour < 12:
            greeting = "Good Morning!"
        elif 12 <= hour < 18:
            greeting = "Good Afternoon!"
        else:
            greeting = "Good Evening!"

        self.speak(
            f"{greeting} I am your Voice Assistant. Click 'Start Listening' to begin."
        )

    def toggle_listening(self):
        if not self.is_listening:
            self.is_listening = True
            self.btn_listen.configure(text="Stop Listening", fg_color="orange")
            # Start listening loop in a background thread
            threading.Thread(target=self.listen_loop, daemon=True).start()
        else:
            self.is_listening = False
            self.btn_listen.configure(
                text="Start Listening", fg_color=["#3B8ED0", "#1F6AA5"]
            )  # Default blue
            self.label_status.configure(text="Stopped")

    def listen_loop(self):
        while self.is_listening:
            query = self.take_command()
            if query == "None":
                continue

            query = query.lower()
            self.process_command(query)

    def take_command(self):
        r = sr.Recognizer()
        with sr.Microphone() as source:
            self.label_status.configure(text="Listening...")
            # r.adjust_for_ambient_noise(source, duration=0.5)
            r.pause_threshold = 1
            try:
                audio = r.listen(source, timeout=5, phrase_time_limit=5)
            except sr.WaitTimeoutError:
                return "None"

        try:
            self.label_status.configure(text="Recognizing...")
            query = r.recognize_google(audio, language="en-in")
            self.log(query, is_user=True)
        except Exception:
            # Don't speak "not understood" on every loop to avoid spamming
            return "None"

        return query

    def process_command(self, query):
        if "wikipedia" in query:
            self.speak("Searching Wikipedia...")
            query = query.replace("wikipedia", "")
            try:
                results = wikipedia.summary(query, sentences=2)
                self.speak("According to Wikipedia")
                self.speak(results)
            except Exception:
                self.speak("Could not find results on Wikipedia.")

        elif "open youtube" in query:
            self.speak("Opening YouTube")
            webbrowser.open("youtube.com")

        elif "open google" in query:
            self.speak("Opening Google")
            webbrowser.open("google.com")

        elif "open stackoverflow" in query:
            self.speak("Opening Stack Overflow")
            webbrowser.open("stackoverflow.com")

        elif "the time" in query:
            strTime = datetime.datetime.now().strftime("%H:%M:%S")
            self.speak(f"Sir, the time is {strTime}")

        elif "hello" in query:
            self.speak("Hello! How can I help you?")

        elif "how are you" in query:
            self.speak("I am fine, thank you. How are you?")

        elif "quit" in query or "exit" in query or "bye" in query:
            self.speak("Goodbye! Have a nice day.")
            self.close_app()

        else:
            self.speak(
                "I'm not sure specifically what to do with that, but I can search google for "
                + query
            )
            webbrowser.open(f"https://www.google.com/search?q={query}")

    def clear_chat(self):
        self.textbox.configure(state="normal")
        self.textbox.delete("1.0", "end")
        self.textbox.configure(state="disabled")

    def close_app(self):
        self.is_listening = False
        self.destroy()
        os._exit(0)


if __name__ == "__main__":
    app = VoiceAssistantApp()
    app.mainloop()
