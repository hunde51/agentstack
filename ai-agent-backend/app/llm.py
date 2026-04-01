import os
from dotenv import load_dotenv
import google.generativeai as genai

load_dotenv()

genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
model = genai.GenerativeModel("gemini-2.5-flash")

def get_ai_response(user_message: str):
    prompt = (
        "You are a senior backend engineer. "
        "Answer clearly and technically.\n\n"
        f"User: {user_message}"
    )
    response = model.generate_content(prompt)
    return response.text