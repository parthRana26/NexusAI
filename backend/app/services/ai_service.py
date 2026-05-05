from groq import Groq
from app.core.config import settings
from app.core.logging import logger

def get_client(api_key: str = None):
    """Returns a Groq client with the provided key or system default."""
    key = api_key if api_key else settings.GROQ_API_KEY
    return Groq(api_key=key)

def ask_ai(messages: list, api_key: str = None):
    try:
        client = get_client(api_key)
        # Handle both string messages (backward compatibility) and list of messages
        if isinstance(messages, str):
            messages = [{"role": "user", "content": messages}]
            
        response = client.chat.completions.create(
            model=settings.AI_MODEL,
            messages=messages,
            temperature=0.7
        )
        return response.choices[0].message.content
    except Exception as e:
        logger.error(f"AI Service Error: {e}")
        raise e

def stream_ai(messages: list, api_key: str = None):
    try:
        client = get_client(api_key)
        if isinstance(messages, str):
            messages = [{"role": "user", "content": messages}]
            
        stream = client.chat.completions.create(
            model=settings.AI_MODEL,
            messages=messages,
            temperature=0.7,
            stream=True
        )

        for chunk in stream:
            content = chunk.choices[0].delta.content
            if content:
                yield content
    except Exception as e:
        logger.error(f"AI Stream Error: {e}")
        yield f"Error: {str(e)}"