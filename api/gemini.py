
import os
import time
from groq import Groq
from groq import APIError, RateLimitError


def generate_gemini_response(prompt: str) -> dict:
    """
    Generates an AI response using Groq.
    Keeps the existing function name so api/views.py
    does not need to change yet.
    """

    api_key = os.getenv("GROQ_API_KEY")

    if not api_key:
        return {
            "success": False,
            "error": "GROQ_API_KEY is missing from environment variables."
        }

    try:
        client = Groq(api_key=api_key)

        max_retries = 3

        for attempt in range(max_retries):
            try:
                response = client.chat.completions.create(
                    model="openai/gpt-oss-20b",
                    messages=[
                        {
                            "role": "user",
                            "content": prompt
                        }
                    ],
                    temperature=0.3,
                    max_completion_tokens=1024
                )

                text = response.choices[0].message.content

                return {
                    "success": True,
                    "text": text or ""
                }

            except RateLimitError as e:
                if attempt < max_retries - 1:
                    time.sleep(2 ** attempt)
                    continue

                return {
                    "success": False,
                    "error": "Groq rate limit reached. Please try again later."
                }

            except APIError as e:
                status_code = getattr(e, "status_code", None)

                if status_code and status_code >= 500:
                    if attempt < max_retries - 1:
                        time.sleep(2 ** attempt)
                        continue

                return {
                    "success": False,
                    "error": f"Groq API error: HTTP {status_code or 'unknown'}. Check the server logs."
                }

        return {
            "success": False,
            "error": "Groq request failed after retries."
        }

    except Exception:
        return {
            "success": False,
            "error": "Could not initialize Groq. Check the API key and server configuration."
        }
