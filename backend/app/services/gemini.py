import google.generativeai as genai
import asyncio
from app.core.config import settings

class GeminiService:
    def __init__(self):
        if not settings.GOOGLE_API_KEY:
            raise ValueError("GOOGLE_API_KEY is not set in configuration.")
        
        genai.configure(api_key=settings.GOOGLE_API_KEY)
        # Upgraded to Gemini 2.5 Flash for superior performance
        self.model = genai.GenerativeModel('gemini-2.5-flash')

    async def generate_content(self, prompt: str) -> str:
        try:
            # The SDK is synchronous; run it in a thread pool to avoid blocking the event loop
            loop = asyncio.get_event_loop()
            response = await loop.run_in_executor(None, self.model.generate_content, prompt)
            return response.text
        except Exception as e:
            return f"Error communicating with Gemini: {str(e)}"

gemini_service = GeminiService()

