import sounddevice as sd
import numpy as np
import wave
import os
import time
from dotenv import load_dotenv
from hotkeys import RobustHotkeyManager

# Load environment variables at module level
load_dotenv()

class AudioRecorder:
    """Simple class for recording audio using sounddevice."""
    
    def __init__(self, filename, samplerate=44100, channels=1, dtype=np.int16):
        self.filename = filename
        self.samplerate = samplerate
        self.channels = channels
        self.dtype = dtype
        self.frames = []
        self.stream = None
    
    def callback(self, indata, frame_count, time, status):
        """Store audio data as it comes in."""
        self.frames.append(indata.copy())
    
    def start_recording(self):
        """Start audio recording."""
        self.frames = []
        self.stream = sd.InputStream(
            samplerate=self.samplerate,
            channels=self.channels,
            dtype=self.dtype,
            callback=self.callback
        )
        self.stream.start()
    
    def stop_recording(self):
        """Stop audio recording."""
        if self.stream:
            self.stream.stop()
            self.stream.close()
            self.stream = None
    
    def save_to_file(self):
        """Save recorded audio to a WAV file."""
        
        if not self.frames:
            raise ValueError('No Audio Recorded')
        
        # Concatenate frames and save to file
        audio_data = np.concatenate(self.frames, axis=0)
        with wave.open(self.filename, 'wb') as wf:
            wf.setnchannels(self.channels)
            wf.setsampwidth(np.dtype(self.dtype).itemsize)
            wf.setframerate(self.samplerate)
            wf.writeframes(audio_data.tobytes())
        
        return self.filename
    
    def get_audio_data(self):
        """Return the recorded audio data as a numpy array."""
        if not self.frames:
            return None
        return np.concatenate(self.frames, axis=0)


def record_audio(filename, duration=None, stop_hotkey=["ctrl", "alt", "s"]):
    """
    Record audio for a specified duration or until a hotkey is pressed.
    
    Args:
        filename: The path where to save the audio file
        duration: Recording duration in seconds (None for manual stop)
        stop_hotkey: List of key names for the hotkey to stop recording (default: Ctrl+S)
        
    Returns:
        Path to the saved audio file
    """
    recorder = AudioRecorder(filename=filename)
    recording_active = True
    
    # Create a function to handle the stop hotkey
    def stop_recording():
        nonlocal recording_active
        recording_active = False
        print("Recording stopped by hotkey.")
    
    # Set up the hotkey manager
    hotkey_manager = RobustHotkeyManager()
    hotkey_manager.register("stop_recording", stop_hotkey, stop_recording)
    hotkey_manager.start(debug=False, persistent=True)
    
    # Start recording
    recorder.start_recording()
    print(f"Recording... Press {'+'.join(stop_hotkey)} to stop.")
    
    try:
        if duration is None:
            # Record until hotkey is pressed
            while recording_active:
                time.sleep(0.1)  # Check every 100ms and keep CPU usage low
        else:
            # Record for specified duration or until hotkey is pressed
            time_start = time.time()
            while time.time() - time_start < duration and recording_active:
                time.sleep(0.1)
    finally:
        # Stop the hotkey manager
        hotkey_manager.stop()
        
        # Stop recording and save
        recorder.stop_recording()
        return recorder.save_to_file()


if __name__ == "__main__":
    # Load environment variables once at module level
    load_dotenv()
    record_audio(filename=os.getenv('AUDIO_FILE', 'output.wav'))
