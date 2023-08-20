<div align="center">
<a href="https://github.com/snowby666">
<img src="https://socialify.git.ci/snowby666/poe-api-wrapper/image?font=Raleway&forks=1&issues=1&language=1&logo=https://i.ibb.co/JsNwP3B/nobgprofile-3.png&name=1&owner=1&pattern=Charlie%20Brown&pulls=1&stargazers=1&theme=Auto" width="700" height="350"></a>

# Poe API Wrapper <img src="https://psc2.cf2.poecdn.net/favicon.svg" style="height: 35px;">

<p><em>A simple API wrapper for Poe.com using Httpx</em></p>
</div>

<p align="center">
<a href="https://pypi.org/project/poe-api-wrapper/">
<img src="https://img.shields.io/pypi/v/poe-api-wrapper">
</a>
<img src="https://img.shields.io/badge/python-3.7+-blue.svg" alt="python">
<br>
</p>

## Table of Contents:
- [Poe API Wrapper ](#poe-api-wrapper-)
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
 - Get Chat Ids & Chat Codes of bot(s)
 - Create new chat thread
 - Send messages
 - Retrieve responses
 - Delete a chat thread
 - Clear conversation context
 - Purge messages of 1 bot
 - Purge all messages of user
 - Create custom bot
 - Edit custom bot
 - Delete a custom bot
 - Get available bots
 - Support multi-chat threads

## Installation:
- First, install this library with the following command:
```sh
pip3 install poe-api-wrapper
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
```
- Getting Chat Ids & Chat Codes
```py
# Get chat ids of all bots
client.get_chat_history()
# Output:
# ------------------ Chat History ------------------
# Chat ID  |     Chat Code       | Bot Name
# --------------------------------------------------
# 59727831 | 2i58aywsckpnm0v7wyl | chinchilla       
# 59727472 | 2i58bw1nfv0aq7eab6i | chinchilla       
# 59726162 | 2i58ciex72dom7im83r | a2
# 59726106 | 2i58campfdh1yn9us8i | a2
# 59726052 | 2i58d5x8am0untzhaxp | a2
# 59724775 | 2i588127auu1k5ilri9 | capybara
# 59724472 | 2i588hu98sfob7dfifx | capybara
# 59724127 | 2i586nb5jwhhvtr8gk4 | a2
# 59722624 | 2i58qnkisefkly649ml | a2
# 59719138 | 2i58xtl3nftynxnsxxi | capybara
# 59667229 | 2i5e3a7vvpbvt4nrif8 | a2
# 59673297 | 2i5gzkx1x2wicy1tzwr | a2
# 59680790 | 2i5hperhw2irsy351gn | capybara
# --------------------------------------------------

print(client.get_chat_history())
# Output:
# {'chinchilla': [{'chatId': 59727831, 'chatCode': '2i58aywsckpnm0v7wyl', 'id': 'Q2hhdDo1OTcyNzgzMQ=='}, {'chatId': 59727472, 'chatCode': '2i58bw1nfv0aq7eab6i', 'id': 'Q2hhdDo1OTcyNzQ3Mg=='}], 'a2': [{'chatId': 59726162, 'chatCode': '2i58ciex72dom7im83r', 'id': 'Q2hhdDo1OTcyNjE2Mg=='}, {'chatId': 59726106, 'chatCode': '2i58campfdh1yn9us8i', 'id': 'Q2hhdDo1OTcyNjEwNg=='}, {'chatId': 59726052, 'chatCode': '2i58d5x8am0untzhaxp', 'id': 'Q2hhdDo1OTcyNjA1Mg=='}, {'chatId': 59724127, 'chatCode': '2i586nb5jwhhvtr8gk4', 'id': 'Q2hhdDo1OTcyNDEyNw=='}, {'chatId': 59722624, 'chatCode': '2i58qnkisefkly649ml', 'id': 'Q2hhdDo1OTcyMjYyNA=='}, {'chatId': 59667229, 'chatCode': '2i5e3a7vvpbvt4nrif8', 'id': 'Q2hhdDo1OTY2NzIyOQ=='}, {'chatId': 59673297, 'chatCode': '2i5gzkx1x2wicy1tzwr', 'id': 'Q2hhdDo1OTY3MzI5Nw=='}], 'capybara': [{'chatId': 59724775, 'chatCode': '2i588127auu1k5ilri9', 'id': 'Q2hhdDo1OTcyNDc3NQ=='}, {'chatId': 59724472, 'chatCode': '2i588hu98sfob7dfifx', 'id': 'Q2hhdDo1OTcyNDQ3Mg=='}, {'chatId': 59719138, 'chatCode': '2i58xtl3nftynxnsxxi', 'id': 'Q2hhdDo1OTcxOTEzOA=='}, {'chatId': 59680790, 'chatCode': '2i5hperhw2irsy351gn', 'id': 'Q2hhdDo1OTY4MDc5MA=='}]}

# Get chat ids of a bot
print(client.get_chat_history("capybara"))
# Output:
# {'capybara': [{'chatId': 59724775, 'chatCode': '2i588127auu1k5ilri9', 'id': 'Q2hhdDo1OTcyNDc3NQ=='}, {'chatId': 59724472, 'chatCode': '2i588hu98sfob7dfifx', 'id': 'Q2hhdDo1OTcyNDQ3Mg=='}, {'chatId': 59719138, 'chatCode': '2i58xtl3nftynxnsxxi', 'id': 'Q2hhdDo1OTcxOTEzOA=='}, {'chatId': 59680790, 'chatCode': '2i5hperhw2irsy351gn', 'id': 'Q2hhdDo1OTY4MDc5MA=='}]}
```

- Sending messages & Retrieving responses 
```py
bot = "a2"
message = "What is reverse engineering?"

# Create new chat thread
print(client.send_message(bot, message))

# Send message to an existing chat thread
# 1. Using chatCode
print(client.send_message(bot, message, chatCode="2i58ciex72dom7im83r"))
# 2. Using chatId
print(client.send_message(bot, message, chatId="59726162"))
```
> **Note**
> Display names are the same as the codenames for custom bots, you can simply pass the bot's display name into `client.send_message(bot, message)`
- Deleting a chat thread
```py
# Delete 1 chat
# Using chatCode
client.delete_chat(bot, chatCode="2i58ciex72dom7im83r")
# Using chatId
client.delete_chat(bot, chatID="59726162")

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
client.chat_break(bot, chatId="59726162")
```
- Purging messages of 1 bot
  
You can pass the numbers of messages to be deleted into `client.purge_conversation(bot, chatId, chatCode, count)` (the default is 50)
  
```py
# 1. Using chatCode
client.purge_conversation(bot, chatCode="2i58ciex72dom7im83r", 10)
# 2. Using chatId
client.purge_conversation(bot, chatId="59726162", 10)
```
- Purging all messages of user
```py
client.purge_all_conversations()
```
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
# Get a defined numbers of bots (default is 25)
client.get_available_bots(count=10)

# Get all available bots
client.get_available_bots(get_all=True)
```

### Misc:
- How to find chatCode manually?

Here is an example, the chatCode is 2i5bego6rzetfsevv5g

![](https://cdn.discordapp.com/attachments/957946068836950026/1142363043741843506/image.png)


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