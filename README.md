# Poe API Wrapper
A simple API wrapper for Poe.com using Httpx
## Table of Contents:
- [Poe API Wrapper](#poe-api-wrapper)
  - [Table of Contents:](#table-of-contents)
  - [Highlights:](#highlights)
  - [Installation:](#installation)
  - [Documentation:](#documentation)
    - [Available Bots:](#available-bots)
    - [How to get your Token:](#how-to-get-your-token)
    - [Basic Usage:](#basic-usage)
  - [Copyright:](#copyright)
    - [Copyright Notice:](#copyright-notice)

## Highlights:
 - Log in with your Quora's token
 - Send messages
 - Retrieve responses
 - Clear conversation context
 - Purge messages of 1 bot
 - Purge all messages of user
 - Create custom bot
 - Edit custom bot
 - Get chat ids of all bot (support multi threads of each bot)

## Installation:
- First, clone the repository and enter the folder:
```sh
git clone https://github.com/snowby666/poe-api-wrapper.git
cd poe-api-wrapper
```
- Install the required packages:
```sh
pip install -r requirements.txt
```
- Run the example.py:
```sh
python example.py 
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
from api import PoeApi
client = PoeApi("TOKEN_HERE")
```
- Sending messages & Retrieving responses
```py
bot = "a2"
message = "What is reverse engineering?"
client.send_message(bot, message)
print(client.get_latest_message(bot))
```
> **Note**
> Display names are the same as the codenames for custom bots, you can simply pass the bot's display name into `client.send_message(bot, message)`
- Clear conversation context
```py
client.chat_break(bot)
```
- Purging messages of 1 bot
  
You can pass the numbers of messages to be deleted into `client.purge_conversation(bot, count)` (the default is 50)
  
```py
client.purge_conversation(bot, 10)
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
client.edit_bot("(NEW)BOT_NAME", "PROMPT_HERE", "BOT_ID", base_model='chinchilla')
```
- Getting chat ids
```py
# Get chat ids of all bots
client.get_chat_history()

# Output | {'a2': [58232105], 'capybara': [58142663, 58171742]}
# ------------------ Chat History ------------------
# Chat ID | Bot Name
# --------------------------------------------------
# 58232105 | a2
# 58142663 | capybara
# 58171742 | capybara
# --------------------------------------------------

# Get chat ids of a bot
client.get_chat_history("capybara")

# Output | {'capybara': [58142663, 58171742]}
# 1. 58142663
# 2. 58171742
```

## Copyright:
This program is licensed under the [GNU GPL v3](https://github.com/snowby666/poe-api-wrapper/blob/main/LICENSE). All code has been written by me, [snowby666](https://github.com/snowby666).

### Copyright Notice:
```
snowby666/poe-api-wrapper: a simple API wrapper for poe.com
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