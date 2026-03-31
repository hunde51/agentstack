from openai import OpenAI
import os
from dotenv import load_dotenv

load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def get_ai_response(user_message: str):
    response = client.chat.completions.create(
        model="gpt-4.1",
        messages=[
            {
                "role": "system",
                "content": "You are a senior backend engineer. Answer clearly and technically."
            },
            {
                "role": "user",
                "content": user_message
            }
        ],
        temperature=0.3
    )

    return response.choices[0].message.content