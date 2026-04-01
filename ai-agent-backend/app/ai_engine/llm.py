import os
import json
from dotenv import load_dotenv
import google.generativeai as genai

load_dotenv()

genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
model = genai.GenerativeModel("gemini-2.5-flash")


def get_ai_response(chat_history: list[dict], user_memory: dict):
    # Build simple context blocks the model can reliably parse.
    memory_block = json.dumps(user_memory or {}, ensure_ascii=True)
    history_lines = []
    for message in chat_history:
        role = message.get("role", "user")
        content = message.get("content", "")
        history_lines.append(f"{role}: {content}")
    history_block = "\n".join(history_lines)

    prompt = f"""
You are an action selector for a backend API.

You must NEVER answer normally.
You must ONLY return valid JSON with this exact shape:
{{
  "action": "string",
  "params": {{}}
}}

Allowed actions:
1) get_users
   - params must be {{}}
2) get_weather
   - params must be {{"city": "<city name>"}}

Pick the single best action based on the user message.
Return JSON only. No markdown. No explanation.

Long-term user memory (JSON): {memory_block}

Conversation history:
{history_block}
"""
    response = model.generate_content(
        prompt,
        generation_config={"response_mime_type": "application/json"},
    )
    return response.text
