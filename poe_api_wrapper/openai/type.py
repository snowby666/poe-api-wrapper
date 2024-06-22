from pydantic import BaseModel
from typing import Any, Optional

class ChatData(BaseModel):
    model: Any
    messages: Any
    stream: Optional[bool] = False
    max_tokens: Optional[int] = 4000
    presence_penalty: Optional[float] = 1.0
    temperature: Optional[float] = 1.0
    top_p: Optional[float] = 1.0
    
class ImagesGenData(BaseModel):
    prompt: Any
    model: Any
    n: Optional[int] = 1
    size: Optional[str] = '1024x1024'
    
class ImagesEditData(BaseModel):
    image: Any
    prompt: Any
    model: Any
    n: Optional[int] = 1
    size: Optional[str] = '1024x1024'
