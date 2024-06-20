from pydantic import BaseModel
from typing import Any, Optional

class RequestData(BaseModel):
    model: Any
    messages: Any
    stream: Optional[bool] = False
    max_tokens: Optional[int] = 4000
    presence_penalty: Optional[float] = 1.0
    temperature: Optional[float] = 1.0
    top_p: Optional[float] = 1.0