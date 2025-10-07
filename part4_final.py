import os
from google import genai

MODEL = "gemini-2.5-flash"  # Example model name
SYSTEM_PROMPT = "You are a fed up and sassy assistant who hates answering questions."

# Set GEMINI_API_KEY as environment variable before running
gemini_api_key = os.getenv("GEMINI_API_KEY")
if not gemini_api_key:
    raise ValueError("Please set the GEMINI_API_KEY environment variable")

# Initialize Gemini AI client
client = genai.Client()

messages = [{"role": "system", "content": SYSTEM_PROMPT}]

def chat(user_input):
    messages.append({"role": "user", "content": user_input})

    try:
        response = client.models.generate_content(
            model=MODEL,
            contents=user_input
        )
        reply = response.text
    except Exception as e:
        reply = f"Error communicating with Gemini API: {e}"

    messages.append({"role": "assistant", "content": reply})
    return reply

while True:
    user_input = input("You: ")
    if user_input.strip().lower() in {"exit", "quit"}:
        break
    answer = chat(user_input)
    print("Assistant:", answer)
