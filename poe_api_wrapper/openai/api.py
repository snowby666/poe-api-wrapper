from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import StreamingResponse, ORJSONResponse
from fastapi.middleware.cors import CORSMiddleware
from daphne.cli import CommandLineInterface
from typing import Any, Union, AsyncGenerator
from poe_api_wrapper import AsyncPoeApi
from poe_api_wrapper.openai import helpers
from poe_api_wrapper.openai.type import ChatData, ImagesGenData, ImagesEditData
import orjson, asyncio, random, os, uuid
from httpx import AsyncClient

DIR = os.path.dirname(os.path.abspath(__file__))

app = FastAPI(title="Poe API Wrapper", description="OpenAI Proxy Server")

app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_credentials=True, allow_methods=["*"], allow_headers=["*"])

with open(os.path.join(DIR, "secrets.json"), "rb") as f:
    TOKENS = orjson.loads(f.read())
    if "tokens" not in TOKENS:
        raise Exception("Tokens not found in secrets.json")
    app.state.tokens = TOKENS["tokens"]

with open(os.path.join(DIR, "models.json"), "rb") as f:
    models = orjson.loads(f.read())
    app.state.models = models

@app.get("/", response_model=None)
async def index() -> ORJSONResponse:
    return ORJSONResponse({"message": "Welcome to Poe Api Wrapper reverse proxy!",
                            "docs": "See project docs @ https://github.com/snowby666/poe-api-wrapper"})


@app.api_route("/models/{model}", methods=["GET", "POST", "PUT", "PATCH", "HEAD"], response_model=None)
@app.api_route("/models/{model}", methods=["GET", "POST", "PUT", "PATCH", "HEAD"], response_model=None)
@app.api_route("/models", methods=["GET", "POST", "PUT", "PATCH", "HEAD"], response_model=None)
@app.api_route("/v1/models", methods=["GET", "POST", "PUT", "PATCH", "HEAD"], response_model=None)
async def list_models(request: Request, model: str = None) -> ORJSONResponse:
    if model:
        if model not in app.state.models:
            raise HTTPException(status_code=400, detail="Invalid model.")
        return ORJSONResponse(app.state.models[model])
    modelsData = [{"id": model, "object": "model", "created": None, "owned_by": values["owned_by"], "tokens": values["tokens"], "endpoints": values["endpoints"]} for model, values in app.state.models.items()]
    return ORJSONResponse({"object": "list", "data": modelsData})


@app.api_route("/chat/completions", methods=["POST", "OPTIONS"], response_model=None)
@app.api_route("/v1/chat/completions", methods=["POST", "OPTIONS"], response_model=None)
async def chat_completions(request: Request, data: ChatData) -> Union[StreamingResponse, ORJSONResponse]:
    messages, model, streaming = data.messages, data.model, data.stream
    
    # Validate messages format
    if not await helpers.__validate_messages_format(messages):
        raise HTTPException(status_code=400, detail="Invalid messages format.")
    
    if model not in app.state.models:
        raise HTTPException(status_code=400, detail="Invalid model.")
    
    modelData = app.state.models[model]
    baseModel, tokensLimit, endpoints, premiumModel = modelData["baseModel"], modelData["tokens"], modelData["endpoints"], modelData["premium_model"]
    
    if "/v1/chat/completions" not in endpoints:
        raise HTTPException(status_code=400, detail="This model does not support chat completions.")
    
    client, subscription = await rotate_token(app.state.tokens)
    
    if premiumModel and not subscription:
        raise HTTPException(status_code=402, detail="Premium model requires a subscription.")
    
    text_messages, image_urls = await helpers.__split_content(messages)
    
    response = await message_handler(baseModel, text_messages, tokensLimit)
    completion_id = await helpers.__generate_completion_id()
    
    return await streaming_response(client, response, model, completion_id, image_urls) if streaming else await non_streaming_response(client, response, model, completion_id, messages, image_urls)

@app.api_route("/images/generations", methods=["POST", "OPTIONS"], response_model=None)
@app.api_route("/v1/images/generations", methods=["POST", "OPTIONS"], response_model=None)
async def create_images(request: Request, data: ImagesGenData) -> ORJSONResponse:
    prompt, model, n = data.prompt, data.model, data.n
    
    if not isinstance(prompt, str):
        raise HTTPException(status_code=400, detail="Invalid prompt.")
    
    if model not in app.state.models:
        raise HTTPException(status_code=400, detail="Invalid model.")

    modelData = app.state.models[model]
    baseModel, tokensLimit, endpoints, premiumModel = modelData["baseModel"], modelData["tokens"], modelData["endpoints"], modelData["premium_model"]
    
    if "/v1/images/generations" not in endpoints:
        raise HTTPException(status_code=400, detail="This model does not support image generation.")
    
    client, subscription = await rotate_token(app.state.tokens)
    
    if premiumModel and not subscription:
        raise HTTPException(status_code=402, detail="Premium model requires a subscription.")
    
    response = await image_handler(baseModel, prompt, tokensLimit)
    
    urls = []
    for _ in range(n):
        image_generation = await generate_image(client, response)
        urls.extend([url for url in image_generation.split() if url.startswith("https://")])
    
    if len(urls) == 0:
        raise HTTPException(detail={"error": {"message": f"The provider for {model} sent an invalid response.", "type": "error", "param": None, "code": 500}}, status_code=500)
        
    async with AsyncClient(http2=True) as fetcher:
        for url in urls:
            r = await fetcher.get(url)
            content_type = r.headers.get("Content-Type", "")
            if not content_type.startswith("image/"):
                raise HTTPException(detail={"error": {"message": "The content returned was not an image.", "type": "error", "param": None, "code": 500}}, status_code=500)

    return ORJSONResponse({"created": await helpers.__generate_timestamp(), "data": [{"url": url} for url in urls]})



@app.api_route("/images/edits", methods=["POST", "OPTIONS"], response_model=None)
@app.api_route("/v1/images/edits", methods=["POST", "OPTIONS"], response_model=None)
async def edit_images(request: Request, data: ImagesEditData) -> ORJSONResponse:
    image, prompt, model = data.image, data.prompt, data.model
    
    if isinstance(image, str) and not os.path.exists(image) and not image.startswith("http"):
        raise HTTPException(status_code=400, detail="Invalid image.")
    
    if not isinstance(prompt, str):
        raise HTTPException(status_code=400, detail="Invalid prompt.")
    
    if model not in app.state.models:
        raise HTTPException(status_code=400, detail="Invalid model.")
    
    modelData = app.state.models[model]
    baseModel, tokensLimit, endpoints, premiumModel = modelData["baseModel"], modelData["tokens"], modelData["endpoints"], modelData["premium_model"]
    
    if "/v1/images/edits" not in endpoints:
        raise HTTPException(status_code=400, detail="This model does not support image editing.")
    
    client, subscription = await rotate_token(app.state.tokens)
    
    if premiumModel and not subscription:
        raise HTTPException(status_code=402, detail="Premium model requires a subscription.")
    
    response = await image_handler(baseModel, prompt, tokensLimit)
    
    urls = []
    for _ in range(1):
        image_generation = await generate_image(client, response, [image])
        urls.extend([url for url in image_generation.split() if url.startswith("https://")])
        
    if len(urls) == 0:
        raise HTTPException(detail={"error": {"message": f"The provider for {model} sent an invalid response.", "type": "error", "param": None, "code": 500}}, status_code=500)
    
    async with AsyncClient(http2=True) as fetcher:
        for url in urls:
            r = await fetcher.get(url)
            content_type = r.headers.get("Content-Type", "")
            if not content_type.startswith("image/"):
                raise HTTPException(detail={"error": {"message": "The content returned was not an image.", "type": "error", "param": None, "code": 500}}, status_code=500)
            
    return ORJSONResponse({"created": await helpers.__generate_timestamp(), "data": [{"url": url} for url in urls]})
   
   
async def rotate_token(tokens):
    token = random.choice(tokens)
    client = await AsyncPoeApi(token).create()
    settings = await client.get_settings()
    if settings["messagePointInfo"]["messagePointBalance"] <= 20:
        tokens.remove(token)
        if len(tokens) == 0:
            raise HTTPException(status_code=402, detail="No tokens available.")
        return await rotate_token(tokens)
    subscriptions = settings["subscription"]["isActive"]
    return client, subscriptions

async def image_handler(baseModel: str, prompt: str, tokensLimit: int) -> dict:
    try:
        message = await helpers.__progressive_summarize_text(prompt, min(len(prompt), tokensLimit))
        return {"bot": baseModel, "message": message}
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to truncate prompt. Error: {e}") from e
   
   
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
        raise HTTPException(status_code=400, detail=f"Failed to process messages. Error: {e}") from e


async def generate_image(client: AsyncPoeApi, response: dict, image: list = []) -> str:
    try:
        async for chunk in client.send_message(bot=response["bot"], message=response["message"], file_path=image):
            pass
        return chunk["text"]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate image. Error: {e}") from e
    
    
async def create_completion_data(chunk: str, completion_id: str, model: str) -> dict[str, Union[str, list, float]]:
    completion_timestamp = await helpers.__generate_timestamp()
    return {
        "id": f"chatcmpl-{completion_id}", 
        "object": "chat.completion.chunk", 
        "created": completion_timestamp, 
        "model": model, 
        "choices": [{
            "index": 0, 
            "delta": {"content": chunk}, 
            "finish_reason": None
        }]
    }


async def generate_chunks(client: AsyncPoeApi, response: dict, model: str, completion_id: str, image_urls: list[str]) -> AsyncGenerator[bytes, None]:
    try:
        async for chunk in client.send_message(bot=response["bot"], message=response["message"], file_path=image_urls):
            content = await create_completion_data(chunk["response"], completion_id, model)
            yield b"data: " + orjson.dumps(content) + b"\n\n"
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
        
        yield b"data: " +  orjson.dumps(end_completion_data) + b"\n\n"
        yield b"data: [DONE]"
    except GeneratorExit:
        pass
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to stream response. Error: {e}") from e
    
async def streaming_response(client: AsyncPoeApi, response: dict, model: str, completion_id: str, image_urls: list[str]) -> StreamingResponse:
    return StreamingResponse(content=generate_chunks(client, response, model, completion_id, image_urls), status_code=200, headers={"X-Request-ID": str(uuid.uuid4()), "Content-Type": "text/event-stream"})


async def non_streaming_response(client: AsyncPoeApi, response: dict, model: str, completion_id: str, messages: list[dict[str, str]], image_urls: list[str]) -> ORJSONResponse:
    try:
        async for chunk in client.send_message(bot=response["bot"], message=response["message"], file_path=image_urls):
            pass
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate completion. Error: {e}") from e
    
    prompt_tokens, completion_tokens = await helpers.__tokenize(''.join([str(message['content']) for message in messages])), await helpers.__tokenize(chunk["text"])
    
    return ORJSONResponse({
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
            
        })


if __name__ == "__main__":
    CommandLineInterface().run(["api:app", "--bind", "127.0.0.1", "--port", "8000"])
    
def start_server(tokens):
    app.state.tokens = tokens
    CommandLineInterface().run(["poe_api_wrapper.openai.api:app", "--bind", "127.0.0.1", "--port", "8000"])