from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import StreamingResponse, ORJSONResponse
from fastapi.middleware.cors import CORSMiddleware
from daphne.cli import CommandLineInterface
from typing import Any, Dict, Tuple, Union, AsyncGenerator
from poe_api_wrapper import AsyncPoeApi
from poe_api_wrapper.openai import helpers
from poe_api_wrapper.openai.type import *
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


async def call_tools(messages, tools, tool_choice):
    response = await message_handler("gpt4_o_mini", messages, 128000, tools, tool_choice)
    tool_calls = None
    client, _ = await rotate_token(app.state.tokens)
    async for chunk in client.send_message(bot="gpt4_o_mini", message=response["message"]):
        try:
            res_list = orjson.loads(chunk["text"].strip().replace("\n", "").replace("\\",""))
            if res_list and type(res_list) == list:
                tool_calls = res_list
                break
        except Exception as e:
            pass
        
    return tool_calls
    
    
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
            raise HTTPException(detail={"error": {"message": "Invalid model.", "type": "error", "param": None, "code": 400}}, status_code=400)
        return ORJSONResponse({"id": model, "object": "model", "created": await helpers.__generate_timestamp(), "owned_by": app.state.models[model]["owned_by"], "tokens": app.state.models[model]["tokens"], "endpoints": app.state.models[model]["endpoints"]})
    modelsData = [{"id": model, "object": "model", "created": await helpers.__generate_timestamp(), "owned_by": values["owned_by"], "tokens": values["tokens"], "endpoints": values["endpoints"]} for model, values in app.state.models.items()]
    return ORJSONResponse({"object": "list", "data": modelsData})


@app.api_route("/chat/completions", methods=["POST", "OPTIONS"], response_model=None)
@app.api_route("/v1/chat/completions", methods=["POST", "OPTIONS"], response_model=None)
async def chat_completions(request: Request, data: ChatData) -> Union[StreamingResponse, ORJSONResponse]:
    messages, model, streaming, max_tokens, stream_options, tools, tool_choice = data.messages, data.model, data.stream, data.max_tokens, data.stream_options, data.tools, data.tool_choice

    # Validate messages format
    if not await helpers.__validate_messages_format(messages):
        raise HTTPException(detail={"error": {"message": "Invalid messages format.", "type": "error", "param": None, "code": 400}}, status_code=400)
    
    if model not in app.state.models:
        raise HTTPException(detail={"error": {"message": "Invalid model.", "type": "error", "param": None, "code": 400}}, status_code=400)
    
    if tools and len(tools) > 20:
        raise HTTPException(detail={"error": {"message": "Maximum 20 tools are allowed.", "type": "error", "param": None, "code": 400}}, status_code=400)
    
    include_usage = stream_options.get("include_usage", False) if stream_options else False
    
    modelData = app.state.models[model]
    baseModel, tokensLimit, endpoints, premiumModel = modelData["baseModel"], modelData["tokens"], modelData["endpoints"], modelData["premium_model"]
    
    if "/v1/chat/completions" not in endpoints:
        raise HTTPException(detail={"error": {"message": "This model does not support chat completions.", "type": "error", "param": None, "code": 400}}, status_code=400)
    
    client, subscription = await rotate_token(app.state.tokens)
    
    if premiumModel and not subscription:
        raise HTTPException(detail={"error": {"message": "Premium model requires a subscription.", "type": "error", "param": None, "code": 402}}, status_code=402)
    
    text_messages, image_urls = await helpers.__split_content(messages)
    
    response = await message_handler(baseModel, text_messages, tokensLimit)
    prompt_tokens = await helpers.__tokenize(''.join([str(message) for message in response["message"]]))
    
    if prompt_tokens > tokensLimit:
        raise HTTPException(detail={"error": {"message": f"Your prompt exceeds the maximum context length of {tokensLimit} tokens.", "type": "error", "param": None, "code": 400}}, status_code=400)
        
    if max_tokens and sum((max_tokens, prompt_tokens)) > tokensLimit:
        raise HTTPException(detail={"error": {
                                        "message": f"This model's maximum context length is {tokensLimit} tokens. However your request exceeds this limit ({max_tokens} in max_tokens, {prompt_tokens} in messages).", 
                                        "type": "error", 
                                        "param": None, 
                                        "code": 400}
                                    }, status_code=400)
    
    raw_tool_calls = None
    if tools:
        if not tool_choice:
            tool_choice = "auto"
        raw_tool_calls = await call_tools(messages, tools, tool_choice)
    
    if raw_tool_calls:
        response = {"bot": "gpt4_o_mini", "message": ""}
        prompt_tokens = await helpers.__tokenize(''.join([str(message["content"]) for message in text_messages]))
        
    completion_id = await helpers.__generate_completion_id()
    
    return await streaming_response(client, response, model, completion_id, prompt_tokens, image_urls, max_tokens, include_usage, raw_tool_calls) \
        if streaming else await non_streaming_response(client, response, model, completion_id, prompt_tokens, image_urls, max_tokens, raw_tool_calls)


@app.api_route("/images/generations", methods=["POST", "OPTIONS"], response_model=None)
@app.api_route("/v1/images/generations", methods=["POST", "OPTIONS"], response_model=None)
async def create_images(request: Request, data: ImagesGenData) -> ORJSONResponse:
    prompt, model, n, size = data.prompt, data.model, data.n, data.size
    
    if not isinstance(prompt, str):
        raise HTTPException(detail={"error": {"message": "Invalid prompt.", "type": "error", "param": None, "code": 400}}, status_code=400)
    
    if model not in app.state.models:
        raise HTTPException(detail={"error": {"message": "Invalid model.", "type": "error", "param": None, "code": 400}}, status_code=400)
    
    if not isinstance(n, int) or n < 1:
        raise HTTPException(detail={"error": {"message": "Invalid n value.", "type": "error", "param": None, "code": 400}}, status_code=400)
    
    if size == "1024x1024":
        aspect_ratio = ""
    elif "sizes" in app.state.models[model] and size in app.state.models[model]["sizes"]:
        aspect_ratio = app.state.models[model]["sizes"][size]
    else:
        raise HTTPException(detail={"error": {"message": f"Invalid size for {model}. Available sizes: {', '.join(app.state.models[model]['sizes']) if 'sizes' in app.state.models[model] else '1024x1024'}", "type": "error", "param": None, "code": 400}}, status_code=400)

    modelData = app.state.models[model]
    baseModel, tokensLimit, endpoints, premiumModel = modelData["baseModel"], modelData["tokens"], modelData["endpoints"], modelData["premium_model"]
    
    if "/v1/images/generations" not in endpoints:
        raise HTTPException(detail={"error": {"message": "This model does not support image generation.", "type": "error", "param": None, "code": 400}}, status_code=400)
    
    client, subscription = await rotate_token(app.state.tokens)
    
    if premiumModel and not subscription:
        raise HTTPException(detail={"error": {"message": "Premium model requires a subscription.", "type": "error", "param": None, "code": 402}}, status_code=402)
    
    response = await image_handler(baseModel, prompt, tokensLimit)
    
    urls = []
    for _ in range(n):
        image_generation = await generate_image(client, response, aspect_ratio)
        urls.extend([url for url in image_generation.split() if url.startswith("https://")])
        if len(urls) >= n:
            break
    urls = urls[-n:]
    
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
    image, prompt, model, n, size = data.image, data.prompt, data.model, data.n, data.size
    
    if not (isinstance(image, str) and (os.path.exists(image) or image.startswith("http"))):
        raise HTTPException(detail={"error": {"message": "Invalid image.", "type": "error", "param": None, "code": 400}}, status_code=400)
    
    if not isinstance(prompt, str):
        raise HTTPException(detail={"error": {"message": "Invalid prompt.", "type": "error", "param": None, "code": 400}}, status_code=400)
    
    if model not in app.state.models:
        raise HTTPException(detail={"error": {"message": "Invalid model.", "type": "error", "param": None, "code": 400}}, status_code=400)
    
    if not isinstance(n, int) or n < 1:
        raise HTTPException(detail={"error": {"message": "Invalid n value.", "type": "error", "param": None, "code": 400}}, status_code=400)
    
    if size == "1024x1024":
        aspect_ratio = ""
    elif "sizes" in app.state.models[model] and size in app.state.models[model]["sizes"]:
        aspect_ratio = app.state.models[model]["sizes"][size]
    else:
        raise HTTPException(detail={"error": {"message": f"Invalid size for {model}. Available sizes: {', '.join(app.state.models[model]['sizes']) if 'sizes' in app.state.models[model] else '1024x1024'}", "type": "error", "param": None, "code": 400}}, status_code=400)
    
    modelData = app.state.models[model]
    baseModel, tokensLimit, endpoints, premiumModel = modelData["baseModel"], modelData["tokens"], modelData["endpoints"], modelData["premium_model"]
    
    if "/v1/images/edits" not in endpoints:
        raise HTTPException(detail={"error": {"message": "This model does not support image editing.", "type": "error", "param": None, "code": 400}}, status_code=400)
    
    client, subscription = await rotate_token(app.state.tokens)
    
    if premiumModel and not subscription:
        raise HTTPException(detail={"error": {"message": "Premium model requires a subscription.", "type": "error", "param": None, "code": 402}}, status_code=402)
    
    response = await image_handler(baseModel, prompt, tokensLimit)
    
    urls = []
    for _ in range(n):
        image_generation = await generate_image(client, response, aspect_ratio, [image])
        urls.extend([url for url in image_generation.split() if url.startswith("https://")])
        if len(urls) >= n:
            break
    urls = urls[-n:]
        
    if len(urls) == 0:
        raise HTTPException(detail={"error": {"message": f"The provider for {model} sent an invalid response.", "type": "error", "param": None, "code": 500}}, status_code=500)
    
    async with AsyncClient(http2=True) as fetcher:
        for url in urls:
            r = await fetcher.get(url)
            content_type = r.headers.get("Content-Type", "")
            if not content_type.startswith("image/"):
                raise HTTPException(detail={"error": {"message": "The content returned was not an image.", "type": "error", "param": None, "code": 500}}, status_code=500)
            
    return ORJSONResponse({"created": await helpers.__generate_timestamp(), "data": [{"url": url} for url in urls]})
   

async def image_handler(baseModel: str, prompt: str, tokensLimit: int) -> dict:
    try:
        message = await helpers.__progressive_summarize_text(prompt, min(len(prompt), tokensLimit))
        return {"bot": baseModel, "message": message}
    except Exception as e:
        raise HTTPException(detail={"error": {"message": f"Failed to truncate prompt. Error: {e}", "type": "error", "param": None, "code": 400}}, status_code=400) from e
   
   
async def message_handler(
    baseModel: str, messages: List[Dict[str, str]], tokensLimit: int, tools: list[dict[str, str]] = None, tool_choice = None
) -> dict:
    
    try:
        main_request = messages[-1]["content"]
        check_user = messages[::-1]
        for message in check_user:
            if message["role"] == "user":
                main_request = message["content"]
                break
        
        if tools:
            rest_tools = await helpers.__convert_functions_format(tools, tool_choice)
            if messages[0]["role"] == "system":
                messages[0]["content"] += rest_tools
            else:
                messages.insert(0, {"role": "system", "content": rest_tools})

        full_string = await helpers.__stringify_messages(messages=messages)
        
        history_string = await helpers.__stringify_messages(messages=messages[:-1])

        full_tokens = await helpers.__tokenize(full_string)
        
        if full_tokens > tokensLimit:
            history_string = await helpers.__progressive_summarize_text(
                history_string, tokensLimit - await helpers.__tokenize(main_request) - 100
            )
        
        message = f"Your current message context: \n{history_string}\n\nReply to most recent message: {main_request}\n\n"
        return {"bot": baseModel, "message": message}
    except Exception as e:
        raise HTTPException(detail={"error": {"message": f"Failed to process messages. Error: {e}", "type": "error", "param": None, "code": 400}}, status_code=400) from e


async def generate_image(client: AsyncPoeApi, response: dict, aspect_ratio: str, image: list = []) -> str:
    try:
        async for chunk in client.send_message(bot=response["bot"], message=f"{response['message']} {aspect_ratio}", file_path=image):
            pass
        return chunk["text"]
    except Exception as e:
        raise HTTPException(detail={"error": {"message": f"Failed to generate image. Error: {e}", "type": "error", "param": None, "code": 500}}, status_code=500) from e
    
    
async def create_completion_data(
    completion_id: str, created: int, model: str, chunk: str = None, 
    finish_reason: str = None, include_usage: bool=False,
    prompt_tokens: int = 0, completion_tokens: int = 0, raw_tool_calls: list[dict[str, str]] = None 
) -> Dict[str, Union[str, list, float]]:
    
    completion_data = ChatCompletionChunk(
        id=f"chatcmpl-{completion_id}",
        object="chat.completion.chunk",
        created=created,
        model=model,
        choices=[
            ChatCompletionChunkChoice(
                index=0,
                delta=MessageResponse(
                    role="assistant", 
                    content=chunk,
                    tool_calls=[ChoiceDeltaToolCall(
                            index = raw_tool_calls.index(tool_call),
                            id=f"call-{await helpers.__generate_completion_id()}",
                            function=ChoiceDeltaToolCallFunction(name=tool_call["name"], arguments=orjson.dumps(tool_call["arguments"]))) for tool_call in raw_tool_calls] if raw_tool_calls else None
                    ),
                finish_reason=finish_reason,
            )
        ],
    )
    
    if include_usage:
        completion_data.usage = None
        if finish_reason in ("stop", "length"):
            completion_data.usage = ChatCompletionUsage(
                prompt_tokens=prompt_tokens,
                completion_tokens=completion_tokens,
                total_tokens=prompt_tokens + completion_tokens)
    
    return completion_data.model_dump()
    
    
async def generate_chunks(
    client: AsyncPoeApi, response: dict, model: str, completion_id: str, 
    prompt_tokens: int, image_urls: List[str], max_tokens: int, include_usage:bool, raw_tool_calls: list[dict[str, str]] = None
) -> AsyncGenerator[bytes, None]:
    
    try:
        completion_timestamp = await helpers.__generate_timestamp()
        finish_reason = "stop"
        
        if not raw_tool_calls:
            async for chunk in client.send_message(bot=response["bot"], message=response["message"], file_path=image_urls):
                chunk_token = await helpers.__tokenize(chunk["text"])
                
                if max_tokens and chunk_token >= max_tokens:
                    await client.cancel_message(chunk)
                    finish_reason = "length"
                    break
                
                content = await create_completion_data(
                                                    completion_id=completion_id, 
                                                    created=completion_timestamp,
                                                    model=model, 
                                                    chunk=chunk["response"], 
                                                    include_usage=include_usage
                                                    )
                
                yield b"data: " + orjson.dumps(content) + b"\n\n"
                await asyncio.sleep(0.001)
                
            end_completion_data = await create_completion_data(
                                                            completion_id=completion_id, 
                                                            created=completion_timestamp,
                                                            model=model, 
                                                            finish_reason=finish_reason, 
                                                            include_usage=include_usage, 
                                                            prompt_tokens=prompt_tokens, 
                                                            completion_tokens=chunk_token
                                                            )
            
            yield b"data: " +  orjson.dumps(end_completion_data) + b"\n\n"
            
        else:
            chunk_token = await helpers.__tokenize(''.join([str(tool_call["name"]) + str(tool_call["arguments"]) for tool_call in raw_tool_calls]))
            content = await create_completion_data(
                                                completion_id=completion_id, 
                                                created=completion_timestamp,
                                                model=model, 
                                                chunk=None,
                                                finish_reason="tool_calls",
                                                include_usage=include_usage,
                                                prompt_tokens=prompt_tokens,
                                                completion_tokens=chunk_token,
                                                raw_tool_calls=raw_tool_calls)
            yield b"data: " + orjson.dumps(content) + b"\n\n"
            await asyncio.sleep(0.01)
   
        yield b"data: [DONE]\n\n"
    except GeneratorExit:
        pass
    except Exception as e:
        raise HTTPException(detail={"error": {"message": f"Failed to stream response. Error: {e}", "type": "error", "param": None, "code": 500}}, status_code=500) from e

    
async def streaming_response(
    client: AsyncPoeApi, response: dict, model: str, completion_id: str, 
    prompt_tokens: int, image_urls: List[str], max_tokens: int, include_usage: bool, raw_tool_calls: list[dict[str, str]] = None
) -> StreamingResponse:
    
    return StreamingResponse(content=generate_chunks(client, response, model, completion_id, prompt_tokens, image_urls, max_tokens, include_usage, raw_tool_calls), status_code=200, 
                             headers={"X-Request-ID": str(uuid.uuid4()), "Content-Type": "text/event-stream"})


async def non_streaming_response(
    client: AsyncPoeApi, response: dict, model: str, completion_id: str,
    prompt_tokens: int, image_urls: List[str], max_tokens: int, raw_tool_calls: list[dict[str, str]] = None
) -> ORJSONResponse:
    
    if not raw_tool_calls:
        try:
            finish_reason = "stop"
            async for chunk in client.send_message(bot=response["bot"], message=response["message"], file_path=image_urls):
                if max_tokens and await helpers.__tokenize(chunk["text"]) >= max_tokens:
                    await client.cancel_message(chunk)
                    finish_reason = "length"
                    break
                pass
        except Exception as e:
            raise HTTPException(detail={"error": {"message": f"Failed to generate completion. Error: {e}", "type": "error", "param": None, "code": 500}}, status_code=500) from e
        
        completion_tokens = await helpers.__tokenize(chunk["text"])
        
    else:
        completion_tokens = await helpers.__tokenize(''.join([str(tool_call["name"]) + str(tool_call["arguments"]) for tool_call in raw_tool_calls]))
        chunk = {"text": ""}
        finish_reason = "tool_calls"
        
    content = ChatCompletionResponse(
        id=f"chatcmpl-{completion_id}",
        object="chat.completion",
        created=await helpers.__generate_timestamp(),
        model=model,
        usage=ChatCompletionUsage(
            prompt_tokens=prompt_tokens,
            completion_tokens=completion_tokens,
            total_tokens=prompt_tokens + completion_tokens,
        ),
        choices=[
            ChatCompletionResponseChoice(
                index=0,
                message=MessageResponse(role="assistant", content=None if raw_tool_calls else chunk["text"],
                                        tool_calls=[ChatCompletionMessageToolCall(
                                            id=f"call-{await helpers.__generate_completion_id()}",
                                            function=FunctionCall(name=tool_call["name"], arguments=orjson.dumps(tool_call["arguments"]))) for tool_call in raw_tool_calls] if raw_tool_calls else None),
                finish_reason=finish_reason,
            )
        ],  
    )
    
    return ORJSONResponse(content.model_dump())


async def rotate_token(tokens) -> Tuple[AsyncPoeApi, bool]:
    if len(tokens) == 0:
        raise HTTPException(detail={"error": {"message": "All tokens have been used. Please add more tokens.", "type": "error", "param": None, "code": 402}}, status_code=402)
    token = random.choice(tokens)
    client = await AsyncPoeApi(token).create()
    settings = await client.get_settings()
    if settings["messagePointInfo"]["messagePointBalance"] <= 20:
        tokens.remove(token)
        return await rotate_token(tokens)
    subscriptions = settings["subscription"]["isActive"]
    return client, subscriptions


if __name__ == "__main__":
    CommandLineInterface().run(["api:app", "--bind", "127.0.0.1", "--port", "8000"])
    
    
def start_server(tokens: list, address: str="127.0.0.1", port: str="8000"):
    if not isinstance(tokens, list):
        raise TypeError("Tokens must be a list.")
    if not all(isinstance(token, dict) for token in tokens):
        raise TypeError("Tokens must be a list of dictionaries.")
    app.state.tokens = tokens
    CommandLineInterface().run(["poe_api_wrapper.openai.api:app", "--bind", f"{address}", "--port", f"{port}"])