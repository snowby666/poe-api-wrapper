<div align="center">
<a href="https://github.com/snowby666">
<img src="https://socialify.git.ci/snowby666/poe-api-wrapper/image?font=Raleway&forks=1&issues=1&language=1&logo=https://i.ibb.co/JsNwP3B/nobgprofile-3.png&name=1&owner=1&pattern=Charlie%20Brown&pulls=1&stargazers=1&theme=Auto" width="700" height="350"></a>

<h1>Poe API Wrapper <img src="https://psc2.cf2.poecdn.net/favicon.svg" height="35"></h1>

<p><em>A simple API wrapper for Poe.com using Httpx</em></p>
</div>

<p align="center">
<a href="https://pypi.org/project/poe-api-wrapper/"><img src="https://img.shields.io/pypi/v/poe-api-wrapper"></a>
<img alt="Python Version" src="https://img.shields.io/badge/python-3.7+-blue.svg" alt="python">
<img alt="PyPI - Downloads" src="https://pepy.tech/badge/poe-api-wrapper">
<br>
</p>

## 🚀 Table of Contents:
- [🚀 Table of Contents:](#-table-of-contents)
- [✨ Highlights:](#-highlights)
- [🔧 Installation:](#-installation)
- [🦄 Documentation:](#-documentation)
  - [Available Default Bots:](#available-default-bots)
  - [How to get your Token:](#how-to-get-your-token)
  - [Basic Usage:](#basic-usage)
  - [Bots Group Chat (beta):](#bots-group-chat-beta)
  - [Misc:](#misc)
- [🤝 Copyright:](#-copyright)
  - [Copyright Notice:](#copyright-notice)

## ✨ Highlights:
 - Log in with your Quora's token
 - Auto Proxy requests
 - Get Chat Ids & Chat Codes of bot(s)
 - Create new chat thread
 - Send messages
 - Stream bot responses
 - Retry the last message
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
 - Get a user's bots
 - Get available categories
 - Explore 3rd party bots and users
 - Share and import messages
 - Support bots group chat **(beta)**

## 🔧 Installation:
- First, install this library with the following command:
```sh
pip install -U poe-api-wrapper
```
Or you can install a proxy-support version of this library for **Python 3.9+**
```sh
pip install -U poe-api-wrapper[proxy]
```
- You can run an example of this library:
```py
from poe_api_wrapper import PoeExample
token = "TOKEN_HERE"
PoeExample(token).chat_with_bot()
```

## 🦄 Documentation:
### Available Default Bots:
| Display Name           | Model                     | Token Limit | Words | Access Type                                                     |
| ---------------------- | ------------------------- | ----------- | ----- | --------------------------------------------------------------- |
| Assistant              | capybara                  | 4K          | 3K    | ![No Limit](https://img.shields.io/badge/no%20limit-2feb7a)     |
| Claude-instant-100k    | a2_100k                   | 100K        | 75K   | ![Soft Limit](https://img.shields.io/badge/soft%20limit-ffea61) |
| Claude-2-100k          | a2_2                      | 100K        | 75K   | ![Soft Limit](https://img.shields.io/badge/soft%20limit-ffea61) |
| Claude-instant         | a2                        | 9K          | 7K    | ![No Limit](https://img.shields.io/badge/no%20limit-2feb7a)     |
| ChatGPT                | chinchilla                | 4K          | 3K    | ![No Limit](https://img.shields.io/badge/no%20limit-2feb7a)     |
| GPT-3.5-Turbo          | gpt3_5                    | 2k          | 1.5K  | ![No Limit](https://img.shields.io/badge/no%20limit-2feb7a)     |
| GPT-3.5-Turbo-Instruct | chinchilla_instruct       | 2K          | 1.5K  | ![No Limit](https://img.shields.io/badge/no%20limit-2feb7a)     |
| ChatGPT-16k            | agouti                    | 16K         | 12K   | ![Hard Limit](https://img.shields.io/badge/hard%20limit-fc4747) |
| GPT-4                  | beaver                    | 4K          | 3K    | ![Hard Limit](https://img.shields.io/badge/hard%20limit-fc4747) |
| GPT-4-32k              | vizcacha                  | 32K         | 24K   | ![Hard Limit](https://img.shields.io/badge/hard%20limit-fc4747) |
| Google-PaLM            | acouchy                   | 8K          | 6K    | ![No Limit](https://img.shields.io/badge/no%20limit-2feb7a)     |
| Llama-2-7b             | llama_2_7b_chat           | 2K          | 1.5K  | ![No Limit](https://img.shields.io/badge/no%20limit-2feb7a)     |
| Llama-2-13b            | llama_2_13b_chat          | 2K          | 1.5K  | ![No Limit](https://img.shields.io/badge/no%20limit-2feb7a)     |
| Llama-2-70b            | llama_2_70b_chat          | 2K          | 1.5K  | ![No Limit](https://img.shields.io/badge/no%20limit-2feb7a)     |
| Code-Llama-7b          | code_llama_7b_instruct    | 4K          | 3K    | ![No Limit](https://img.shields.io/badge/no%20limit-2feb7a)     |
| Code-Llama-13b         | code_llama_13b_instruct   | 4K          | 3K    | ![No Limit](https://img.shields.io/badge/no%20limit-2feb7a)     |
| Code-Llama-34b         | code_llama_34b_instruct   | 4K          | 3K    | ![No Limit](https://img.shields.io/badge/no%20limit-2feb7a)     |
| Solar-0-70b            | upstage_solar_0_70b_16bit | 2K          | 1.5K  | ![No Limit](https://img.shields.io/badge/no%20limit-2feb7a)     |
>**Important**
> The data on token limits and word counts listed above are approximate and may not be entirely accurate, as the pre-prompt engineering process of poe.com is private and not publicly disclosed.
### How to get your Token:
Sign in at https://www.quora.com/

F12 for Devtools (Right-click + Inspect)
- Chromium: Devtools > Application > Cookies > quora.com
- Firefox: Devtools > Storage > Cookies
- Safari: Devtools > Storage > Cookies

Copy the value of `m-b` cookie

>**Note**
> Make sure you have logged in poe.com using **the same email** which registered on quora.com.
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
- Retrying the last message
```py
for chunk in client.retry_message(chatCode):
    print(chunk['response'], end='', flush=True)
```
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
>**Note**
> It will fetch messages from the latest to the oldest, but the order to be displayed is reversed.
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
categories = client.get_available_categories()
>> Output:
['Official', 'Popular', 'New', 'Mind', 'Funny', 'AI', 'Roleplay', 'Utilities', 'History', 'Sports', 'Travel', 'Music', 'Advice', 'Games', 'Cooking', 'Programming', 'Writing', 'Learning', 'Professional']
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
shareCode = client.share_chat(bot, count=10)
# Share all messages
shareCode = client.share_chat(bot)

# Set up the 2nd Client and import messages from the shareCode
client2 = PoeApi("2nd_TOKEN_HERE")
print(client2.import_chat(bot, shareCode))
>> Output:
{'chatId': 72929127, 'chatCode': '2iw0xcem7a18wy1avd3'}
```
### Bots Group Chat (beta):
- Creating a group chat
```py
bots = [
    {'bot': 'yayayayaeclaude', 'name': 'Yae'}, 
    {'bot': 'gepardL', 'name': 'gepard'}, 
    {'bot': 'SayukiTokihara', 'name': 'Sayuki'}
]

client.create_group(group_name='Hangout', bots=bots) 
```
> Note:
> `bot` arg is the model/displayName.
> `name` arg is the one you'd mention them in group chat.
- Sending messages and Streaming responses in group chat
```py
while True: 
    message = str(input('\n\033[38;5;121mYou : \033[0m'))
    prev_bot = ""
    for chunk in client.send_message_to_group('test', message= message):
        if chunk['bot'] != prev_bot:
            print(f"\n\033[38;5;121m{chunk['bot']} : \033[0m", end='', flush=True)
            prev_bot = chunk['bot']
        print(chunk['response'], end='', flush=True)
    print('\n')
```
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

### Misc:
- How to find chatCode manually?

Here is an example, the chatCode is 2i5bego6rzetfsevv5g

![](https://cdn.discordapp.com/attachments/957946068836950026/1142363043741843506/image.png)

- What are the file types that poe-api-wrapper support?

Currently, this API only supports these file types for adding attachments

| .pdf | .docx | .txt | .py | .js | .ts | .html | .css | .csv | .c | .cs | .cpp |
| - | - | - | - | - | - | - | - | - | - | - | - |
|                                               |

## 🤝 Copyright:
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