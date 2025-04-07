import os
from dotenv import load_dotenv
from deepgram import (
    DeepgramClient,
    PrerecordedOptions,
    FileSource,
)

def get_text(API_KEY, AUDIO_FILE):
    try:
        # STEP 1 Create a Deepgram client using the API key
        deepgram = DeepgramClient(api_key=API_KEY)

        with open(AUDIO_FILE, "rb") as file:
            buffer_data = file.read()

        payload: FileSource = {
            "buffer": buffer_data,
        }

        #STEP 2: Configure Deepgram options for audio analysis
        options = PrerecordedOptions(
            model="nova-3",
            smart_format=True,
            language='en',
            filler_words=True,
            punctuate=False
        )
        # STEP 3: Call the transcribe_file method with the text payload and options
        response = deepgram.listen.rest.v("1").transcribe_file(payload, options)
        # STEP 4: return the response
        return response['results']['channels'][0]['alternatives'][0]['transcript']
    except Exception as e:
        print(f"Exception: {e}")

if __name__ == "__main__":
    load_dotenv()
    print(get_text(API_KEY=os.getenv('DEEPGRAM_API_KEY'), AUDIO_FILE=os.getenv('AUDIO_FILE', 'output.wav')))
