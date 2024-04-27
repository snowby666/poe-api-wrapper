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
<img alt="PyPI - Downloads" src="https://pepy.tech/badge/poe-api-wrapper"></a>
<br>
</p>

## 📚 Table of Contents
- [Highlights](https://github.com/snowby666/poe-api-wrapper#-highlights)
- [Installation](https://github.com/snowby666/poe-api-wrapper#-installation)
- [Documentation](https://github.com/snowby666/poe-api-wrapper#-documentation)
  - [Available Default Bots](https://github.com/snowby666/poe-api-wrapper#available-default-bots)
  - [How to get your Token](https://github.com/snowby666/poe-api-wrapper#how-to-get-your-token)
  - [Basic Usage](https://github.com/snowby666/poe-api-wrapper#basic-usage)
  - [Bots Group Chat (beta)](https://github.com/snowby666/poe-api-wrapper#bots-group-chat-beta)
  - [Misc](https://github.com/snowby666/poe-api-wrapper#misc)
- [Contributing](https://github.com/snowby666/poe-api-wrapper#-contributing)
  - [Run debug](https://github.com/snowby666/poe-api-wrapper#run-debug)
  - [Ways to contribute](https://github.com/snowby666/poe-api-wrapper#ways-to-contribute)
  - [Contributors](https://github.com/snowby666/poe-api-wrapper#contributors)
- [Copyright](https://github.com/snowby666/poe-api-wrapper#-copyright)
  - [Copyright Notice](https://github.com/snowby666/poe-api-wrapper#copyright-notice)

## ✨ Highlights
<details close>
<summary>Support both <b>Sync</b> and <b>Async</b></summary>
</details>
<details close>
<summary>Authentication</summary><br>
<ul>
<li>Log in with your Quora's token or Poe's token</li>
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
<summary>Knowledge Base Customization <b>(New)</b></summary><br>
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
Or you can install a proxy-support version of this library for **Python 3.9+**
```ShellSession
pip install -U poe-api-wrapper[proxy]
```
You can also use the Async version:
```ShellSession
pip install -U poe-api-wrapper[async]
```
Quick setup for Async Client:
```py
from poe_api_wrapper import AsyncPoeApi
import asyncio
tokens = {
    'b': ..., 
    'lat': ...
}

async def main():
    client = await AsyncPoeApi(cookie=tokens).create()
    message = "Explain quantum computing in simple terms"
    async for chunk in client.send_message(bot="gpt3_5", message=message):
        print(chunk["response"], end='', flush=True)
        
asyncio.run(main())
```
- You can run an example of this library:
```py
from poe_api_wrapper import PoeExample
tokens = {
    'b': ..., 
    'lat': ...
}
PoeExample(cookie=tokens).chat_with_bot()
```
- This library also supports command-line interface:
```ShellSession
poe --b B_TOKEN --lat LAT_TOKEN   
```
> [!TIP]
> Type `poe -h` for more info

<img src="https://i.imgur.com/ScZjzbx.png" width="100%" height="auto">

## 🦄 Documentation
### Available Default Bots
| Display Name           | Model                     | Token Limit | Words | Access Type                                                     |
| ---------------------- | ------------------------- | ----------- | ----- | --------------------------------------------------------------- |
| Assistant              | capybara                  | 4K          | 3K    | ![No Limit](https://img.shields.io/badge/no%20limit-2feb7a)     |
| Claude-3-Opus          | claude_2_1_cedar          | 4K          | 3K    | ![Subscriber](https://img.shields.io/badge/subscriber-fc4747)   |
| Claude-3-Sonnet        | claude_2_1_bamboo         | 4K          | 3K    | ![No Limit](https://img.shields.io/badge/no%20limit-2feb7a)     |
| Claude-3-Opus-200k     | claude_3_opus_200k        | 200K        | 150K  | ![Subscriber](https://img.shields.io/badge/subscriber-fc4747)   |
| Claude-3-Sonnet-200k   | claude_3_sonnet_200k      | 200K        | 150K  | ![Subscriber](https://img.shields.io/badge/subscriber-fc4747)   |
| Claude-instant-100k    | a2_100k                   | 100K        | 75K   | ![No Limit](https://img.shields.io/badge/no%20limit-2feb7a)     |
| Claude-2               | claude_2_short            | 4K          | 3K    | ![Subscriber](https://img.shields.io/badge/subscriber-fc4747)   |
| Claude-2-100k          | a2_2                      | 100K        | 75K   | ![Subscriber](https://img.shields.io/badge/subscriber-fc4747)   |
| Claude-instant         | a2                        | 9K          | 7K    | ![No Limit](https://img.shields.io/badge/no%20limit-2feb7a)     |
| ChatGPT                | chinchilla                | 4K          | 3K    | ![No Limit](https://img.shields.io/badge/no%20limit-2feb7a)     |
| GPT-3.5-Turbo          | gpt3_5                    | 2k          | 1.5K  | ![No Limit](https://img.shields.io/badge/no%20limit-2feb7a)     |
| GPT-3.5-Turbo-Instruct | chinchilla_instruct       | 2K          | 1.5K  | ![No Limit](https://img.shields.io/badge/no%20limit-2feb7a)     |
| ChatGPT-16k            | agouti                    | 16K         | 12K   | ![Subscriber](https://img.shields.io/badge/subscriber-fc4747)   |
| GPT-4                  | beaver                    | 4K          | 3K    | ![Subscriber](https://img.shields.io/badge/subscriber-fc4747)   |
| GPT-4-128k             | vizcacha                  | 128K        | 96K   | ![Subscriber](https://img.shields.io/badge/subscriber-fc4747)   |
| Google-PaLM            | acouchy                   | 8K          | 6K    | ![No Limit](https://img.shields.io/badge/no%20limit-2feb7a)     |
| Llama-2-7b             | llama_2_7b_chat           | 2K          | 1.5K  | ![No Limit](https://img.shields.io/badge/no%20limit-2feb7a)     |
| Llama-2-13b            | llama_2_13b_chat          | 2K          | 1.5K  | ![No Limit](https://img.shields.io/badge/no%20limit-2feb7a)     |
| Llama-2-70b            | llama_2_70b_chat          | 2K          | 1.5K  | ![No Limit](https://img.shields.io/badge/no%20limit-2feb7a)     |
| Code-Llama-7b          | code_llama_7b_instruct    | 4K          | 3K    | ![No Limit](https://img.shields.io/badge/no%20limit-2feb7a)     |
| Code-Llama-13b         | code_llama_13b_instruct   | 4K          | 3K    | ![No Limit](https://img.shields.io/badge/no%20limit-2feb7a)     |
| Code-Llama-34b         | code_llama_34b_instruct   | 4K          | 3K    | ![No Limit](https://img.shields.io/badge/no%20limit-2feb7a)     |
| Solar-Mini             | upstage_solar_0_70b_16bit | 2K          | 1.5K  | ![No Limit](https://img.shields.io/badge/no%20limit-2feb7a)     |
> [!IMPORTANT]  
> The data on token limits and word counts listed above are approximate and may not be entirely accurate, as the pre-prompt engineering process of poe.com is private and not publicly disclosed.

### How to get your Token
Poe API Wrapper accepts both quora.com and poe.com tokens. Pick one that works best for you.
#### Quora Tokens
Sign in at https://www.quora.com/

F12 for Devtools (Right-click + Inspect)
- Chromium: Devtools > Application > Cookies > quora.com
- Firefox: Devtools > Storage > Cookies
- Safari: Devtools > Storage > Cookies

Copy the values of `m-b` and `m-lat` cookies

#### Poe Tokens
Sign in at https://poe.com/

F12 for Devtools (Right-click + Inspect)
- Chromium: Devtools > Application > Cookies > poe.com
- Firefox: Devtools > Storage > Cookies
- Safari: Devtools > Storage > Cookies

Copy the values of `p-b` and `p-lat` cookies

> [!NOTE]
> Make sure you have logged in poe.com using **the same email** which registered on quora.com.

### Basic Usage
- Connecting to the API
```py
# Using poe.com tokens
tokens = {
    'b': 'p-b token here',
    'lat': 'p-lat token here'
}
# Using quora.com tokens
tokens = {
    'b': 'm-b token here',
    'lat': 'm-lat token here'
}

from poe_api_wrapper import PoeApi
client = PoeApi(cookie=tokens)

# Using Client with auto_proxy (default is False)
client = PoeApi(cookie=tokens, auto_proxy=True)

# Passing proxies manually
proxy_context = [
    {"https":X1, "http":X1},
    {"https":X2, "http":X2},
    ...
]

client = PoeApi(cookie=tokens, proxy=proxy_context) 
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
['chinchilla', 'mixtral8x7bchat', 'playgroundv25', 'stablediffusionxl', 'dalle3', 'a2', 'claude_2_short', 'gemini_pro', 'a2_2', 'a2_100k', 'beaver', 'llama_2_70b_chat', 'mythomaxl213b', 'claude_2_1_bamboo', 'claude_2_1_cedar', 'claude_3_haiku', 'claude_3_haiku_200k']
```
- Creating a new Bot
```py
client.create_bot("BOT_NAME", "PROMPT_HERE", base_model="a2")

# Using knowledge bases (you can use source_ids from uploaded knowledge bases for your custom bot)
client.create_bot("BOT_NAME", "PROMPT_HERE", base_model="a2", knowledgeSourceIds=source_ids, shouldCiteSources=True)
```
- Editing a Bot
```py
client.edit_bot("(NEW)BOT_NAME", "PROMPT_HERE", base_model='chinchilla')

# Adding knowledge bases 
client.edit_bot("(NEW)BOT_NAME", "PROMPT_HERE", base_model='chinchilla', knowledgeSourceIdsToAdd=source_ids, shouldCiteSources=True)

# Removing knowledge bases
client.edit_bot("(NEW)BOT_NAME", "PROMPT_HERE", base_model='chinchilla', knowledgeSourceIdsToRemove=source_ids, shouldCiteSources=True)
```
> [!TIP]
> You can also use both `knowledgeSourceIdsToAdd` and `knowledgeSourceIdsToRemove` at the same time.
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
### Bots Group Chat (beta)
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

### Misc
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
