# Voice Assistant with Gemini AI

A simple voice assistant that records your speech, transcribes it using Deepgram, and gets responses from Google's Gemini AI.

## Architecture

This application consists of several key components:
- **Audio Recording**: Uses `sounddevice` to capture audio from your microphone
- **Hotkey Management**: Custom hotkey handling with `pynput` for controlling the application
- **Speech-to-Text**: Deepgram AI API for fast and accurate transcription
- **AI Processing**: Google Gemini AI for generating intelligent responses

## Detailed Setup

### Prerequisites
- Python 3.8 or higher
- Working microphone
- API keys for Deepgram and Google Gemini

### Installation

1. Clone the repository:
   ```
   git clone <repository-url>
   cd <repository-directory>
   ```

2. Create and activate a virtual environment (recommended):
   ```
   # On Windows
   python -m venv env
   env\Scripts\activate

   # On macOS/Linux
   python3 -m venv env
   source env/bin/activate
   ```

3. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

4. Set up API keys in a `.env` file:
   ```
   GEMINI_API_KEY=your_gemini_api_key
   DEEPGRAM_API_KEY=your_deepgram_api_key
   AUDIO_FILE=output.wav
   ```

### How to Get API Keys

- **Deepgram API Key**: Sign up at [Deepgram Console](https://console.deepgram.com/), create a new project, and generate an API key.
- **Google Gemini API Key**: Visit [Google AI Studio](https://ai.google.dev/), sign in with your Google account, navigate to API keys, and create a new key.

## How to Use

1. Run the assistant:
   ```
   python main.py
   ```

2. The application will start and run in the background.
3. Press **Ctrl+Alt+Win** to start a new voice prompt.
4. Speak your question or command clearly.
5. Press **Ctrl+Alt+S** to stop recording.
6. The application will transcribe your speech and send it to Gemini AI.
7. View the AI response in the terminal.

## Customization

### Changing Hotkeys

You can modify the hotkeys in `main.py`:
- To change the prompt activation hotkey, edit the `hotkey_manager.register()` call in the `main()` function.
- To change the recording stop hotkey, modify the `stop_hotkey` parameter in the `record_audio()` call.

### Modifying AI Settings

- **Gemini AI**: Adjust response settings in `gemini_API.py` by changing the `temperature` (0.0-1.0) and other parameters.
- **Deepgram STT**: Customize transcription settings in `Deepgram_STT_API.py` by modifying the `PrerecordedOptions`.

## Troubleshooting

### Common Issues

1. **No audio recording**:
   - Check that your microphone is connected and set as the default device
   - Ensure you have the necessary permissions for microphone access

2. **Hotkeys not working**:
   - Some keyboard layouts or system configurations might require different key combinations
   - Try running the application with administrator privileges on Windows

3. **API errors**:
   - Verify your API keys are correctly entered in the `.env` file
   - Check your internet connection

### Debug Mode

To enable debug logging for hotkeys, modify the `hotkey_manager.start()` call in `main.py`:
```python
hotkey_manager.start(debug=True, persistent=True)
```

## Features

- Hotkey activation (no need to interact with the terminal)
- Speech-to-text with Deepgram AI
- AI responses from Google Gemini
- Audio file is automatically deleted after use
- Cross-platform compatibility (Windows, macOS, Linux)
- Customizable hotkeys and AI settings

## Requirements

- Python 3.8+
- A Deepgram API key
- A Google Gemini API key
- Sound input device
- Network connection for API access 