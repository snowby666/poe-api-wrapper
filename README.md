<div align="center">
<a href="https://github.com/snowby666">
<img src="https://socialify.git.ci/snowby666/poe-api-wrapper/image?font=Raleway&forks=1&issues=1&language=1&logo=https://i.ibb.co/JsNwP3B/nobgprofile-3.png&name=1&owner=1&pattern=Charlie%20Brown&pulls=1&stargazers=1&theme=Auto" width="700" height="350"></a>

<h1>Poe API Wrapper <img src="https://psc2.cf2.poecdn.net/favicon.svg" height="35"></h1>

<p><em>A simple API wrapper for Poe.com using Httpx</em></p>
</div>

<p align="center">
<a href="https://pypi.org/project/poe-api-wrapper/"><img src="https://img.shields.io/pypi/v/poe-api-wrapper"></a>
<img alt="Python Version" src="https://img.shields.io/badge/python-3.7+-blue.svg" alt="python">
<img alt="PyPI - Downloads" src="https://img.shields.io/pypi/dm/poe-api-wrapper">
<br>
</p>

## Table of Contents:
- [Table of Contents:](#table-of-contents)
- [Highlights:](#highlights)
- [Installation:](#installation)
- [Documentation:](#documentation)
  - [Available Bots:](#available-bots)
  - [How to get your Token:](#how-to-get-your-token)
  - [Basic Usage:](#basic-usage)
  - [Misc:](#misc)
- [Copyright:](#copyright)
  - [Copyright Notice:](#copyright-notice)

## Highlights:
 - Log in with your Quora's token
 - Auto Proxy requests
 - Get Chat Ids & Chat Codes of bot(s)
 - Create new chat thread
 - Send messages
 - Stream bot responses
 - Support file attachments
 - Retrieve suggested replies
 - Stop message generation
 - Delete chat threads
 - Clear conversation context
 - Purge messages of 1 bot
 - Purge all messages of user
 - Fetch previous messages
 - Create custom bot
 - Edit custom bot
 - Delete a custom bot
 - Get available bots
 - Explore 3rd party bots
 - Share and import messages
 - Support multi-chat threads

## Installation:
- First, install this library with the following command:
```sh
pip3 install -U poe-api-wrapper
```
- You can run an example of this library:
```py
from poe_api_wrapper import Poe
token = "TOKEN_HERE"
Poe.chat_with_bot(token)
```

## Documentation:
### Available Bots:
- Assistant (capybara)
- Claude-instant-100k (a2_100k)
- Claude-2-100k (a2_2)
- Claude-instant (a2)
- ChatGPT (chinchilla)
- ChatGPT-16k (agouti)
- GPT-4 (beaver)
- GPT-4-32k (vizcacha)
- Google-PaLM (acouchy)
- Llama-2-7b (llama_2_7b_chat)
- Llama-2-13b (llama_2_13b_chat)
- Llama-2-70b (llama_2_70b_chat)
- Code-Llama-7b (code_llama_7b_instruct)
- Code-Llama-13b (code_llama_13b_instruct)
- Code-Llama-34b (code_llama_34b_instruct)

### How to get your Token:
Sign in at https://www.quora.com/

F12 for Devtools (Right-click + Inspect)
- Chromium: Devtools > Application > Cookies > quora.com
- Firefox: Devtools > Storage > Cookies
- Safari: Devtools > Storage > Cookies

Copy the value of `m-b` cookie
### Basic Usage:
- Connecting to the API
```py
from poe_api_wrapper import PoeApi
client = PoeApi("TOKEN_HERE")

# Using Client with proxy (default is False)
client = PoeApi("TOKEN_HERE", proxy=True)
```
- Getting Chat Ids & Chat Codes
```py
# Get chat ids of all bots
client.get_chat_history()
# Output:
# -------------------------------------- Chat History --------------------------------------
# Chat ID  |     Chat Code       |           Bot Name            |       Chat Title
# ------------------------------------------------------------------------------------------
# 74397929 | 2ith0h11zfyvsta1u3z | chinchilla                    | Comparison
# 74397392 | 2ithbduzsysy3g178hb | code_llama_7b_instruct        | Decent Programmers
# 74396838 | 2ith9nikybn4ksn51l8 | a2                            | Reverse Engineering
# 74396452 | 2ith79n4x0p0p8w5yue | a2                            | Clean Code
# 74396246 | 2ith82wj0tjrggj46no | leocooks                      | Pizza perfection
# 74396020 | 2ith5o3p8c5ajkdwd3k | capybara                      | Greeting
# ------------------------------------------------------------------------------------------

print(client.get_chat_history())
# Output:
# {'chinchilla': [{'chatId': 74397929, 'chatCode': '2ith0h11zfyvsta1u3z', 'id': 'Q2hhdDo3NDM5NzkyOQ==', 'title': 'Comparison'}], 'code_llama_7b_instruct': [{'chatId': 74397392, 'chatCode': '2ithbduzsysy3g178hb', 'id': 'Q2hhdDo3NDM5NzM5Mg==', 'title': 'Decent Programmers'}], 'a2': [{'chatId': 74396838, 'chatCode': '2ith9nikybn4ksn51l8', 'id': 'Q2hhdDo3NDM5NjgzOA==', 'title': 'Reverse Engineering'}, {'chatId': 74396452, 'chatCode': '2ith79n4x0p0p8w5yue', 'id': 'Q2hhdDo3NDM5NjQ1Mg==', 'title': 'Clean Code'}], 'leocooks': [{'chatId': 74396246, 'chatCode': '2ith82wj0tjrggj46no', 'id': 'Q2hhdDo3NDM5NjI0Ng==', 'title': 'Pizza perfection'}], 'capybara': [{'chatId': 74396020, 'chatCode': '2ith5o3p8c5ajkdwd3k', 'id': 'Q2hhdDo3NDM5NjAyMA==', 'title': 'Greeting'}]}

# Get chat ids of a bot
print(client.get_chat_history("a2"))
# Output:
# {'a2': [{'chatId': 74396838, 'chatCode': '2ith9nikybn4ksn51l8', 'id': 'Q2hhdDo3NDM5NjgzOA==', 'title': 'Reverse Engineering'}, {'chatId': 74396452, 'chatCode': '2ith79n4x0p0p8w5yue', 'id': 'Q2hhdDo3NDM5NjQ1Mg==', 'title': 'Clean Code'}]}
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
# You can get the meaningful title as well
title = chunk["title"]

# Send message to an existing chat thread
# 1. Using chatCode
for chunk in client.send_message(bot, message, chatCode="2i58ciex72dom7im83r"):
    print(chunk["response"], end="", flush=True)
# 2. Using chatId
for chunk in client.send_message(bot, message, chatId=59726162):
    print(chunk["response"], end="", flush=True)
```
> **Note**
> Display names are the same as the codenames for custom bots, you can simply pass the bot's display name into `client.send_message(bot, message)`
- Adding file attachments
```py
# Web urls example:
file_urls = ["https://sweet.ua.pt/jpbarraca/course/er-2122/slides/er-1-intro_to_re.pdf", 
            "https://www.kcl.ac.uk/warstudies/assets/automation-and-artificial-intelligence.pdf"]
for chunk in client.send_message(bot, "Compare 2 files and describe them in 300 words", file_path=file_urls):
    print(chunk["response"], end="", flush=True)
    
# Local paths example:
local_paths = ["c:\users\snowby666\hello_world.py"]
for chunk in client.send_message(bot, "What is this file about?", file_path=local_paths):
    print(chunk["response"], end="", flush=True)
```
> **Note**
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
client.delete_chat(bot, chatID=59726162)

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
  
You can pass the number of messages to be deleted into `client.purge_conversation(bot, chatId, chatCode, count)` (the default is 50)
  
```py
# 1. Using chatCode
client.purge_conversation(bot, chatCode="2i58ciex72dom7im83r", count=10)
# 2. Using chatId
client.purge_conversation(bot, chatId=59726162, count=10)
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
# Output:
# {'author': 'human', 'text': 'nice to meet you'}
# {'author': 'code_llama_34b_instruct', 'text': " Nice to meet you too! How are you doing today? Is there anything on your mind that you'd like to talk about? I'm here to listen and help"}

# Get all previous messages
# Using chatCode
previous_messages = client.get_previous_messages('code_llama_34b_instruct', chatCode='2itg2a7muygs42v1u0k', get_all=True)
# Using chatId
previous_messages = client.get_previous_messages('code_llama_34b_instruct', chatId=74411139, get_all=True)
for message in previous_messages:
    print(message)
# Output:
# {'author': 'human', 'text': 'hi there'}
# {'author': 'code_llama_34b_instruct', 'text': " Hello! It's nice to meet you. Is there something I can help you with or would you like to chat?"}
# {'author': 'human', 'text': 'nice to meet you'}
# {'author': 'code_llama_34b_instruct', 'text': " Nice to meet you too! How are you doing today? Is there anything on your mind that you'd like to talk about? I'm here to listen and help"}
```
>**Note**
> It will fetch messages from the latest to the oldest, but the order to be displayed is vice-versa.
- Creating a new Bot
```py
client.create_bot("BOT_NAME", "PROMPT_HERE", base_model="a2")
```
- Editing a Bot
```py
client.edit_bot("(NEW)BOT_NAME", "PROMPT_HERE", base_model='chinchilla')
```
- Deleting a Bot
```py
client.delete_bot("BOT_NAME")
```
- Getting available Bots
```py
# Get a defined number of bots (default is 25)
print(client.get_available_bots(count=10))
# Get all available bots
print(client.get_available_bots(get_all=True))
```
- Exploring 3rd party bots
```py
# Explore section example:
# Get a defined number of bots (default is 50)
print(client.explore_bots(count=10))
# Get all available bots
print(client.explore_bots(explore_all=True))

# Search section example:
# Get a defined number of bots (default is 50)
print(client.explore_bots(search="Midjourney", count=30))
# Get all available bots
print(client.explore_bots(search="Midjourney", explore_all=True))
```
- Sharing & Importing messages
```py
# Share a defined number of messages (from the lastest to the oldest)
shareCode = client.share_chat(bot, count=10)
# Share all messages
shareCode = client.share_chat(bot)

# Set up the 2nd Client and import messages from the shareCode
client2 = PoeApi("2nd_TOKEN_HERE")
print(client2.import_chat(bot, shareCode))
# Output:
# {'chatId': 72929127, 'chatCode': '2iw0xcem7a18wy1avd3'}
```

### Misc:
- How to find chatCode manually?

Here is an example, the chatCode is 2i5bego6rzetfsevv5g

![](https://cdn.discordapp.com/attachments/957946068836950026/1142363043741843506/image.png)

- What are the file types that poe-api-wrapper support?

Currently, this API only supports these file types for adding attachments

| .pdf | .docx | .txt | .py | .js | .ts | .html | .css | .csv | .c | .cs | .cpp |
| - | - | - | - | - | - | - | - | - | - | - | - |
|                                               |

## Copyright:
This program is licensed under the [GNU GPL v3](https://github.com/snowby666/poe-api-wrapper/blob/main/LICENSE). All code has been written by me, [snowby666](https://github.com/snowby666).

### Copyright Notice:
```
snowby666/poe-api-wrapper: A simple API wrapper for poe.com using Httpx
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