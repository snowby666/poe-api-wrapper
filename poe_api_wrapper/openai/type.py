from pydantic import BaseModel, Extra
from typing import Any, Optional, List, Literal, Dict, Union

class ChatData(BaseModel):
    model: Any
    messages: Any
    stream: Optional[bool] = False
    max_tokens: Optional[int] = None
    frequency_penalty: Optional[float] = 0.0
    presence_penalty: Optional[float] = 1.0
    temperature: Optional[float] = 1.0
    top_p: Optional[float] = 1.0
    stream_options: Optional[dict[str, Any]] = None
    tools: Optional[List[dict]] = None
    tool_choice: Optional[Union[str, dict]] = None
    
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


# OpenAI typing
class FunctionCall(BaseModel):
    name: Optional[str] = None
    arguments: Optional[str] = None
    
class ChoiceDeltaToolCallFunction(BaseModel):
    name: Optional[str] = None
    arguments: Optional[str] = None

class ChatCompletionMessageToolCall(BaseModel, extra=Extra.allow):
    id: Optional[str] = None
    function: FunctionCall
    type: Optional[Literal["function"]] = 'function'
    
class ChoiceDeltaToolCall(BaseModel):
    index: Optional[int] = 0
    id: Optional[str] = None
    function: ChoiceDeltaToolCallFunction
    type: Optional[Literal["function"]] = 'function'

class MessageResponse(BaseModel):
    role: Optional[Literal["user", "system", "assistant", "tool"]] = None
    content: Optional[str] = None
    function_call: Optional[ChoiceDeltaToolCallFunction] = None
    tool_calls: Optional[List[Union[ChatCompletionMessageToolCall, ChoiceDeltaToolCall]]] = None

class ChatCompletionUsage(BaseModel):
    prompt_tokens: int
    completion_tokens: int
    total_tokens: int
    
# Non-Streaming
class ChatCompletionResponseChoice(BaseModel):
    index: int
    message: MessageResponse
    finish_reason: Optional[Literal["stop", "length", "content_filter", "tool_calls", "function_call"]] = None
    
class ChatCompletionResponse(BaseModel):
    id: str
    choices: List[ChatCompletionResponseChoice]
    created: int  # Unix timestamp (in seconds)
    model: str
    system_fingerprint: Optional[str] = None
    object: Literal["chat.completion"] = "chat.completion"
    usage: ChatCompletionUsage

# Streaming
class ChatCompletionChunkChoice(BaseModel):
    index: int
    delta: MessageResponse
    finish_reason: Optional[Literal["stop", "length", "content_filter", "tool_calls", "function_call"]] = None
    
class ChatCompletionChunk(BaseModel, extra=Extra.allow):
    id: str
    choices: List[ChatCompletionChunkChoice]
    object: Literal["chat.completion.chunk"] = "chat.completion.chunk"
    created: int 
    model: str