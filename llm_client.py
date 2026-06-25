"""
Thin wrapper around the Gemini streaming API.
"""
import os
from typing import Iterator
from google import genai

client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])
MODEL = "gemini-2.5-flash"


def stream_cover_letter(system_prompt: str, user_prompt: str) -> Iterator[str]:
    full_prompt = f"{system_prompt}\n\n{user_prompt}"
    response = client.models.generate_content_stream(
        model=MODEL,
        contents=full_prompt,
    )
    for chunk in response:
        if chunk.text:
            yield chunk.text