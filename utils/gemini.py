import os
from dotenv import load_dotenv
from google import genai

load_dotenv()

API_KEY = os.getenv("GOOGLE_API_KEY")

if not API_KEY:
    raise ValueError("GOOGLE_API_KEY not found in .env file")

client = genai.Client(api_key=API_KEY)

MODEL = "gemini-3.6-flash"


def get_answer(context, question):

    prompt = f"""
You are an AI assistant for an interview preparation platform.

Answer the user's question using ONLY the provided context.

CONTEXT:
{context}

QUESTION:
{question}

Instructions:
- Give a clear and accurate answer.
- Use only information supported by the context.
- If the answer is not present in the context, say:
  "The answer is not available in the uploaded notes."
"""

    try:
        response = client.interactions.create(
            model=MODEL,
            input=prompt
        )

        return response.output_text

    except Exception as e:

        error_message = str(e)
        normalized_error = error_message.lower()

        if (
            "429" in error_message
            or "rate" in normalized_error
            or "quota" in normalized_error
            or "resource_exhausted" in normalized_error
        ):
            return (
                "⚠️ Gemini API rate/quota limit reached.\n\n"
                f"{error_message}\n\n"
                "Wait for the retry window or quota reset, or use a project/API "
                "key with available quota."
            )

        return f"❌ Gemini API error: {error_message}"