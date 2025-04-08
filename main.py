from gemini_API import GeminiAPI
from deepgram_STT_API import get_text
from recorder import record_audio
from dotenv import load_dotenv
from pynput import keyboard
import subprocess
import os

# getting environment variables
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')
DEEPGRAM_API_KEY = os.getenv('DEEPGRAM_API_KEY')
AUDIO_FILE = os.getenv('AUDIO_FILE')


def send_notification(title, message):
    if os.name != 'nt':
        subprocess.run(['notify-send', title, message])


def audio_transcription():
    try:
        transcription = get_text(API_KEY=DEEPGRAM_API_KEY, AUDIO_FILE=AUDIO_FILE)
        if transcription:
            return transcription
        else:
            send_notification("AI Assistant", "No transcription result")
            return None
    except Exception as e:
        send_notification("AI Assistant Error", str(e))
        return None


def get_gemini_response(transcript):
    try:
        response = GeminiAPI.send_request(transcript, GEMINI_API_KEY=GEMINI_API_KEY)
        if response:
            return response
        else:
            send_notification("AI Assistant", "No response from Gemini")
            return None
    except Exception as e:
        send_notification("AI Assistant Error", str(e))
        return None


def run_new_prompt():
    """Record audio, transcribe it, and get a response from Gemini."""
    send_notification("Recording... ", "Press Ctrl+Alt+Q to stop")
    record_audio(filename=AUDIO_FILE, duration=None)

    send_notification("Recording complete,", " transcribing...")
    transcription = audio_transcription()
    os.remove(AUDIO_FILE)  # Clean up the audio file after transcription

    if transcription is not None:
        send_notification("Transcription complete,", "getting response...")
        response = get_gemini_response(transcription)
        if response:
            send_notification("AI Response:", response)
    return None


def main():
    """Main function that sets up the hotkey manager and runs the program."""
    send_notification("AI Assistant running...",  "Press Ctrl+Alt+N for new prompt, \nCtrl+C to quit")
    
    with keyboard.GlobalHotKeys({
        '<ctrl>+<alt>+n': run_new_prompt,
    }) as h:
        try:
            h.join()
        except KeyboardInterrupt:
            send_notification("AI Assistant", "Shutting down...")


if __name__ == "__main__":
    load_dotenv()
    main()



