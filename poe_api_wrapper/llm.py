from loguru import logger

try:
    from .openai.api import start_server
    LLM_PACKAGE = True
except ImportError:
    LLM_PACKAGE = False

class PoeServer:
    def __init__(self, tokens: dict[str, str]):
        try:
            start_server(tokens)
        except Exception as e:
            logger.error(f"Failed to start server: {e}")
            raise e
