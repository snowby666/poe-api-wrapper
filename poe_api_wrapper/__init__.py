import os, socket

def is_using_proxy(address, port):
    try:
        socket.create_connection((address, port), timeout=5)
        return True
    except Exception as e:
        return False

if is_using_proxy("127.0.0.1", "7890"):
    print("""
        3rd party proxy client detected. 
        Updating environment variables ...
        """)

    os.environ["http_proxy"] = "http://127.0.0.1:7890"
    os.environ["https_proxy"] = "http://127.0.0.1:7890"

from .api import PoeApi
from .async_api import AsyncPoeApi
from .example import PoeExample

from .llm import LLM_PACKAGE
if LLM_PACKAGE:
    from .llm import PoeServer