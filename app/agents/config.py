try:
    from langchain_community.llms import Ollama
except ImportError:
    from langchain.llms import Ollama  # Fallback for older installs
from app.config import settings


def get_llm(fast: bool = False):
    model = settings.OLLAMA_FAST_MODEL if fast else settings.OLLAMA_MODEL_NAME
    return Ollama(
        base_url=settings.OLLAMA_API_URL,
        model=model,
        temperature=settings.OLLAMA_TEMPERATURE,
    )
