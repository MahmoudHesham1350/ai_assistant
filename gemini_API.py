from google import genai
from dotenv import load_dotenv
from google.genai.types import GenerateContentConfig
import os
import sys


class GeminiAPI:
    """Handles communication with the Gemini API."""
    @staticmethod
    def send_request(text, GEMINI_API_KEY):
        """Send text to Gemini API and get response."""
        if not GEMINI_API_KEY:
            raise ValueError("GEMINI_API_KEY not found in environment variables")
            
        client = genai.Client(api_key=GEMINI_API_KEY)
        response = client.models.generate_content(
        model="gemini-2.0-flash",
        contents=text,
        config=GenerateContentConfig(
            temperature=0.3,
            max_output_tokens=30,
            system_instruction="Respond concisely and clearly."
            )
        )
        return response.text


if __name__ == "__main__":
    # Load environment variables
    load_dotenv()
    text = " ".join(sys.argv[1:])
    print(GeminiAPI.send_request(text=text, GEMINI_API_KEY=os.getenv('GEMINI_API_KEY')))




