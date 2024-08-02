from typing import Dict
from loguru import logger

try:
    from .openai.api import start_server
    LLM_PACKAGE = True
except ImportError:
    LLM_PACKAGE = False

class PoeServer:
    def __init__(self, tokens: Dict[str, str], address: str="127.0.0.1", port: str="8000"):
        try:
            start_server(tokens, address, port)
        except Exception as e:
            logger.error(f"Failed to start server: {e}")
            raise e
