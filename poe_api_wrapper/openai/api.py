from fastapi import FastAPI, Request, HTTPException, Response
from fastapi.responses import StreamingResponse
from daphne.cli import CommandLineInterface
from typing import Any, Generator
from poe_api_wrapper import AsyncPoeApi
from poe_api_wrapper.openai import helpers
from poe_api_wrapper.openai.type import ChatData, ImagesData
import ujson, asyncio, random, os
from httpx import AsyncClient

DIR = os.path.dirname(os.path.abspath(__file__))

app = FastAPI()

with open(os.path.join(DIR, "models.json"), "r") as f:
    models = ujson.load(f)
    app.state.models = models

@app.get("/")
async def index():
    return Response(content=ujson.dumps({"message": "Welcome to the Poe API!", 
                                         "docs": "See project docs @ https://github.com/snowby666/poe-api-wrapper"}, 
                                        indent=4), media_type="application/json")

@app.get("/models")
@app.get("/v1/models")
async def models():
    return Response(content=ujson.dumps(app.state.models, indent=4), media_type="application/json")

@app.post("/chat/completions")
@app.post("/v1/chat/completions")
async def chat_completions(request: Request, data: ChatData) -> dict:
    messages, model, streaming = data.messages, data.model, data.stream
    
    # Validate messages format
    if not await helpers.__validate_messages_format(messages):
        raise HTTPException(status_code=400, detail="Invalid messages format.")
    
    if model not in app.state.models:
        raise HTTPException(status_code=400, detail="Invalid model.")
    
    modelData = app.state.models[model]
    baseModel, tokensLimit, endpoints, premiumModel = modelData["baseModel"], modelData["tokens"], modelData["endpoints"], modelData["premium_model"]
    
    if endpoints != "/v1/chat/completions":
        raise HTTPException(status_code=400, detail="This model does not support chat completions.")
    
    token = random.choice(app.state.tokens)
    client = await AsyncPoeApi(token).create() 
    settings = await client.get_settings()
    subscription = settings["subscription"]["isActive"]
    
    if premiumModel and not subscription:
        raise HTTPException(status_code=402, detail="Premium model requires a subscription.")
    
    text_messages, image_urls = await helpers.__split_content(messages)
    
    response = await message_handler(baseModel, text_messages, tokensLimit)
    completion_id = await helpers.__generate_completion_id()
    
    if streaming:
        return StreamingResponse(content=streaming_response(client, response, model, completion_id, image_urls), media_type="text/event-stream", status_code=200)
    else:
        resp = await non_streaming_response(client, response, model, completion_id, messages, image_urls)
        return resp


@app.post("/images/generations")
@app.post("/v1/images/generations")
async def images(request: Request, data: ImagesData) -> None:
    prompt, model, n = data.prompt, data.model, data.n
    
    if not isinstance(prompt, str):
        raise HTTPException(status_code=400, detail="Invalid prompt.")
    
    if model not in app.state.models:
        raise HTTPException(status_code=400, detail="Invalid model.")

    modelData = app.state.models[model]
    baseModel, tokensLimit, endpoints, premiumModel = modelData["baseModel"], modelData["tokens"], modelData["endpoints"], modelData["premium_model"]
    
    if endpoints != "/v1/images/generations":
        raise HTTPException(status_code=400, detail="This model does not support image generation.")
    
    token = random.choice(app.state.tokens)
    client = await AsyncPoeApi(token).create()
    settings = await client.get_settings()
    subscription = settings["subscription"]["isActive"]
    
    if premiumModel and not subscription:
        raise HTTPException(status_code=402, detail="Premium model requires a subscription.")
    
    response = await image_handler(prompt, model, tokensLimit)
    
    urls = []
    for _ in range(n):
        image_generation = await generate_image(client, response, baseModel)
        urls.extend([url for url in image_generation.split() if url.startswith("https://")])
    
    if len(urls) == 0:
        raise HTTPException(detail={"error": {"message": "The provider for {model} sent an invalid response.", "type": "error", "param": None, "code": 500}}, status_code=500)
        
    async with AsyncClient() as fetcher:
        for url in urls:
            r = await fetcher.get(url)
            content_type = r.headers.get("Content-Type", "")
            if not content_type.startswith("image/"):
                raise HTTPException(detail={"error": {"message": "The content returned was not an image.", "type": "error", "param": None, "code": 500}}, status_code=500)

    return {"created": await helpers.__generate_timestamp(), "data": [{"url": url} for url in urls]}


async def image_handler(prompt: str, model: str, tokensLimit: int) -> dict:
    try:
        message = await helpers.__progressive_summarize_text(prompt, min(len(prompt), tokensLimit))
        return {"bot": model, "message": message}
    except Exception as e:
        raise HTTPException(status_code=400, detail="Failed to truncate prompt.") from e
         
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

async def generate_image(client: AsyncPoeApi, response: dict, model: str) -> str:
    try:
        async for chunk in client.send_message(bot=response["bot"], message=response["message"]):
            pass
        return chunk["text"]
    except Exception as e:
        raise HTTPException(status_code=500, detail="Failed to generate image.") from e
    
async def create_completion_data(chunk, completion_id, model):
    completion_timestamp = await helpers.__generate_timestamp()
    return ujson.dumps({"id": f"chatcmpl-{completion_id}", "object": "chat.completion.chunk", "created": completion_timestamp, "model": model, "choices": [{"index": 0, "delta": {"content": chunk}, "finish_reason": None}]}, separators=(",",":"), escape_forward_slashes=False)


async def streaming_response(client: AsyncPoeApi, response: dict, model: str, completion_id: str, image_urls: list[str]) -> Generator[str, Any, None]:
    try:
        async for chunk in client.send_message(bot=response["bot"], message=response["message"], file_path=image_urls):
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

async def non_streaming_response(client: AsyncPoeApi, response: dict, model: str, completion_id: str, messages: list[dict[str, str]], image_urls: list[str]) -> dict:
    async for chunk in client.send_message(bot=response["bot"], message=response["message"], file_path=image_urls):
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
    with open(os.path.join(DIR, "secrets.json"), "r") as f:
        TOKENS = ujson.load(f)
        if "tokens" not in TOKENS:
            raise Exception("Tokens not found in secrets.json")
        app.state.tokens = TOKENS["tokens"]
    
    CommandLineInterface().run(["api:app", "--bind", "127.0.0.1", "--port", "8000"])
    
def start_server(tokens):
    app.state.tokens = tokens
    
    CommandLineInterface().run(["poe_api_wrapper.openai.api:app", "--bind", "127.0.0.1", "--port", "8000"])