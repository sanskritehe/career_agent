import os
from dotenv import load_dotenv
from groq import Groq

# Load variables from .env
load_dotenv()

# Get the key from environment variables
api_key = os.getenv("GROQ_API_KEY")

client = Groq(api_key=api_key)

def call_llm(prompt):
    try:
        chat_completion = client.chat.completions.create(
            messages=[
                {"role": "system", "content": "You are a professional recruiter. Return ONLY valid JSON."},
                {"role": "user", "content": prompt}
            ],
            model="llama-3.3-70b-versatile",
            response_format={"type": "json_object"},
            temperature=0.0  # Kept at 0 for score consistency!
        )
        return chat_completion.choices[0].message.content
    except Exception as e:
        return f'{{"error": "{str(e)}"}}'