<div align="center">
<a href="https://github.com/snowby666">
<img src="https://socialify.git.ci/snowby666/poe-api-wrapper/image?font=Raleway&forks=1&issues=1&language=1&logo=https://i.ibb.co/xHrZxFY/logo-nobg.png&name=1&owner=1&pattern=Charlie%20Brown&pulls=1&stargazers=1&theme=Auto" width="700" height="350"></a>

<h1>Poe API Wrapper <img src="https://psc2.cf2.poecdn.net/favicon.svg" height="35"></h1>

<p><em>A simple, lightweight and efficient API wrapper for Poe.com</em></p>
</div>

<p align="center">
<a href="https://pypi.org/project/poe-api-wrapper/"><img src="https://img.shields.io/pypi/v/poe-api-wrapper"></a>
<img alt="Python Version" src="https://img.shields.io/badge/python-3.7+-blue.svg" alt="python">
<a href="https://www.pepy.tech/projects/poe-api-wrapper">
<img alt="PyPI - Downloads" src="https://static.pepy.tech/badge/poe-api-wrapper"></a>
<a href="https://discord.gg/apUUqbxCBQ">
<img alt="Support Server" src="https://dcbadge.limes.pink/api/server/https://discord.com/invite/apUUqbxCBQ?style=flat"></a>
<br>
</p>

## 📚 Table of Contents
- [📚 Table of Contents](#-table-of-contents)
- [✨ Highlights](#-highlights)
- [🔧 Installation](#-installation)
- [🦄 Documentation](#-documentation)
  - [Available Default Bots](#available-default-bots)
  - [How to get your Token](#how-to-get-your-token)
    - [Getting p-b and p-lat cookies (*required*)](#getting-p-b-and-p-lat-cookies-required)
    - [Getting formkey (*optional*)](#getting-formkey-optional)
  - [OpenAI](#openai)
    - [Available Routes](#available-routes)
    - [Quick Setup](#quick-setup)
    - [Built-in completion (WIP)](#built-in-completion-wip)
    - [OpenAI Proxy Server](#openai-proxy-server)
      - [Chat](#chat)
      - [Images](#images)
      - [Models](#models)
  - [Basic Usage](#basic-usage)
  - [Bots Group Chat](#bots-group-chat)
  - [Misc](#misc)
    - [Text files](#text-files)
    - [Media files](#media-files)
- [🙌 Contributing](#-contributing)
  - [Run debug](#run-debug)
  - [Ways to contribute](#ways-to-contribute)
  - [Contributors](#contributors)
- [🤝 Copyright](#-copyright)
  - [Copyright Notice](#copyright-notice)

## ✨ Highlights
<details close>
<summary>Support both <b>Sync</b> and <b>Async</b></summary>
</details>
<details close>
<summary>Authentication</summary><br>
<ul>
<li>Log in with your Poe tokens</li>
<li>Auto Proxy requests</li>
<li>Specify Proxy context</li>
</ul>
</details>
<details close>
<summary>Message Automation</summary><br>
<ul>
<li>Create new chat thread</li>
<li>Send messages</li>
<li>Stream bot responses</li>
<li>Send concurrent messages</li>
<li>Retry the last message</li>
<li>Support file attachments</li>
<li>Retrieve suggested replies</li>
<li>Stop message generation</li>
<li>Delete chat threads</li>
<li>Clear conversation context</li>
<li>Purge messages of 1 bot</li>
<li>Purge all messages of user</li>
<li>Fetch previous messages</li>
<li>Share and import messages</li>
<li>Get citations</li>
</ul>
</details>
<details close>
<summary>Chat Management</summary><br>
<ul>
<li>Get Chat Ids & Chat Codes of bot(s)</li>
<li>Get subscription info and remaining points</li>
</ul>
</details>
<details close>
<summary>Bot Management</summary><br>
<ul>
<li>Get bot info</li>
<li>Get available creation models</li>
<li>Create custom bot</li>
<li>Edit custom bot</li>
<li>Delete a custom bot</li>
</ul>
</details>
<details close>
<summary>Knowledge Base Customization</summary><br>
<ul>
<li>Get available knowledge bases</li>
<li>Upload knowledge bases for custom bots</li>
<li>Edit knowledge bases for custom bots</li>
</ul>
</details>
<details close>
<summary>Discovery</summary><br>
<ul>
<li>Get available bots</li>
<li>Get a user's bots</li>
<li>Get available categories</li>
<li>Explore 3rd party bots and users</li>
</ul>
</details>
<details close>
<summary>Bots Group Chat <b>(Beta)</b></summary><br>
<ul>
<li>Create a group chat</li>
<li>Delete a group chat</li>
<li>Get created groups</li>
<li>Get group data</li>
<li>Save group chat history</li>
<li>Load group chat history</li>
</ul>
</details>

## 🔧 Installation
- First, install this library with the following command:
```ShellSession
pip install -U poe-api-wrapper
```
Or you can install auto-proxy version of this library for **Python 3.9+**
```ShellSession
pip install -U 'poe-api-wrapper[proxy]'
```
Quick setup for Async Client:
```py
from poe_api_wrapper import AsyncPoeApi
import asyncio
tokens = {
    'p-b': ..., 
    'p-lat': ...,
}

async def main():
    client = await AsyncPoeApi(tokens=tokens).create()
    message = "Explain quantum computing in simple terms"
    async for chunk in client.send_message(bot="gpt3_5", message=message):
        print(chunk["response"], end='', flush=True)
        
asyncio.run(main())
```
- You can run an example of this library:
```py
from poe_api_wrapper import PoeExample
tokens = {
    'p-b': ..., 
    'p-lat': ...,
}
PoeExample(tokens=tokens).chat_with_bot()
```
- This library also supports command-line interface:
```ShellSession
poe -b P-B_HERE -lat P-LAT_HERE -f FORMKEY_HERE
```
> [!TIP]
> Type `poe -h` for more info

<img src="https://i.imgur.com/oAkTHfB.png" width="100%" height="auto">

## 🦄 Documentation
### Available Default Bots
| Display Name            | Model                     | Token Limit | Words | Access Type                                                     |
| ----------------------- | ------------------------- | ----------- | ----- | --------------------------------------------------------------- |
| Assistant               | capybara                  | 4K          | 3K    | ![Free](https://img.shields.io/badge/free-2feb7a)               |
| Claude-3.5-Sonnet       | claude_3_igloo            | 4K          | 3K    | ![Free](https://img.shields.io/badge/free-2feb7a)               |
| Claude-3-Opus           | claude_2_1_cedar          | 4K          | 3K    | ![Subscriber](https://img.shields.io/badge/subscriber-fc4747)   |
| Claude-3-Sonnet         | claude_2_1_bamboo         | 4K          | 3K    | ![Free](https://img.shields.io/badge/free-2feb7a)               |
| Claude-3-Haiku          | claude_3_haiku            | 4K          | 3K    | ![Free](https://img.shields.io/badge/free-2feb7a)               |
| Claude-3.5-Sonnet-200k  | claude_3_igloo_200k       | 200K        | 150K  | ![Free](https://img.shields.io/badge/free-2feb7a)               |
| Claude-3-Opus-200k      | claude_3_opus_200k        | 200K        | 150K  | ![Subscriber](https://img.shields.io/badge/subscriber-fc4747)   |
| Claude-3-Sonnet-200k    | claude_3_sonnet_200k      | 200K        | 150K  | ![Subscriber](https://img.shields.io/badge/subscriber-fc4747)   |
| Claude-3-Haiku-200k     | claude_3_haiku_200k       | 200K        | 150K  | ![Free](https://img.shields.io/badge/free-2feb7a)               |
| Claude-2                | claude_2_short            | 4K          | 3K    | ![Subscriber](https://img.shields.io/badge/subscriber-fc4747)   |
| Claude-2-100k           | a2_2                      | 100K        | 75K   | ![Subscriber](https://img.shields.io/badge/subscriber-fc4747)   |
| Claude-instant          | a2                        | 9K          | 7K    | ![Free](https://img.shields.io/badge/free-2feb7a)               |
| Claude-instant-100k     | a2_100k                   | 100K        | 75K   | ![Free](https://img.shields.io/badge/free-2feb7a)               |
| GPT-3.5-Turbo           | chinchilla                | 4K          | 3K    | ![Free](https://img.shields.io/badge/free-2feb7a)               |
| GPT-3.5-Turbo-Raw       | gpt3_5                    | 2k          | 1.5K  | ![Free](https://img.shields.io/badge/free-2feb7a)               |
| GPT-3.5-Turbo-Instruct  | chinchilla_instruct       | 2K          | 1.5K  | ![Free](https://img.shields.io/badge/free-2feb7a)               |
| ChatGPT-16k             | agouti                    | 16K         | 12K   | ![Subscriber](https://img.shields.io/badge/subscriber-fc4747)   |
| GPT-4-Classic           | gpt4_classic              | 2K          | 1.5K  | ![Subscriber](https://img.shields.io/badge/subscriber-fc4747)   |
| GPT-4-Turbo             | beaver                    | 4K          | 3K    | ![Subscriber](https://img.shields.io/badge/subscriber-fc4747)   |
| GPT-4-Turbo-128k        | vizcacha                  | 128K        | 96K   | ![Subscriber](https://img.shields.io/badge/subscriber-fc4747)   |
| GPT-4o                  | gpt4_o                    | 4k          | 3K    | ![Free](https://img.shields.io/badge/free-2feb7a)               |
| GPT-4o-128k             | gpt4_o_128k               | 128K        | 96K   | ![Subscriber](https://img.shields.io/badge/subscriber-fc4747)   |
| GPT-4o-Mini             | gpt4_o_mini               | 4K          | 3K    | ![Free](https://img.shields.io/badge/free-2feb7a)               |
| GPT-4o-Mini-128k        | gpt4_o_mini_128k          | 128K        | 96K    | ![Free](https://img.shields.io/badge/free-2feb7a)              |
| Google-PaLM             | acouchy                   | 8K          | 6K    | ![Free](https://img.shields.io/badge/free-2feb7a)               |
| Code-Llama-13b          | code_llama_13b_instruct   | 4K          | 3K    | ![Free](https://img.shields.io/badge/free-2feb7a)               |
| Code-Llama-34b          | code_llama_34b_instruct   | 4K          | 3K    | ![Free](https://img.shields.io/badge/free-2feb7a)               |
| Solar-Mini              | upstage_solar_0_70b_16bit | 2K          | 1.5K  | ![Free](https://img.shields.io/badge/free-2feb7a)               |
| Gemini-1.5-Flash-Search | gemini_pro_search         | 4K          | 3K    | ![Free](https://img.shields.io/badge/free-2feb7a)               |
| Gemini-1.5-Pro-2M       | gemini_1_5_pro_1m         | 2M          | 1.5M  | ![Subscriber](https://img.shields.io/badge/subscriber-fc4747)   |
> [!IMPORTANT]  
> The data on token limits and word counts listed above are approximate and may not be entirely accurate, as the pre-prompt engineering process of poe.com is private and not publicly disclosed. 
>
> The table above only shows bots with different display names from their models. Other bots on poe.com have the same display name as model.

### How to get your Token

#### Getting p-b and p-lat cookies (*required*)
Sign in at https://poe.com/

F12 for Devtools (Right-click + Inspect)
- Chromium: Devtools > Application > Cookies > poe.com
- Firefox: Devtools > Storage > Cookies
- Safari: Devtools > Storage > Cookies

Copy the values of `p-b` and `p-lat` cookies

#### Getting formkey (*optional*)
> [!IMPORTANT] 
> By default, **poe-api-wrapper** will automatically retrieve formkey for you. If it doesn't work, please pass this token manually by following these steps:

There are two ways to get formkey:

F12 for Devtools (Right-click + Inspect)

- 1st Method: Devtools > Network > gql_POST > Headers > Poe-Formkey

    Copy the value of `Poe-Formkey`

- 2nd Method: Devtools > Console > Type: `allow pasting` > Paste this script: `window.ereNdsRqhp2Rd3LEW()`

    Copy the result

### OpenAI
<details close>
<summary>Read Docs</summary>

#### Available Routes

- /models
- /chat/completions
- /images/generations
- /images/edits
- /v1/models
- /v1/chat/completions
- /v1/images/generations
- /v1/images/edits

#### Quick Setup
- First, install the additional packages:
```ShellSession
pip install -U 'poe-api-wrapper[llm]'
```
- Clone the repo or use the same setup in `openai` folder:
```ShellSession
git clone https://github.com/snowby666/poe-api-wrapper.git
cd poe-api-wrapper\poe_api_wrapper\openai
```
- Modify secrets.json with your own tokens
  
- Run the FastAPI server:
```ShellSession
python api.py
```
- Run the examples:
```ShellSession
python example.py
```

#### Built-in completion (WIP)

#### OpenAI Proxy Server
- Start the server
```py
from poe_api_wrapper import PoeServer
tokens = [
    {"p-b": "XXXXXXXX", "p-lat": "XXXXXXXX"},
    {"p-b": "XXXXXXXX", "p-lat": "XXXXXXXX"},
    {"p-b": "XXXXXXXX", "p-lat": "XXXXXXXX"}
]
PoeServer(tokens=tokens)

# You can also specify address and port (default is 127.0.0.1:8000)
PoeServer(tokens=tokens, address="0.0.0.0", port="8080")
```

##### Chat
- Non-streamed example:
```py
import openai 
client = openai.OpenAI(api_key="anything", base_url="http://127.0.0.1:8000/v1/", default_headers={"Authorization": "Bearer anything"})

response = client.chat.completions.create(
    model="gpt-3.5-turbo", 
    messages = [
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": "Hello!"}
            ]
)

print(response.choices[0].message.content)
```
- Streaming example:
```py
import openai 
client = openai.OpenAI(api_key="anything", base_url="http://127.0.0.1:8000/v1/", default_headers={"Authorization": "Bearer anything"})

stream = client.chat.completions.create(
    model="gpt-3.5-turbo", 
    messages = [
                {"role": "user", "content": "this is a test request, write a short poem"}
            ],
    stream=True
)

for chunk in stream:
    print(chunk.choices[0].delta.content or "", end="", flush=True)

# Set max_tokens
stream_2 = client.chat.completions.create(
    model="claude-instant", 
    messages = [
                {"role": "user", "content": "Can you tell me about the creation of blackholes?"}
            ],
    stream=True,
    max_tokens=20, # if max_tokens reached, finish_reason will be 'length'
)

for chunk in stream_2:
    print(chunk.choices[0].delta.content or "", end="", flush=True)

# Include usage 
stream_3 = client.chat.completions.create(
    model="claude-instant", 
    messages = [
                {"role": "user", "content": "Write a 100-character meta description for my blog post about llamas"}
            ],
    stream=True,
    max_tokens=4096,
    stream_options={
		"include_usage": True # last chunk contains prompts_tokens, completion_tokens and total_tokens
	}
)

for chunk in stream_3:
    print(chunk, end="\n\n", flush=True)
```
- Image input example:
```py
import openai 
client = openai.OpenAI(api_key="anything", base_url="http://127.0.0.1:8000/v1/", default_headers={"Authorization": "Bearer anything"})

# Legacy style (https://platform.openai.com/docs/api-reference/chat/create)
response = client.chat.completions.create(
    model="claude-3.5-sonnet",
    messages=[
        {
            "role": "user",
            "content": [
                {"type": "text", "text": "What's in this image?"},
                {
                    "type": "image_url",
                    "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/d/dd/Gfp-wisconsin-madison-the-nature-boardwalk.jpg/2560px-Gfp-wisconsin-madison-the-nature-boardwalk.jpg",
                }
            ],
        }
    ]
)

# New style (https://platform.openai.com/docs/guides/vision)
response = client.chat.completions.create(
    model="claude-3.5-sonnet",
    messages=[
        {
            "role": "user",
            "content": [
                {"type": "text", "text": "What's in this image?"},
                {
                    "type": "image_url",
                    "image_url": {
                        "url": "https://upload.wikimedia.org/wikipedia/commons/thumb/d/dd/Gfp-wisconsin-madison-the-nature-boardwalk.jpg/2560px-Gfp-wisconsin-madison-the-nature-boardwalk.jpg"
                    }
                }
            ],
        }
    ]
)

# Multiple images
response = client.chat.completions.create(
    model="gpt-4o",
    messages=[
    {
      "role": "user",
      "content": [
        {
          "type": "text",
          "text": "What are in these images? Is there any difference between them?",
        },
        {
          "type": "image_url",
          "image_url": {
            "url": "https://upload.wikimedia.org/wikipedia/commons/thumb/d/dd/Gfp-wisconsin-madison-the-nature-boardwalk.jpg/2560px-Gfp-wisconsin-madison-the-nature-boardwalk.jpg",
          },
        },
        {
          "type": "image_url",
          "image_url": {
            "url": "https://imgcdn.stablediffusionweb.com/2024/4/29/0b0b8798-1965-4e3d-b0a8-d153728320d4.jpg",
          }
        }
      ]
    }
  ]
)

# Base64 image
import base64

# Function to encode the image
def encode_image(image_path):
  with open(image_path, "rb") as image_file:
    return base64.b64encode(image_file.read()).decode('utf-8')

# Path to your image
image_path = "path_to_your_image.jpg"

# Getting the base64 string
base64_image = encode_image(image_path)

response = client.chat.completions.create(
    model="gpt-4o",
    messages=[
    {
      "role": "user",
      "content": [
        {
          "type": "text",
          "text": "What’s in this image?"
        },
        {
          "type": "image_url",
          "image_url": {
            "url": f"data:image/jpeg;base64,{base64_image}"
          }
        }
      ]
    }
  ]
)

print(response.choices[0].message.content)
```
- Function calling example:
```py
import openai, json
client = openai.OpenAI(api_key="anything", base_url="http://127.0.0.1:8000/v1/", default_headers={"Authorization": "Bearer anything"})

TEST_MODEL = "gpt-4o-mini"

# Example dummy function hard coded to return the same weather
# In production, this could be your backend API or an external API
def get_current_temperature(location, unit="fahrenheit"):
    """Get the current weather in a given location"""
    if "tokyo" in location.lower():
        return json.dumps({"location": "Tokyo", "temperature": "10", "unit": unit})
    elif "san francisco" in location.lower():
        return json.dumps({"location": "San Francisco", "temperature": "72", "unit": unit})
    elif "paris" in location.lower():
        return json.dumps({"location": "Paris", "temperature": "22", "unit": unit})
    else:
        return json.dumps({"location": location, "temperature": "unknown"})
    
def get_rain_probability(location):
    """Get the probability of rain in a given location"""
    if "tokyo" in location.lower():
        return json.dumps({"location": "Tokyo", "rain_probability": "10%"})
    elif "san francisco" in location.lower():
        return json.dumps({"location": "San Francisco", "rain_probability": "20%"})
    elif "paris" in location.lower():
        return json.dumps({"location": "Paris", "rain_probability": "30%"})
    else:
        return json.dumps({"location": location, "rain_probability": "unknown"})
    
def run_conversation():
    # Step 1: send the conversation and available functions to the model
    messages = [
        {'role': 'user', 'content': "Hello there. What the weather like in Tokyo?"},
        {'role': 'assistant', 'content': "Let me check the weather for you."},
        {'role': 'user', 'content': "What is the chance of raining in paris? Can you also tell me the temperature in Tokyo and LA?"},
                ]
    tools = [
    {
      "type": "function",
      "function": {
        "name": "get_current_temperature",
        "description": "Get the current temperature for a specific location",
        "parameters": {
          "type": "object",
          "properties": {
            "location": {
              "type": "string",
              "description": "The city and state, e.g., San Francisco, CA"
            },
            "unit": {
              "type": "string",
              "enum": ["Celsius", "Fahrenheit"],
              "description": "The temperature unit to use. Infer this from the user's location."
            }
          },
          "required": ["location", "unit"]
        }
      }
    },
    {
      "type": "function",
      "function": {
        "name": "get_rain_probability",
        "description": "Get the probability of rain for a specific location",
        "parameters": {
          "type": "object",
          "properties": {
            "location": {
              "type": "string",
              "description": "The city and state, e.g., San Francisco, CA"
            }
          },
          "required": ["location"]
        }
      }
    }
  ]
    response = client.chat.completions.create(
        model=TEST_MODEL,
        messages=messages,
        tools=tools,
        tool_choice={"type": "function", "function": {"name": "get_current_temperature"}},
    )
    response_message = response.choices[0].message
    print("\n", response_message, "\n")
        
    tool_calls = response_message.tool_calls
    # Step 2: check if the model wanted to call a function
    if tool_calls:
        # Step 3: call the function
        # Note: the JSON response may not always be valid; be sure to handle errors
        available_functions = {
            "get_current_temperature": get_current_temperature,
            "get_rain_probability": get_rain_probability
        }  # only two functions in this example, but you can have multiple
        messages.append(response_message)  # extend conversation with assistant's reply
        # Step 4: send the info for each function call and function response to the model
        for tool_call in tool_calls:
            print(tool_call, "\n")
            function_name = tool_call.function.name
            function_to_call = available_functions[function_name]
            function_args = json.loads(tool_call.function.arguments)
            function_response = function_to_call(**function_args)
            messages.append(
                {
                    "tool_call_id": tool_call.id,
                    "role": "tool",
                    "name": function_name,
                    "content": function_response,
                }
            )  # extend conversation with function response
    second_response = client.chat.completions.create(
        model=TEST_MODEL,
        messages=messages,
    )  # get a new response from the model where it can see the function response
    return second_response.choices[0].message.content

print(run_conversation())
```

##### Images
- Create image example:
```py
import openai
client = openai.OpenAI(api_key="anything", base_url="http://127.0.0.1:8000/v1/", default_headers={"Authorization": "Bearer anything"})

images_url = client.images.generate(
  model="playground-v2.5",
  prompt="A cute baby sea otter",
  n=2, # The number of images to generate
  size="1792x1024" # The size of image (view models.json for available sizes)
)

print(images_url)
```
- Edit image example:
```py
import openai
client = openai.OpenAI(api_key="anything", base_url="http://127.0.0.1:8000/v1/", default_headers={"Authorization": "Bearer anything"})

images_url = client.images.edit(
  image="https://imgcdn.stablediffusionweb.com/2024/4/29/0b0b8798-1965-4e3d-b0a8-d153728320d4.jpg",
  model="sdxl",
  prompt="A cute baby sea otter wearing a raincoat",
  n=1, # The number of images to generate
  size="1024x1024" # The size of image (view models.json for available sizes)
)

print(images_url)
```

##### Models
- List models example:
```py
import openai
client = openai.OpenAI(api_key="anything", base_url="http://127.0.0.1:8000/v1/", default_headers={"Authorization": "Bearer anything"})

models = client.models.list()

print(models)
```
- Retrieve model example:
```py
import openai
client = openai.OpenAI(api_key="anything", base_url="http://127.0.0.1:8000/v1/", default_headers={"Authorization": "Bearer anything"})

model = client.models.retrieve("gpt-3.5-turbo-instruct")

print(model)
```
</details>

### Basic Usage
<details close>
<summary>Read Docs</summary>

- Connecting to the API
```py
tokens = {
    'p-b': 'p-b cookie here',
    'p-lat': 'p-lat cookie here',
}

# Default setup
from poe_api_wrapper import PoeApi
client = PoeApi(tokens=tokens)

# Using Client with auto_proxy (default is False)
client = PoeApi(tokens=tokens, auto_proxy=True)

# Passing proxies manually
proxy_context = [
    {"https://":X1, "http://":X1},
    {"https://":X2, "http://":X2},
    ...
]

client = PoeApi(tokens=tokens, proxy=proxy_context) 

# Add formkey and cloudflare cookies to pass challenges
tokens = {
    'p-b': 'p-b cookie here',
    'p-lat': 'p-lat cookie here',
    'formkey': 'formkey here',
    '__cf_bm': '__cf_bm cookie here', 
    'cf_clearance': 'cf_clearance cookie here'
}
```
- Getting Chat Ids & Chat Codes
```py
# Get chat data of all bots (this will fetch all available threads)
print(client.get_chat_history()['data'])
>> Output:
{'chinchilla': [{'chatId': 74397929, 'chatCode': '2ith0h11zfyvsta1u3z', 'id': 'Q2hhdDo3NDM5NzkyOQ==', 'title': 'Comparison'}], 'code_llama_7b_instruct': [{'chatId': 74397392, 'chatCode': '2ithbduzsysy3g178hb', 'id': 'Q2hhdDo3NDM5NzM5Mg==', 'title': 'Decent Programmers'}], 'a2': [{'chatId': 74396838, 'chatCode': '2ith9nikybn4ksn51l8', 'id': 'Q2hhdDo3NDM5NjgzOA==', 'title': 'Reverse Engineering'}, {'chatId': 74396452, 'chatCode': '2ith79n4x0p0p8w5yue', 'id': 'Q2hhdDo3NDM5NjQ1Mg==', 'title': 'Clean Code'}], 'leocooks': [{'chatId': 74396246, 'chatCode': '2ith82wj0tjrggj46no', 'id': 'Q2hhdDo3NDM5NjI0Ng==', 'title': 'Pizza perfection'}], 'capybara': [{'chatId': 74396020, 'chatCode': '2ith5o3p8c5ajkdwd3k', 'id': 'Q2hhdDo3NDM5NjAyMA==', 'title': 'Greeting'}]}

# Get chat data of a bot (this will fetch all available threads)
print(client.get_chat_history("a2")['data'])
>> Output:
{'a2': [{'chatId': 74396838, 'chatCode': '2ith9nikybn4ksn51l8', 'id': 'Q2hhdDo3NDM5NjgzOA==', 'title': 'Reverse Engineering'}, {'chatId': 74396452, 'chatCode': '2ith79n4x0p0p8w5yue', 'id': 'Q2hhdDo3NDM5NjQ1Mg==', 'title': 'Clean Code'}]}

# Get a defined number of most recent chat threads (using count param will ignore interval param)
# Fetching all bots
print(client.get_chat_history(count=20)['data'])
# Fetching 1 bot
print(client.get_chat_history(bot="a2", count=20)['data'])

# You can pass the number of bots fetched for each interval to both functions. (default is 50)
# Fetching 200 chat threads of all bots each interval
print(client.get_chat_history(interval=200)['data'])
# Fetching 200 chat threads of a bot each interval
print(client.get_chat_history(bot="a2", interval=200)['data'])

# Pagination Example:
# Fetch the first 20 chat threads
history = client.get_chat_history(count=20)
pages = [history['data']]
new_cursor = history['cursor']

# Set a while loop with a condition of your choice
while new_cursor != None:
    # Fetch the next 20 chat threads with new_cursor
    new_history = client.get_chat_history(count=20, cursor=new_cursor)
    # Append the next 20 chat threads 
    new_cursor = new_history['cursor']
    pages.append(new_history['data'])

# Print the pages (20 chat threads each page)
for page in range(len(pages)):
    print(f'This is page {page+1}')
    for bot, value in pages[page].items():
        for thread in value:
            print({bot: thread})
```
- Getting subscription info and remaining points
```py
data = client.get_settings()
print(data)
```
- Sending messages & Streaming responses 
```py
bot = "a2"
message = "What is reverse engineering?"

# Create new chat thread
# Streamed example:
for chunk in client.send_message(bot, message):
    print(chunk["response"], end="", flush=True)
print("\n")

# Non-streamed example:
for chunk in client.send_message(bot, message):
    pass
print(chunk["text"])

# You can get chatCode and chatId of created thread to continue the conversation
chatCode = chunk["chatCode"]
chatId = chunk["chatId"]
# You can also retrieve msgPrice
msgPrice = chunk["msgPrice"]

# Send message to an existing chat thread
# 1. Using chatCode
for chunk in client.send_message(bot, message, chatCode="2i58ciex72dom7im83r"):
    print(chunk["response"], end="", flush=True)
# 2. Using chatId
for chunk in client.send_message(bot, message, chatId=59726162):
    print(chunk["response"], end="", flush=True)
# 3. Specify msgPrice manually (the wrapper automatically gets this, but you can also pass the param for less resources consumed)
for chunk in client.send_message(bot, message, chatId=59726162, msgPrice=msgPrice):
    print(chunk["response"], end="", flush=True)
```
> [!NOTE]
> Display names are the same as the codenames for custom bots, you can simply pass the bot's display name into `client.send_message(bot, message)`
- Sending concurrent messages
```py
# Use at your own risk, increase timeout to avoid ratelimit (default is 20)

import time, threading
thread_count = 0

def message_thread(prompt, counter):
    global thread_count
    try:
        for chunk in client.send_message("gpt3_5", prompt):
            pass
        print(prompt+"\n"+chunk["text"]+"\n"*3)
        thread_count -= 1
    except Exception as e:
        pass

prompts = [
  "Write a paragraph about the impact of social media on mental health.",
  "Write a paragraph about the history and significance of the Olympic Games.",
  "Write a paragraph about the effects of climate change on the world's oceans.",
  "Write a paragraph about the benefits and drawbacks of remote work for employees and companies.",
  "Write a paragraph about the role of technology in modern education.",
  "Write a paragraph about the history and impact of the Civil Rights Movement in America.",
  "Write a paragraph about the impact of COVID-19 on global economies.",
  "Write a paragraph about the rise and fall of the Roman Empire.",
  "Write a paragraph about the benefits and drawbacks of genetically modified organisms (GMOs).",
  "Write a paragraph about the impact of globalization on cultural identity.",
  "Write a paragraph about the history and significance of the Mona Lisa painting.",
  "Write a paragraph about the benefits and drawbacks of renewable energy sources.",
  "Write a paragraph about the impact of social media on political discourse.",
  "Write a paragraph about the history and impact of the Industrial Revolution.",
  "Write a paragraph about the benefits and drawbacks of online shopping for consumers and businesses.",
  "Write a paragraph about the impact of artificial intelligence on the job market.",
  "Write a paragraph about the history and significance of the Great Wall of China.",
  "Write a paragraph about the benefits and drawbacks of standardized testing in schools.",
  "Write a paragraph about the impact of the feminist movement on women's rights.",
  "Write a paragraph about the history and impact of the American Revolution."
]

   
for i in range(len(prompts)):
    t = threading.Thread(target=message_thread, args=(prompts[i], i), daemon=True)
    t.start()
    thread_count += 1
    time.sleep(1)

while thread_count:
    time.sleep(0.01)
```
- Retrying the last message
```py
for chunk in client.retry_message(chatCode):
    print(chunk['response'], end='', flush=True)
```
- Adding file attachments
```py
# Web urls example:
file_urls = ["https://elinux.org/images/c/c5/IntroductionToReverseEngineering_Anderson.pdf", 
            "https://www.kcl.ac.uk/warstudies/assets/automation-and-artificial-intelligence.pdf"]
for chunk in client.send_message(bot, "Compare 2 files and describe them in 300 words", file_path=file_urls):
    print(chunk["response"], end="", flush=True)
    
# Local paths example:
local_paths = ["c:\\users\\snowby666\\hello_world.py"]
for chunk in client.send_message(bot, "What is this file about?", file_path=local_paths):
    print(chunk["response"], end="", flush=True)
```
> [!NOTE]
> The files size limit is different for each model.
- Retrieving suggested replies 
```py
for chunk in client.send_message(bot, "Introduce 5 books about clean code", suggest_replies=True):
    print(chunk["response"], end="", flush=True)
print("\n")

for reply in chunk["suggestedReplies"]:
    print(reply)
```
- Stopping message generation
```py
# You can use an event to trigger this function
# Example:
# Note that keyboard library may not be compatible with MacOS, Linux, Ubuntu
import keyboard
for chunk in client.send_message(bot, message):
    print(chunk["response"], end="", flush=True)
    # Press Q key to stop the generation
    if keyboard.is_pressed('q'):
        client.cancel_message(chunk)
        print("\nMessage is now cancelled")
        break 
```
- Deleting chat threads
```py
# Delete 1 chat
# Using chatCode
client.delete_chat(bot, chatCode="2i58ciex72dom7im83r")
# Using chatId
client.delete_chat(bot, chatId=59726162)

# Delete n chats
# Using chatCode
client.delete_chat(bot, chatCode=["LIST_OF_CHAT_CODES"])
# Using chatId
client.delete_chat(bot, chatId=["LIST_OF_CHAT_IDS"])

# Delete all chats of a bot
client.delete_chat(bot, del_all=True)
```
- Clearing conversation context
```py
# 1. Using chatCode
client.chat_break(bot, chatCode="2i58ciex72dom7im83r")
# 2. Using chatId
client.chat_break(bot, chatId=59726162)
```
- Purging messages of 1 bot
  
```py
# Purge a defined number of messages (default is 50)
# 1. Using chatCode
client.purge_conversation(bot, chatCode="2i58ciex72dom7im83r", count=10)
# 2. Using chatId
client.purge_conversation(bot, chatId=59726162, count=10)

# Purge all messsages of the thread
# 1. Using chatCode
client.purge_conversation(bot, chatCode="2i58ciex72dom7im83r", del_all=True)
# 2. Using chatId
client.purge_conversation(bot, chatId=59726162,  del_all=True)
```
- Purging all messages of user
```py
client.purge_all_conversations()
```
- Fetching previous messsages
```py
# Get a defined number of messages (default is 50)
# Using chatCode
previous_messages = client.get_previous_messages('code_llama_34b_instruct', chatCode='2itg2a7muygs42v1u0k', count=2)
# Using chatId
previous_messages = client.get_previous_messages('code_llama_34b_instruct', chatId=74411139, count=2)
for message in previous_messages:
    print(message)
>> Output:
{'author': 'human', 'text': 'nice to meet you', 'messageId': 2861709279}
{'author': 'code_llama_34b_instruct', 'text': " Nice to meet you too! How are you doing today? Is there anything on your mind that you'd like to talk about? I'm here to listen and help", 'messageId': 2861873125}

# Get messages with extended metadata (state and creationTime)
# Using chatCode
previous_messages = client.get_previous_messages('code_llama_34b_instruct', chatCode='2itg2a7muygs42v1u0k', include_extended=True)
# Using chatId
previous_messages = client.get_previous_messages('code_llama_34b_instruct', chatId=74411139, include_extended=True)
>> Output:
{'author': 'human', 'text': 'hi there', 'messageId': 2861363514, 'state': 'complete', 'creationTime': 1732029401216595}

# Get all previous messages
# Using chatCode
previous_messages = client.get_previous_messages('code_llama_34b_instruct', chatCode='2itg2a7muygs42v1u0k', get_all=True)
# Using chatId
previous_messages = client.get_previous_messages('code_llama_34b_instruct', chatId=74411139, get_all=True)
for message in previous_messages:
    print(message)
>> Output:
{'author': 'human', 'text': 'hi there', 'messageId': 2861363514}
{'author': 'code_llama_34b_instruct', 'text': " Hello! It's nice to meet you. Is there something I can help you with or would you like to chat?", 'messageId': 2861363530}
{'author': 'chat_break', 'text': "", 'messageId': 2872383991}
{'author': 'human', 'text': 'nice to meet you', 'messageId': 2861709279}
{'author': 'code_llama_34b_instruct', 'text': " Nice to meet you too! How are you doing today? Is there anything on your mind that you'd like to talk about? I'm here to listen and help", 'messageId': 2861873125}
```
> [!NOTE]
> It will fetch messages from the latest to the oldest, but the order to be displayed is reversed.
- Getting available knowledge bases
```py
# Get a defined number of sources (default is 10)
print(client.get_available_knowledge(botName="BOT_NAME", count=2))
>> Output:
{'What is Quora?': [86698], 'Founders of Quora': [86705]}
# Get all available sources
print(client.get_available_knowledge(botName="BOT_NAME", get_all=True))
```
- Uploading knowledge bases
```py
# Web urls example:
file_urls = ["https://elinux.org/images/c/c5/IntroductionToReverseEngineering_Anderson.pdf", 
            "https://www.kcl.ac.uk/warstudies/assets/automation-and-artificial-intelligence.pdf"]
source_ids = client.upload_knowledge(file_path=file_urls)
print(source_ids)
>> Output:
{'er-1-intro_to_re.pdf': [86344], 'automation-and-artificial-intelligence.pdf': [86345]}

# Local paths example:
local_paths = ["c:\\users\\snowby666\\hello_world.py"]
source_ids = client.upload_knowledge(file_path=local_paths)
print(source_ids)
>> Output:
{'hello_world.py': [86523]}

# Plain texts example:
knowledges = [
    {
        "title": "What is Quora?",
        "content": "Quora is a popular online platform that enables users to ask questions on various topics and receive answers from a diverse community. It covers a wide range of subjects, from academic and professional queries to personal experiences and opinions, fostering knowledge-sharing and meaningful discussions among its users worldwide."
    },
    {
        "title": "Founders of Quora",
        "content": "Quora was founded by two individuals, Adam D'Angelo and Charlie Cheever. Adam D'Angelo, who previously served as the Chief Technology Officer (CTO) at Facebook, and Charlie Cheever, a former Facebook employee as well, launched Quora in June 2009. They aimed to create a platform that would enable users to ask questions and receive high-quality answers from knowledgeable individuals. Since its inception, Quora has grown into a widely used question-and-answer platform with a large user base and a diverse range of topics covered."
    },
]
source_ids = client.upload_knowledge(text_knowledge=knowledges)
print(source_ids)
>> Output:
{'What is Quora?': [86368], 'Founders of Quora': [86369]}

# Hybrid example:
source_ids = client.upload_knowledge(file_path=file_urls, text_knowledge=knowledges)
print(source_ids)
>> Output:
{'What is Quora?': [86381], 'Founders of Quora': [86383], 'er-1-intro_to_re.pdf': [86395], 'automation-and-artificial-intelligence.pdf': [86396]}
```
- Editing knowledge bases (Only for plain texts)
```py
client.edit_knowledge(knowledgeSourceId=86381, title='What is Quora?', content='Quora is a question-and-answer platform where users can ask questions, provide answers, and engage in discussions on various topics.')
```
- Getting bot info
```py
bot = 'gpt-4'
print(client.get_botInfo(handle=bot))
>> Output:
{'handle': 'GPT-4', 'model': 'beaver', 'supportsFileUpload': True, 'messageTimeoutSecs': 15, 'displayMessagePointPrice': 350, 'numRemainingMessages': 20, 'viewerIsCreator': False, 'id': 'Qm90OjMwMDc='}
```
- Getting available creation models
```py
print(client.get_available_creation_models())
>> Output:
{'text': ['claude_3_igloo', 'gpt4_o_mini', 'gpt4_o', 'gemini_1_5_flash', 'gemini_1_5_pro', 'claude_2_1_bamboo', 'claude_3_haiku', 'claude_2_1_cedar', 'gemini_1_5_flash_128k', 'gemini_1_5_pro_128k', 'gemini_1_5_flash_1m', 'gemini_1_5_pro_1m', 'gpt4_o_mini_128k', 'gpt4_o_128k', 'beaver', 'gemini_pro', 'chinchilla', 'vizcacha', 'claude_3_igloo_200k', 'claude_3_sonnet_200k', 'claude_3_haiku_200k', 'claude_3_opus_200k', 'mixtral8x7bchat', 'claude_2_short', 'a2_2', 'mythomaxl213b', 'a2', 'a2_100k'], 'image': ['playgroundv25', 'ideogram', 'dalle3', 'stablediffusion3', 'sd3turbo', 'stablediffusionxl'], 'video': ['pika']}
```
- Creating a new Bot
```py
client.create_bot(handle="BOT_NAME", prompt="PROMPT_HERE", base_model="a2")

# Using knowledge bases (you can use source_ids from uploaded knowledge bases for your custom bot)
client.create_bot(handle="BOT_NAME", prompt="PROMPT_HERE", base_model="a2", knowledgeSourceIds=source_ids, shouldCiteSources=True)
```
- Editing a Bot
```py
client.edit_bot(handle="BOT_NAME", prompt="PROMPT_HERE", new_handle="NEW_BOT_NAME", base_model='chinchilla')

# Adding knowledge bases 
client.edit_bot(handle="BOT_NAME", prompt="PROMPT_HERE", new_handle="NEW_BOT_NAME", base_model='chinchilla', knowledgeSourceIdsToAdd=source_ids, shouldCiteSources=True)

# Removing knowledge bases
client.edit_bot(handle="BOT_NAME", prompt="PROMPT_HERE", new_handle="NEW_BOT_NAME", base_model='chinchilla', knowledgeSourceIdsToRemove=source_ids, shouldCiteSources=True)
```
> [!TIP]
> You can also use both `knowledgeSourceIdsToAdd` and `knowledgeSourceIdsToRemove` at the same time.
- Deleting a Bot
```py
client.delete_bot(handle="BOT_NAME")
```
- Getting available bots (your bots section)
```py
# Get a defined number of bots (default is 25)
print(client.get_available_bots(count=10))
# Get all available bots
print(client.get_available_bots(get_all=True))
```
- Getting a user's bots
```py
handle = 'poe'
print(client.get_user_bots(user=handle))
```
- Getting available categories
```py
print(client.get_available_categories())
>> Output:
['Official', 'Popular', 'New', 'ImageGen', 'AI', 'Professional', 'Funny', 'History', 'Cooking', 'Advice', 'Mind', 'Programming', 'Travel', 'Writing', 'Games', 'Learning', 'Roleplay', 'Utilities', 'Sports', 'Music']
```
- Exploring 3rd party bots and users
```py
# Explore section example:
# Get a defined number of bots (default is 50)
print(client.explore(count=10))
# Get all available bots
print(client.explore(explore_all=True))

# Search for bots by query example:
# Get a defined number of bots (default is 50)
print(client.explore(search="Midjourney", count=30))
# Get all available bots
print(client.explore(search="Midjourney", explore_all=True))

# Search for bots by category example (default is defaultCategory):
# Get a defined number of bots (default is 50)
print(client.explore(categoryName="Popular", count=30))
# Get all available bots
print(client.explore(categoryName="AI", explore_all=True))

# Search for people example:
# Get a defined number of people (default is 50)
print(client.explore(search="Poe", entity_type='user', count=30))
# Get all available people
print(client.explore(search="Poe", entity_type='user', explore_all=True))
```
- Sharing & Importing messages
```py
# Share a defined number of messages (from the lastest to the oldest)
# Using chatCode
shareCode = client.share_chat("a2", chatCode="2roap5g8nd7s28ul836",count=10)
# Using chatId
shareCode = client.share_chat("a2", chatId=204052028,count=10)

# Share all messages
# Using chatCode
shareCode = client.share_chat("a2", chatCode="2roap5g8nd7s28ul836")
# Using chatId
shareCode = client.share_chat("a2", chatId=204052028)

# Set up the 2nd Client and import messages from the shareCode
client2 = PoeApi("2nd_TOKEN_HERE")
print(client2.import_chat(bot, shareCode))
>> Output:
{'chatId': 72929127, 'chatCode': '2iw0xcem7a18wy1avd3'}
```
- Getting citations
```py
print(client.get_citations(messageId=141597902621))
```
</details>

### Bots Group Chat
<details close>
<summary>Read Docs</summary>

- Creating a group chat
```py
bots = [
    {'bot': 'yayayayaeclaude', 'name': 'Yae'}, 
    {'bot': 'gepardL', 'name': 'gepard'}, 
    {'bot': 'SayukiTokihara', 'name': 'Sayuki'}
]

client.create_group(group_name='Hangout', bots=bots) 
```
> [!NOTE]
> `bot` arg is the model/displayName.
> `name` arg is the one you'd mention them in group chat.
- Sending messages and Streaming responses in group chat
```py
# User engagement example:
while True: 
    message = str(input('\n\033[38;5;121mYou : \033[0m'))
    prev_bot = ""
    for chunk in client.send_message_to_group(group_name='Hangout', message=message):
        if chunk['bot'] != prev_bot:
            print(f"\n\033[38;5;121m{chunk['bot']} : \033[0m", end='', flush=True)
            prev_bot = chunk['bot']
        print(chunk['response'], end='', flush=True)
    print('\n')

# Auto-play example:
while True:
    prev_bot = ""
    for chunk in client.send_message_to_group(group_name='Hangout', autoplay=True):
        if chunk['bot'] != prev_bot:
            print(f"\n\033[38;5;121m{chunk['bot']} : \033[0m", end='', flush=True)
            prev_bot = chunk['bot']
        print(chunk['response'], end='', flush=True)
    print('\n')

# Preset history example:
preset_path = "c:\\users\\snowby666\\preset.json"
prev_bot = ""
for chunk in client.send_message_to_group(group_name='Hangout', autoplay=True, preset_history=preset_path):
    if chunk['bot'] != prev_bot:
        print(f"\n\033[38;5;121m{chunk['bot']} : \033[0m", end='', flush=True)
        prev_bot = chunk['bot']
    print(chunk['response'], end='', flush=True)
print('\n')
while True:
    for chunk in client.send_message_to_group(group_name='Hangout', autoplay=True):
        if chunk['bot'] != prev_bot:
            print(f"\n\033[38;5;121m{chunk['bot']} : \033[0m", end='', flush=True)
            prev_bot = chunk['bot']
        print(chunk['response'], end='', flush=True)
    print('\n')
```
> [!NOTE]
> You can also change your name in group chat by passing a new one to the above function: `client.send_message_to_group('Hangout', message=message, user='Danny')`
> If you want to auto save the conversation_log, just simply set this to true: `client.send_message_to_group('Hangout', message=message, autosave=True)`
- Deleting a group chat
```py
client.delete_group(group_name='Hangout')
```
- Getting created groups
```py
print(client.get_available_groups())
```
- Getting group data
```py
print(client.get_group(group_name='Hangout'))
```
- Saving group chat history
```py
# Save as json in the same directory
client.save_group_history(group_name='Hangout')
# Save with a local path (json only)
local_path = "c:\\users\\snowby666\\log.json"
client.save_group_history(group_name='Hangout', file_path=local_path)
```
- Loading group chat history
```py
print(client.load_group_history(file_path=local_path))
```
</details>

### Misc
<details close>
<summary>Read Docs</summary>

- How to find chatCode manually?

Here is an example, the chatCode is 23o1gxjhb9cfnlacdcd

![](https://i.imgur.com/m1zDP36.png)

- What are the file types that poe-api-wrapper support?

Currently, this API only supports these file types for adding attachments

#### Text files
| .pdf | .docx | .txt | .md | .py | .js | .ts | .html | .css | .csv | .c | .cs | .cpp | .lua | .rs | .rb | .go | .java |
| - | - | - | - | - | - | - | - | - | - | - | - | - | - | - | - | - | - |
|                                                                       |
#### Media files
| .png | .jpg | .jpeg | .gif | .mp4 | .mov | .mp3 | .wav |
| - | - | - | - | - | - | - | - |
|                               |
</details>

## 🙌 Contributing
We would love to develop poe-api-wrapper together with our community! 💕
### Run debug
First, clone this repo:
```ShellSession
git clone https://github.com/snowby666/poe-api-wrapper.git
cd poe-api-wrapper
```
Then run the test cases:
```ShellSession
python -m pip install -e .[tests]
tox
```
### Ways to contribute
- Try poe-api-wrapper and give feedback
- Add new integrations with open [PR](https://github.com/snowby666/poe-api-wrapper/pulls)
- Help with open [issues](https://github.com/snowby666/poe-api-wrapper/issues) or [create your own](https://github.com/snowby666/poe-api-wrapper/issues/new/choose)
- Share your thoughts and suggestions with us
- Request a feature by submitting a proposal
- Report a bug
- **Improve documentation:** fix incomplete or missing docs, bad wording, examples or explanations.

### Contributors
<a href="https://github.com/snowby666/poe-api-wrapper/graphs/contributors">
  <img src="https://contrib.rocks/image?repo=snowby666/poe-api-wrapper" />
</a>

<br>

<img src="https://repobeats.axiom.co/api/embed/cba15fced158acd258575d31fc14d7e5c59b07a3.svg" alt="Repobeats analytics image">

## 🤝 Copyright
This program is licensed under the [GNU GPL v3](https://github.com/snowby666/poe-api-wrapper/blob/main/LICENSE). Most code has been written by me, [snowby666](https://github.com/snowby666).

### Copyright Notice
```
snowby666/poe-api-wrapper: A simple, lightweight and efficient API wrapper for Poe.com
Copyright (C) 2023 snowby666

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <https://www.gnu.org/licenses/>.
```
