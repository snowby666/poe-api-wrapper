from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import StreamingResponse
from typing import Any, Generator
from poe_api_wrapper import AsyncPoeApi
from poe_api_wrapper.openai import helpers
import ujson, asyncio, random, os
from poe_api_wrapper.openai.type import RequestData

DIR = os.path.dirname(os.path.abspath(__file__))

app = FastAPI()

with open(DIR + "\\models.json", "r") as f:
    models = ujson.load(f)
    app.state.models = models

@app.get("/")
async def index():
    return {"message": "Welcome to the Poe API!"}

@app.get("/models")
@app.get("/v1/models")
async def models():
    return app.state.models

@app.post("/chat/completions")
@app.post("/v1/chat/completions")
async def chat_completions(request: Request, data: RequestData) -> dict:
    messages, model, streaming = data.messages, data.model, data.stream
    
    # Validate messages format
    if not await helpers.__validate_messages_format(messages):
        raise HTTPException(status_code=400, detail="Invalid messages format.")
    
    if model not in app.state.models:
        raise HTTPException(status_code=400, detail="Invalid model.")
    
    modelData = app.state.models[model]
    baseModel, tokensLimit, premiumModel = modelData["baseModel"], modelData["tokens"], modelData["premium_model"]
    
    token = random.choice(app.state.tokens)
    client = await AsyncPoeApi(token).create() 
    settings = await client.get_settings()
    subscription = settings["subscription"]["isActive"]
    
    if premiumModel and not subscription:
        raise HTTPException(status_code=402, detail="Premium model requires a subscription.")
    
    response = await message_handler(baseModel, messages, tokensLimit)
    completion_id = await helpers.__generate_completion_id()
    
    if streaming:
        return StreamingResponse(content=streaming_response(client, response, model, completion_id), media_type="text/event-stream", status_code=200)
    else:
        resp = await non_streaming_response(client, response, model, completion_id, messages)
        return resp
        
        
async def message_handler(baseModel: str, messages: list[dict[str, str]], tokensLimit: int) -> dict:
    try:
        main_request = messages[-1]["content"]

        rest_string = await helpers.__stringify_messages(messages=messages)
        
        rest_string = await helpers.__progressive_summarize_text(
                    rest_string, min(len(rest_string), tokensLimit) 
                )
        
        message = f"IGNORE PREVIOUS MESSAGES.\n\nYour current message context: {rest_string}\n\nThe most recent message: {main_request}\n\n"
        return {"bot": baseModel, "message": message}
    except Exception as e:
        raise HTTPException(status_code=400, detail="Failed to process messages.") from e


async def create_completion_data(chunk, completion_id, model):
    completion_timestamp = await helpers.__generate_timestamp()
    return ujson.dumps({"id": f"chatcmpl-{completion_id}", "object": "chat.completion.chunk", "created": completion_timestamp, "model": model, "choices": [{"index": 0, "delta": {"content": chunk}, "finish_reason": None}]}, separators=(",",":"), escape_forward_slashes=False)


async def streaming_response(client: AsyncPoeApi, response: dict, model: str, completion_id: str) -> Generator[str, Any, None]:
    try:
        async for chunk in client.send_message(response["bot"], response["message"]):
            content = await create_completion_data(chunk["response"], completion_id, model)
            yield f"data: {content}\n\n"
            await asyncio.sleep(0.001)
            
        end_completion_data = {
            "id": f"chatcmpl-{completion_id}",
            "object": "chat.completion.chunk",
            "created": await helpers.__generate_timestamp(),
            "model": model,
            "choices": [
                {
                    "index": 0,
                    "delta": {},
                    "finish_reason": "stop",
                }
            ],
        }
        content = ujson.dumps(end_completion_data, separators=(",", ":"))
        yield f"data: {content}\n\n"
    except GeneratorExit:
        pass

async def non_streaming_response(client: AsyncPoeApi, response: dict, model: str, completion_id: str, messages: list[dict[str, str]]) -> dict:
    async for chunk in client.send_message(response["bot"], response["message"]):
        pass
    
    prompt_tokens, completion_tokens = await helpers.__tokenize(''.join([str(message['content']) for message in messages])), await helpers.__tokenize(chunk["text"])
    
    return {
            "id": f"chatcmpl-{completion_id}",
            "object": "chat.completion",
            "created": await helpers.__generate_timestamp(),
            "model": model,
            "usage": {
                "prompt_tokens": prompt_tokens,
                "completion_tokens": completion_tokens,
                "total_tokens": prompt_tokens + completion_tokens,
            },
            "choices": [
                {
                    "message": {"role": "assistant", "content": chunk["text"]},
                    "finish_reason": "stop",
                    "index": 0,
                }
            ],
            
        }
    
if __name__ == "__main__":
    with open(DIR + "\\secrets.json", "r") as f:
        TOKENS = ujson.load(f)
        if "tokens" not in TOKENS:
            raise Exception("Tokens not found in secrets.json")
        app.state.tokens = TOKENS["tokens"]
    
    from daphne.cli import CommandLineInterface
    CommandLineInterface().run(["api:app", "--bind", "127.0.0.1", "--port", "8000"])
    
def start_server(tokens):
    app.state.tokens = tokens
    from daphne.cli import CommandLineInterface
    CommandLineInterface().run(["poe_api_wrapper.openai.api:app", "--bind", "127.0.0.1", "--port", "8000"])