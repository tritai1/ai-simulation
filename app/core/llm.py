import google.generativeai as genai

from app.core.config import GEMINI_API_KEY


genai.configure(
    api_key=GEMINI_API_KEY
)


model = genai.GenerativeModel(
    "gemini-2.5-flash"
)