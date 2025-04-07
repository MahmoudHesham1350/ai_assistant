from google import genai
import speech_recognition as sr
import time
from pynput import keyboard
import pyttsx3
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

class VoiceAssistant:
    def __init__(self):
        self.is_listening = False
        self.recognizer = sr.Recognizer()
        self.microphone = sr.Microphone()
        self.recognized_texts = []  # Store all recognized texts
        self.ctrl_pressed = False
        self.alt_pressed = False
        self.win_pressed = False
        self.should_stop = False
        
        # Initialize text-to-speech engine
        self.engine = pyttsx3.init()
        self.engine.setProperty('rate', 150)  # Speed of speech
        
        # Configure recognizer settings
        self.recognizer.dynamic_energy_threshold = True
        self.recognizer.energy_threshold = 300  # Increase sensitivity
        self.recognizer.pause_threshold = 1.0  # Wait longer for speech to end
        
    def speak(self, text):
        print(text)  # Still print for reference
        self.engine.say(text)
        self.engine.runAndWait()

    def on_press(self, key):
        try:
            if key == keyboard.Key.ctrl_l or key == keyboard.Key.ctrl_r:
                self.ctrl_pressed = True
            elif key == keyboard.Key.alt_l or key == keyboard.Key.alt_r:
                self.alt_pressed = True
            elif key == keyboard.Key.cmd:  # Windows key
                self.win_pressed = True
            elif key == keyboard.Key.esc:
                self.should_stop = True
                self.is_listening = False
                self.speak("Stopped listening.")
                return False  # Stop the listener

            # Check for Ctrl+Alt+Win combination
            if self.ctrl_pressed and self.alt_pressed and self.win_pressed:
                self.is_listening = True
                self.speak("Started listening...")
        except AttributeError:
            pass

    def on_release(self, key):
        try:
            if key == keyboard.Key.ctrl_l or key == keyboard.Key.ctrl_r:
                self.ctrl_pressed = False
            elif key == keyboard.Key.alt_l or key == keyboard.Key.alt_r:
                self.alt_pressed = False
            elif key == keyboard.Key.cmd:  # Windows key
                self.win_pressed = False
        except AttributeError:
            pass

    def start_listening(self):
        with self.microphone as source:
            print("Adjusting for ambient noise...")
            self.recognizer.adjust_for_ambient_noise(source, duration=2)  # Longer adjustment
            print("Press Ctrl+Alt+Win to start listening, Esc to stop...")
            
            # Start the keyboard listener
            with keyboard.Listener(on_press=self.on_press, on_release=self.on_release) as listener:
                while not self.should_stop:
                    if self.is_listening:
                        try:
                            print("Listening...")
                            audio = self.recognizer.listen(source, timeout=None, phrase_time_limit=50)  # No timeout, max 30 seconds per phrase
                            text = self.recognizer.recognize_google(audio)
                            print(f"You said: {text}")
                            self.recognized_texts.append(text)  # Store the recognized text
                        except sr.WaitTimeoutError:
                            continue
                        except sr.UnknownValueError:
                            self.speak("B")
                        except sr.RequestError as e:
                            self.speak(f"Could not request results: exiting")
                            exit()
                    time.sleep(0.1)  # Reduce CPU usage

        # After stopping, combine all texts and send to Gemini
        if self.recognized_texts:
            combined_text = " ".join(self.recognized_texts)
            print("Sending all recognized text to Gemini...")
            response = send_to_gemini(combined_text)
            print("Gemini Response: " + response)
            return combined_text
        return None

def send_to_gemini(text):
    api_key = os.getenv('GEMINI_API_KEY')
    if not api_key:
        raise ValueError("GEMINI_API_KEY not found in environment variables")
        
    client = genai.Client(api_key=api_key)
    response = client.models.generate_content(
        model="gemini-2.0-flash",
        contents=text,
    )
    return response.text

if __name__ == "__main__":
    assistant = VoiceAssistant()
    assistant.start_listening()


