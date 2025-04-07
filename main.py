from gemini_API import GeminiAPI
from deepgram_STT_API import get_text
from hotkeys import RobustHotkeyManager
from recorder import record_audio
from dotenv import load_dotenv
import time
import subprocess
import os

# getting enviroment variables
GEMINI_API_KEY= os.getenv('GEMINI_API_KEY')
DEEPGRAM_API_KEY= os.getenv('DEEPGRAM_API_KEY')
AUDIO_FILE= os.getenv('AUDIO_FILE')


def send_notification(title, message):
    if os.name != 'nt':
        subprocess.run(['notify-send', title, message])
        
    
    
def run_new_prompt():
    """Record audio, transcribe it, and get a response from Gemini."""
    print("New Prompt started", "AI application has started a new Prompt")
    
    try:
        # Record audio with ctrl+alt+s to stop
        record_audio(filename=AUDIO_FILE, stop_hotkey=["ctrl", "alt", "s"])
        
        # Transcribe the audio
        transcript = get_text(API_KEY=DEEPGRAM_API_KEY, AUDIO_FILE=AUDIO_FILE)

        try:
            os.remove(AUDIO_FILE)
            print("file removed")
        finally:
            pass
        
        if not transcript:
            print("No transcript provided")
            send_notification("AI Assistant", "No transcript detected")
            return
        
        print("transcript: ", transcript)
        
        # Get response from Gemini
        response = GeminiAPI.send_request(transcript, GEMINI_API_KEY=GEMINI_API_KEY)
        print(response)
        send_notification("AI Response", response)
        print("prompt ended")
        print("Press Ctrl + Alt + Win to start a new prompt")
    except Exception as e:
        print(f"Error in prompt processing: {e}")


def main():
    """Main function that sets up the hotkey manager and runs the program."""
    print("AI Assistant starting...")
    print("Press Ctrl+Alt+Win to start a new prompt")
    
    # Create hotkey manager
    hotkey_manager = RobustHotkeyManager()
    hotkey_manager.register("new_prompt", ["ctrl", "alt", "win"], run_new_prompt)
    hotkey_manager.start(debug=False, persistent=True)
    
    try:
        print("AI Assistant is running. Press Ctrl+C to exit.")
        while hotkey_manager.running:
            time.sleep(0.1)
    except KeyboardInterrupt:
        print("\nExiting AI Assistant...")
    finally:
        # Make sure to clean up
        hotkey_manager.stop()

    
if __name__ == "__main__":
    load_dotenv()
    main()
        
        
    
