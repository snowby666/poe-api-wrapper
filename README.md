# Poe API Wrapper
<br>
A simple API wrapper for Poe.com

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
- Sign in at https://www.quora.com/

F12 for console
Copy the values
Session: Go to Storage → Cookies → m-b. Copy the value of that cookie
### Basic Usage:
- Connect to the Bot
```py
from api import PoeApi
client = PoeApi("TOKEN_HERE", "BOT_NAME")
```
> **Note**
> Display names are the same as the codenames for custom bots, you can simply pass the bot's display name into `client = PoeApi("TOKEN_HERE", "BOT_NAME")`
- Sending messages & Retrieving responses
```py
message = "What is reverse engineering?"
client.send_message(message)
print(client.get_latest_message())
```
- Clear conversation context
```py
client.chat_break()
```
- Purge messages of 1 bot
```py
client.purge_conversation()
```
- Purge all messages of user
```py
client.purge_all_conversations()
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