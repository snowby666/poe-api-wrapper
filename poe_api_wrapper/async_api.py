try:
    from httpx import AsyncClient, ConnectError, ReadTimeout
    ASYNC = True
except ImportError:
    ASYNC = False
import asyncio, json, queue, random, ssl, threading, websocket, string, secrets, os, hashlib
from time import time
from typing import  AsyncIterator
from loguru import logger
from requests_toolbelt import MultipartEncoder

# Allow multi-threading for asyncio
import nest_asyncio
nest_asyncio.apply()

from .utils import (
                    BASE_URL,
                    HEADERS,
                    SubscriptionsMutation,
                    BOTS_LIST, 
                    REVERSE_BOTS_LIST, 
                    bot_map, 
                    generate_nonce, 
                    generate_file
                    )
from .queries import generate_payload
from .proxies import PROXY
if PROXY:
    from .proxies import fetch_proxy

"""
This API is modified and maintained by @snowby666
Credit to @ading2210 for the GraphQL queries
"""


class AsyncPoeApi:
    BASE_URL = BASE_URL
    HEADERS = HEADERS
    def __init__(self, tokens: dict={}, proxy: list=[], auto_proxy: bool=False):
        self.client = None
        if not ASYNC:
            raise ImportError("Please install Async version using 'pip install poe-api-wrapper[async]'")
        if not {'p-b', 'p-lat', 'formkey'}.issubset(tokens):
            raise ValueError("Please provide valid p-b, p-lat, and formkey")
        
        self.proxy = proxy
        self.auto_proxy = auto_proxy
        self.tokens = tokens
        self.formkey = None
        self.ws_connecting = False
        self.ws_connected = False
        self.ws_error = False
        self.active_messages = {}
        self.message_queues = {}
        self.current_thread = {}
        self.retry_attempts = 3
        self.message_generating = True
        self.ws_refresh = 3
        self.groups = {}
        self.formkey = self.tokens['formkey']
        
        self.client = AsyncClient(headers=self.HEADERS, timeout=60, http2=True)
        self.client.cookies.update({
                                'p-b': self.tokens['p-b'], 
                                'p-lat': self.tokens['p-lat']
                                })
        
          
        if { '__cf_bm', 'cf_clearance'}.issubset(tokens):
            self.client.cookies.update({
                '__cf_bm': tokens['__cf_bm'], 
                'cf_clearance': tokens['cf_clearance']
            })
            
        self.client.headers.update({
            'Poe-Formkey': self.formkey,
        })
        
    async def create(self):
        if self.proxy != [] or self.auto_proxy == True:
            await self.select_proxy(self.proxy, auto_proxy=self.auto_proxy)
        elif self.proxy == [] and self.auto_proxy == False:
            await self.connect_ws() 
        else:
            raise ValueError("Please provide a valid proxy list or set auto_proxy to False")
        
        logger.info("Async instance created")

        return self
        
    def __del__(self):
        if self.client:
            asyncio.get_event_loop().run_until_complete(self.client.aclose())
        
    async def select_proxy(self, proxy: list, auto_proxy: bool=False):
        if proxy == [] and auto_proxy == True and PROXY == True:
            proxies = fetch_proxy()
        elif proxy != [] and auto_proxy == False:
            proxies = proxy
        else:
            raise ValueError("Please provide a valid proxy list or set auto_proxy to False")
        for p in range(len(proxies)):
            try:
                self.client.proxies = p
                await self.connect_ws()
                logger.info(f"Connection established with {proxies[p]}")
                break
            except:
                logger.info(f"Connection failed with {proxies[p]}. Trying {p+1}/{len(proxies)} ...")
                await asyncio.sleep(1)

    async def send_request(self, path: str, query_name: str="", variables: dict={}, file_form: list=[], knowledge: bool=False, ratelimit: int = 0):
        if ratelimit > 0:
            logger.warning(f"Wating for {ratelimit} seconds to avoid rate limit")
            asyncio.sleep(random.randint(2, 3))
        status_code = 0
        
        try:
            payload = generate_payload(query_name, variables)
            base_string = payload + self.formkey + "4LxgHM6KpFqokX0Ox"
            if file_form == []:
                headers = {'Content-Type': 'application/json'}
            else:
                fields = {'queryInfo': payload}
                if not knowledge:
                    for i in range(len(file_form)):
                        fields[f'file{i}'] = file_form[i]
                else:
                    fields['file'] = file_form[0]
                payload = MultipartEncoder(
                    fields=fields
                    )
                headers = {'Content-Type': payload.content_type}
                payload = payload.to_string()
            
            headers.update({
                "poe-tag-id": hashlib.md5(base_string.encode()).hexdigest(),
            })
            response = await self.client.post(f'{self.BASE_URL}/api/{path}', data=payload, headers=headers, follow_redirects=True, timeout=30)
            
            status_code = response.status_code
            json_data = json.loads(response.text)

            if (
                "success" in json_data.keys()
                and not json_data["success"]
                or (json_data and json_data["data"] is None)
            ):
                err_msg: str = json_data["errors"][0]["message"]
                if err_msg == "Server Error":
                    raise RuntimeError(f"Server Error. Raw response data: {json_data}")
                else:
                    logger.error(response.status_code)
                    logger.error(response.text)
                    raise Exception(response.text)
                
            if status_code == 200:
                for file in file_form:
                    try:
                        if hasattr(file[1], 'closed') and not file[1].closed:
                            file[1].close()
                    except IOError as e:
                        logger.warning(f"Failed to close file: {file[0]}. Reason: {e}")
                return json_data
            
        except Exception as e:
            if isinstance(e, ReadTimeout):
                if query_name == "SendMessageMutation":
                    logger.error(f"Failed to send message {variables['query']} due to ReadTimeout")
                    logger.info(f"Attempting to retry message {variables['query']} 3 times...")
                else:
                    logger.error(f"Automatic retrying request {query_name} due to ReadTimeout")
                    return self.send_request(path, query_name, variables, file_form)

            if (
                isinstance(e, ConnectError) or 500 <= status_code < 600
            ) and ratelimit < 2:
                return self.send_request(path, query_name, variables, file_form, ratelimit=ratelimit + 1)

            error_code = f"status_code:{status_code}, " if status_code else ""
            raise Exception(
                f"Sending request {query_name} failed. {error_code} Error log: {repr(e)}"
            )
    
    async def get_channel_settings(self):
        response = await self.client.get(f'{self.BASE_URL}/api/settings', headers=self.HEADERS, follow_redirects=True, timeout=30)
        response_json = response.json()
        self.ws_domain = f"tch{random.randint(1, int(1e6))}"[:11]
        self.tchannel_data = response_json["tchannelData"]
        self.client.headers["Poe-Tchannel"] = self.tchannel_data["channel"]
        self.channel_url = f'ws://{self.ws_domain}.tch.{self.tchannel_data["baseHost"]}/up/{self.tchannel_data["boxName"]}/updates?min_seq={self.tchannel_data["minSeq"]}&channel={self.tchannel_data["channel"]}&hash={self.tchannel_data["channelHash"]}'
        await self.subscribe()
    
    async def subscribe(self):
        response_json = await self.send_request('gql_POST', "SubscriptionsMutation", SubscriptionsMutation)
        if response_json['data'] == None and response_json["errors"]:
            raise RuntimeError(f'Failed to subscribe by sending SubscriptionsMutation. Raw response data: {response_json}')
            
    def ws_run_thread(self):
        if not self.ws.sock:
            kwargs = {"sslopt": {"cert_reqs": ssl.CERT_NONE}}
            self.ws.run_forever(**kwargs)
             
    async def connect_ws(self, timeout=20):
         
        if self.ws_connected:
            return

        if self.ws_connecting:
            while not self.ws_connected:
                await asyncio.sleep(0.01)
            return

        self.ws_connecting = True
        self.ws_connected = False
        self.ws_refresh = 3
        
        while True:
            self.ws_refresh -= 1
            if self.ws_refresh == 0:
                self.ws_refresh = 3
                raise RuntimeError("Rate limit exceeded for sending requests to poe.com. Please try again later.")
            try:
                await self.get_channel_settings()
                break
            except Exception as e:
                logger.error(f"Failed to get channel settings. Reason: {e}")
                await asyncio.sleep(1)
                continue

        self.ws = await asyncio.get_event_loop().run_in_executor(
            None,
            lambda: websocket.WebSocketApp(self.channel_url, 
                                           header={
                                                "Origin": f"{self.BASE_URL}",
                                                "Pragma": "no-cache",
                                                "Cache-Control": "no-cache",
                                            },
                                            on_message=lambda ws, msg: self.on_message(ws, msg), 
                                            on_open=lambda ws: self.on_ws_connect(ws), 
                                            on_error=lambda ws, error: self.on_ws_error(ws, error), 
                                            on_close=lambda ws, close_status_code, close_message: self.on_ws_close(ws, close_status_code, close_message))
        )

        t = threading.Thread(target=self.ws_run_thread, daemon=True)
        t.start()

        timer = 0
        while not self.ws_connected:
            await asyncio.sleep(0.01)
            timer += 0.01
            if timer > timeout:
                self.ws_connecting = False
                self.ws_connected = False
                self.ws_error = True
                self.ws.close()
                raise RuntimeError("Timed out waiting for websocket to connect.")

    def disconnect_ws(self):
        self.ws_connecting = False
        self.ws_connected = False
        if self.ws:
            self.ws.close()

    def on_ws_connect(self, ws):
        self.ws_connecting = False
        self.ws_connected = True

    def on_ws_close(self, ws, close_status_code, close_message):
        self.ws_connecting = False
        self.ws_connected = False
        if self.ws_error:
            logger.warning("Connection to remote host was lost. Reconnecting...")
            self.ws_error = False
            asyncio.get_event_loop().run_until_complete(self.connect_ws())

    def on_ws_error(self, ws, error):
        self.ws_connecting = False
        self.ws_connected = False
        self.ws_error = True

    def on_message(self, ws, msg):
        try:
            ws_data = json.loads(msg)

            if "error" in ws_data.keys() and ws_data["error"] == "missed_messages":
                self.disconnect_ws()
                asyncio.get_event_loop().run_until_complete(self.connect_ws())
                return
            
            if not "messages" in ws_data:
                return
            
            for data in ws_data["messages"]:
                data = json.loads(data)
                message_type = data.get("message_type")
                if message_type == "refetchChannel":
                    self.disconnect_ws()
                    asyncio.get_event_loop().run_until_complete(self.connect_ws())
                    return

                payload = data.get("payload", {})

                if payload.get("subscription_name") not in [
                    "messageAdded",
                    "messageCancelled",
                ]:
                    continue

                data = (payload.get("data", {})).get("messageAdded", {})
                
                if (
                    not data
                    or data["suggestedReplies"]
                    or data.get("author") == "chat_break"
                ):
                    continue

                copied_dict = self.active_messages.copy()
                for key, value in copied_dict.items():
                    if value == data["messageId"] and key in self.message_queues:
                        self.message_queues[key].put(data)
                        return

                    elif key != "pending" and value == None and data["state"] != "complete":
                        self.active_messages[key] = data["messageId"]
                        self.message_queues[key].put(data)
                        return
                    
        except Exception:
            logger.exception(f"Failed to parse message: {msg}")
            self.disconnect_ws()
            asyncio.get_event_loop().run_until_complete(self.connect_ws())
            
    async def get_remaining_points(self):
        response_json = await self.send_request('gql_POST', 'SettingsPageQuery', {})
        return response_json["data"]["viewer"]["messagePointInfo"]
    
    async def get_available_bots(self, count: int=25, get_all: bool=False):
        self.bots = {}
        if not (get_all or count):
            raise TypeError("Please provide at least one of the following parameters: get_all=<bool>, count=<int>")
        response = await self.send_request('gql_POST',"AvailableBotsSelectorModalPaginationQuery", {}) 
        bots = [
            each["node"]
            for each in response["data"]["viewer"]["availableBotsConnection"]["edges"]
            if each["node"]["deletionState"] == "not_deleted"
        ]
        cursor = response["data"]["viewer"]["availableBotsConnection"]["pageInfo"]["endCursor"]
        if len(bots) >= count and not get_all:
            self.bots.update({bot["handle"]: {"bot": bot} for bot in bots})
            return self.bots
        while len(bots) < count or get_all:
            response = await self.send_request("gql_POST", "AvailableBotsSelectorModalPaginationQuery", {"cursor": cursor})
            new_bots = [
                each["node"]
                for each in response["data"]["viewer"]["availableBotsConnection"]["edges"]
                if each["node"]["deletionState"] == "not_deleted"
            ]
            cursor = response["data"]["viewer"]["availableBotsConnection"]["pageInfo"]["endCursor"]
            bots += new_bots
            if len(new_bots) == 0:
                if not get_all:
                    logger.warning(f"Only {len(bots)} bots found on this account")
                else:
                    logger.info(f"Total {len(bots)} bots found on this account")
                self.bots.update({bot["handle"]: {"bot": bot} for bot in bots})
                return self.bots
            
        logger.info("Succeed to get available bots")
        self.bots.update({bot["handle"]: {"bot": bot} for bot in bots})
        return self.bots
    
    async def get_chat_history(self, bot: str=None, count: int=None, interval: int=50, cursor: str=None):

        chat_bots = {'data': {}, 'cursor': None}
        
        if count != None:
            interval = count
        
        if bot == None:
            response_json = await self.send_request('gql_POST', 'ChatHistoryListPaginationQuery', {'count': interval, 'cursor': cursor})
            if response_json['data']['chats']['pageInfo']['hasNextPage']:
                cursor = response_json['data']['chats']['pageInfo']['endCursor']
                chat_bots['cursor'] = cursor  
            else:
                chat_bots['cursor'] = None
            edges = response_json['data']['chats']['edges']
           
            for edge in edges:
                chat = edge['node']
                model = bot_map(chat["defaultBotObject"]["displayName"])

                if model in chat_bots['data']:
                    chat_bots['data'][model].append({"chatId": chat["chatId"],"chatCode": chat["chatCode"], "id": chat["id"], "title": chat["title"]})
                else:
                    chat_bots['data'][model] = [{"chatId": chat["chatId"], "chatCode": chat["chatCode"], "id": chat["id"], "title": chat["title"]}]
            # Fetch more chats
            if count == None:
                while response_json['data']['chats']['pageInfo']['hasNextPage']:
                    response_json = await self.send_request('gql_POST', 'ChatHistoryListPaginationQuery', {'count': interval, 'cursor': cursor})
                    edges = response_json['data']['chats']['edges']
                    for edge in edges:
                        chat = edge['node']
                        model = bot_map(chat["defaultBotObject"]["displayName"])
                   
                        if model in chat_bots['data']:
                            chat_bots['data'][model].append({"chatId": chat["chatId"],"chatCode": chat["chatCode"], "id": chat["id"], "title": chat["title"]})
                        else:
                            chat_bots['data'][model] = [{"chatId": chat["chatId"], "chatCode": chat["chatCode"], "id": chat["id"], "title": chat["title"]}]    
                    cursor = response_json['data']['chats']['pageInfo']['endCursor']  
                    chat_bots['cursor'] = cursor      
                if not response_json['data']['chats']['pageInfo']['hasNextPage']:
                    chat_bots['cursor'] = None  
        else:
            model = bot.lower().replace(' ', '')
            handle = model
            for key, value in BOTS_LIST.items():
                if model == value:
                    handle = key
                    break
            response_json = await self.send_request('gql_POST', 'ChatHistoryFilteredListPaginationQuery', {'count': interval, 'handle': handle, 'cursor': cursor})
            if response_json['data'] == None and response_json["errors"]:
                raise ValueError(
                    f"Bot {bot} not found. Make sure the bot exists before creating new chat."
                )
            if response_json['data']['filteredChats']['pageInfo']['hasNextPage']:
                cursor = response_json['data']['filteredChats']['pageInfo']['endCursor']
                chat_bots['cursor'] = cursor  
            else:
                chat_bots['cursor'] = None
            edges = response_json['data']['filteredChats']['edges']
            for edge in edges:
                chat = edge['node']
                try:
                    if model in chat_bots['data']:
                        chat_bots['data'][model].append({"chatId": chat["chatId"],"chatCode": chat["chatCode"], "id": chat["id"], "title": chat["title"]})
                    else:
                        chat_bots['data'][model] = [{"chatId": chat["chatId"], "chatCode": chat["chatCode"], "id": chat["id"], "title": chat["title"]}]
                except Exception as e:
                    logger.debug(str(e))
                    pass 
            # Fetch more chats
            if count == None:
                while response_json['data']['filteredChats']['pageInfo']['hasNextPage']:
                    response_json = await self.send_request('gql_POST', 'ChatHistoryFilteredListPaginationQuery', {'count': interval, 'handle': handle, 'cursor': cursor})
                    edges = response_json['data']['filteredChats']['edges']
                    for edge in edges:
                        chat = edge['node']
                        try:
                            if model in chat_bots['data']:
                                chat_bots['data'][model].append({"chatId": chat["chatId"],"chatCode": chat["chatCode"], "id": chat["id"], "title": chat["title"]})
                            else:
                                chat_bots['data'][model] = [{"chatId": chat["chatId"], "chatCode": chat["chatCode"], "id": chat["id"], "title": chat["title"]}]
                        except Exception as e:
                            logger.debug(str(e))
                            pass     
                    cursor = response_json['data']['filteredChats']['pageInfo']['endCursor']  
                    chat_bots['cursor'] = cursor  
                if not response_json['data']['filteredChats']['pageInfo']['hasNextPage']:
                    chat_bots['cursor'] = None
        return chat_bots
    
    async def get_threadData(self, bot: str="", chatCode: str=None, chatId: int=None):
        id = None
        title = None
        if bot not in self.current_thread:
            self.current_thread[bot] = await self.get_chat_history(bot=bot)['data'][bot]
        elif len(self.current_thread[bot]) <= 1:
            self.current_thread[bot] = await self.get_chat_history(bot=bot)['data'][bot]
        if chatCode != None:
            for chat in self.current_thread[bot]:
                if chat['chatCode'] == chatCode:
                    chatId = chat['chatId']
                    id = chat['id']
                    title = chat['title']
                    break
        elif chatId != None:
            for chat in self.current_thread[bot]:
                if chat['chatId'] == chatId:
                    chatCode = chat['chatCode']
                    id = chat['id']
                    title = chat['title']
                    break
        return {'chatCode': chatCode, 'chatId': chatId, 'id': id, 'title': title}
    
    async def get_botInfo(self, handle: str):
        if handle in REVERSE_BOTS_LIST:
            handle = REVERSE_BOTS_LIST[handle]
        else:
            handle = handle.lower().replace(' ', '')
        response_json = await self.send_request('gql_POST', 'HandleBotLandingPageQuery', {'botHandle': handle})
        if response_json['data'] == None and response_json["errors"]:
            raise ValueError(
                f"Bot {handle} not found. Make sure the bot exists before creating new chat."
            )
        botData = response_json['data']['bot']
        data = {
                'handle': botData['handle'],
                'model':botData['model'],
                'supportsFileUpload': botData['supportsFileUpload'], 
                'messageTimeoutSecs': botData['messageTimeoutSecs'], 
                'displayMessagePointPrice': botData['messagePointLimit']['displayMessagePointPrice'], 
                'numRemainingMessages': botData['messagePointLimit']['numRemainingMessages'],
                'viewerIsCreator': botData['viewerIsCreator'],
                'id': botData['id'],
                }
        return data
    
    async def get_suggestions(self, queue, response, chatId: int, title: str,chatCode: str=None, timeout: int=10):
        variables = {'chatCode': chatCode}
        state = 'incomplete'
        suggestions = []
        start_time = time()
        while True:
            elapsed_time = time() - start_time
            if elapsed_time >= timeout:
                break
            await asyncio.sleep(0.5)
            response_json = await self.send_request('gql_POST', 'ChatPageQuery', variables)
            hasSuggestedReplies = response_json['data']['chatOfCode']['defaultBotObject']['mayHaveSuggestedReplies']
            latest_message = response_json['data']['chatOfCode']['lastMessage']
            if hasSuggestedReplies and latest_message:
                suggestions = latest_message['suggestedReplies']
                state = latest_message['state']
                if state == 'complete' and suggestions:
                    break
                if state == 'error_user_message_too_long':
                    break
            else:
                break
        queue.put({'text': response["text"], 'response':'', 'suggestedReplies': suggestions, 'state': state, 'chatCode': chatCode, 'chatId': chatId, 'title': title})
        
    async def retry_message(self, chatCode: str, suggest_replies: bool=False, timeout: int=20):
        self.retry_attempts = 3
        timer = 0
        while None in self.active_messages.values():
            await asyncio.sleep(0.01)
            timer += 0.01
            if timer > timeout:
                raise RuntimeError("Timed out waiting for other messages to send.")
        self.active_messages["pending"] = None
        
        while self.ws_error:
            await asyncio.sleep(0.01)
        await self.connect_ws()
        
        variables = {"chatCode": chatCode}
        response_json = await self.send_request('gql_POST', 'ChatPageQuery', variables)
        if response_json['data'] == None and response_json["errors"]:
            raise RuntimeError(f"An unknown error occurred. Raw response data: {response_json}")
        elif response_json['data']['viewer']['enableRemixButton'] != True:
            raise RuntimeError(f"Retry button is not enabled. Raw response data: {response_json}")
        edges = response_json['data']['chatOfCode']['messagesConnection']['edges']
        edges.reverse()
        
        chatId = response_json['data']['chatOfCode']['chatId']
        title = response_json['data']['chatOfCode']['title']
        msgPrice = response_json['data']['chatOfCode']['defaultBotObject']['messagePointLimit']['displayMessagePointPrice']
        last_message = edges[0]['node']
        
        if last_message['author'] == 'human':
            raise RuntimeError(f"Last message is not from bot. Raw response data: {response_json}")
        
        bot = bot_map(last_message['author'])
        
        status = last_message['state']
        if status == 'error_user_message_too_long':
            raise RuntimeError(f"Last message is too long. Raw response data: {response_json}")
        while status != 'complete':
            await asyncio.sleep(0.5)
            response_json = await self.send_request('gql_POST', 'ChatPageQuery', variables)
            if response_json['data'] == None and response_json["errors"]:
                raise RuntimeError(f"An unknown error occurred. Raw response data: {response_json}")
            edges = response_json['data']['chatOfCode']['messagesConnection']['edges']
            edges.reverse()
            last_message = edges[0]['node']
            status = last_message['state']
            if status == 'error_user_message_too_long':
                raise RuntimeError(f"Last message is too long. Raw response data: {response_json}")
        
        bot_message_id = last_message['messageId']
        human_message_id = edges[1]['node']['messageId']
        
        response_json = await self.send_request('gql_POST', 'RegenerateMessageMutation', {'messageId': bot_message_id, 'messagePointsDisplayPrice': msgPrice})
        if response_json['data'] == None and response_json["errors"]:
            logger.error(f"Failed to retry message {bot_message_id} of Thread {chatCode}. Raw response data: {response_json}")
        else:
            logger.info(f"Message {bot_message_id} of Thread {chatCode} has been retried.")
            
        self.message_generating = True
        self.active_messages[human_message_id] = None
        self.message_queues[human_message_id] = queue.Queue()

        last_text = ""
        message_id = None
        
        stateChange = False
        
        while True:
            try:
                response = self.message_queues[human_message_id].get(timeout=timeout)
            except queue.Empty:
                try:
                    if self.retry_attempts > 0:
                        self.retry_attempts -= 1
                        logger.warning(f"Retrying request {3-self.retry_attempts}/3 times...")
                    else:
                        self.retry_attempts = 3
                        del self.active_messages[human_message_id]
                        del self.message_queues[human_message_id]
                        raise RuntimeError("Timed out waiting for response.")
                    await self.connect_ws()
                    continue
                except Exception as e:
                    raise e
            
            response["chatCode"] = chatCode
            response["chatId"] = chatId
            response["title"] = title
            response["msgPrice"] = msgPrice

            if response["state"] == "error_user_message_too_long":
                response["response"]  = 'Message too long. Please try again!'
                yield response
                break
            
            if (response['author'] == 'pacarana' and response['text'].strip() == last_text.strip()):
                response["response"] = ''
            elif response['author'] == 'pacarana' and (last_text == '' or bot == 'web-search'):
                response["response"] = f'{response["text"]}\n'
            else:
                if stateChange == False:
                    response["response"] = response["text"]
                    stateChange = True
                else:
                    response["response"] = response["text"][len(last_text):]
            
            yield response
            
            if response["state"] == "complete" or not self.message_generating:
                if last_text and response["messageId"] == message_id:
                    break
                else:
                    continue
            
            last_text = response["text"]
            message_id = response["messageId"]
            
        async def recv_post_thread():
            bot_message_id = self.active_messages[human_message_id]
            await asyncio.sleep(2.5)
            await self.send_request("receive_POST", "recv", {
                "bot_name": bot,
                "time_to_first_typing_indicator": 300,
                "time_to_first_subscription_response": 600,
                "time_to_full_bot_response": 1100,
                "full_response_length": len(last_text) + 1,
                "full_response_word_count": len(last_text.split(" ")) + 1,
                "human_message_id": human_message_id,
                "bot_message_id": bot_message_id,
                "chat_id": chatId,
                "bot_response_status": "success",
            })
            await asyncio.sleep(0.5)
        
        if response["state"] != "error_user_message_too_long": 
            await recv_post_thread()
            
            if suggest_replies:
                self.suggestions_queue = queue.Queue()
                await self.get_suggestions(self.suggestions_queue, response, chatId, title, chatCode, 10)
                try:
                    suggestions = self.suggestions_queue.get(timeout=10)
                    yield suggestions
                except queue.Empty:
                    yield {'text': response["text"], 'response':'', 'suggestedReplies': [], 'state': None, 'chatCode': chatCode, 'chatId': chatId, 'title': title}
                del self.suggestions_queue
        
        del self.active_messages[human_message_id]
        del self.message_queues[human_message_id]
        self.retry_attempts = 3
        
    async def send_message(self, bot: str, message: str, chatId: int=None, chatCode: str=None, msgPrice: int=20, file_path: list=[], suggest_replies: bool=False, timeout: int=10) -> AsyncIterator[dict]:
        self.retry_attempts = 3
        timer = 0
        while None in self.active_messages.values():
            await asyncio.sleep(0.01)
            timer += 0.01
            if timer > timeout:
                raise RuntimeError("Timed out waiting for other messages to send.")
        self.active_messages["pending"] = None
        
        while self.ws_error:
            await asyncio.sleep(0.01)
        await self.connect_ws()
        
        bot = bot_map(bot)
        attachments = []
        
        if file_path == []:
            apiPath = 'gql_POST'
            file_form = []
        else:
            apiPath = 'gql_upload_POST'
            file_form, file_size = generate_file(file_path, self.client.proxies)
            if file_size > 50000000:
                raise RuntimeError("File size too large. Please try again with a smaller file.")
            for i in range(len(file_form)):
                attachments.append(f'file{i}')
        
        if (chatId == None and chatCode == None):
            try:
                variables = {
                                "chatId": None, 
                                "bot": bot,
                                "query":message, 
                                "shouldFetchChat": True, 
                                "source":{"sourceType":"chat_input","chatInputMetadata":{"useVoiceRecord":False,}}, 
                                "clientNonce": generate_nonce(),
                                "sdid":"","attachments":attachments, 
                                "existingMessageAttachmentsIds":[],
                                "messagePointsDisplayPrice": msgPrice
                            }
                message_data = await self.send_request(apiPath, 'SendMessageMutation', variables, file_form)
                
                if message_data["data"] != None and message_data["data"]["messageEdgeCreate"]["status"] == "message_points_display_price_mismatch":
                    msgPrice = message_data["data"]["messageEdgeCreate"]["bot"]["messagePointLimit"]["displayMessagePointPrice"]
                    variables = {
                                    "chatId": None, 
                                    "bot": bot,
                                    "query":message, 
                                    "shouldFetchChat": True, 
                                    "source":{"sourceType":"chat_input","chatInputMetadata":{"useVoiceRecord":False,}}, 
                                    "clientNonce": generate_nonce(),
                                    "sdid":"",
                                    "attachments":attachments, 
                                    "existingMessageAttachmentsIds":[],
                                    "messagePointsDisplayPrice": msgPrice
                                }
                    message_data = await self.send_request(apiPath, 'SendMessageMutation', variables, file_form)
        
                if message_data["data"] == None and message_data["errors"]:
                    raise ValueError(
                        f"Bot {bot} not found. Make sure the bot exists before creating new chat."
                    )
                else:
                    status = message_data['data']['messageEdgeCreate']['status']
                    if status == 'success' and file_path != []:
                        for file in file_form:
                            logger.info(f"File '{file[0]}' uploaded successfully")
                    elif status == 'unsupported_file_type' and file_path != []:
                        logger.warning("This file type is not supported. Please try again with a different file.")
                    elif status == 'reached_limit':
                        raise RuntimeError(f"Daily limit reached for {bot}.")
                    elif status == 'too_many_tokens':
                        raise RuntimeError(f"{message_data['data']['messageEdgeCreate']['statusMessage']}")
                        
                    logger.info(f"New Thread created | {message_data['data']['messageEdgeCreate']['chat']['chatCode']}")
                
                message_data = message_data['data']['messageEdgeCreate']['chat']
                chatCode = message_data['chatCode']
                chatId = message_data['chatId']
                title = message_data['title']
                if bot not in self.current_thread:
                    self.current_thread[bot] = [{'chatId': chatId, 'chatCode': chatCode, 'id': message_data['id'], 'title': message_data['title']}]
                elif self.current_thread[bot] == []:
                    self.current_thread[bot] = [{'chatId': chatId, 'chatCode': chatCode, 'id': message_data['id'], 'title': message_data['title']}]
                else:
                    self.current_thread[bot].append({'chatId': chatId, 'chatCode': chatCode, 'id': message_data['id'], 'title': message_data['title']})
                del self.active_messages["pending"]
            except Exception as e:
                del self.active_messages["pending"]
                raise e
            try:
                human_message = message_data['messagesConnection']['edges'][0]['node']['text']
                human_message_id = message_data['messagesConnection']['edges'][0]['node']['messageId']
            except TypeError:
                raise RuntimeError(f"An unknown error occurred. Raw response data: {message_data}")
        else:
            chatdata = await self.get_threadData(bot, chatCode, chatId)
            chatCode = chatdata['chatCode']
            chatId = chatdata['chatId']
            title = chatdata['title']
            variables = {
                            'chatId': chatId, 
                            'bot': bot, 
                            'query': message, 
                            'shouldFetchChat': False, 
                            'source': { "sourceType": "chat_input", "chatInputMetadata": {"useVoiceRecord": False}}, 
                            "clientNonce": generate_nonce(), 
                            'sdid':"", 
                            'attachments': attachments, 
                            "existingMessageAttachmentsIds":[],
                            "messagePointsDisplayPrice": msgPrice
                        }
            
            try:
                message_data = await self.send_request(apiPath, 'SendMessageMutation', variables, file_form)
                if message_data["data"] != None and message_data["data"]["messageEdgeCreate"]["status"] == "message_points_display_price_mismatch":
                    msgPrice = message_data["data"]["messageEdgeCreate"]["bot"]["messagePointLimit"]["displayMessagePointPrice"]
                    variables = {
                                    "chatId": chatId, 
                                    "bot": bot,
                                    "query":message, 
                                    "shouldFetchChat": True, 
                                    "source":{"sourceType":"chat_input","chatInputMetadata":{"useVoiceRecord":False,}}, 
                                    "clientNonce": generate_nonce(),
                                    "sdid":"",
                                    "attachments":attachments, 
                                    "existingMessageAttachmentsIds":[],
                                    "messagePointsDisplayPrice": msgPrice
                                }
                    message_data = await self.send_request(apiPath, 'SendMessageMutation', variables, file_form)
                    
                if message_data["data"] == None and message_data["errors"]:
                    raise RuntimeError(f"An unknown error occurred. Raw response data: {message_data}")
                else:
                    status = message_data['data']['messageEdgeCreate']['status']
                    if status == 'success' and file_path != []:
                        for file in file_form:
                            logger.info(f"File '{file[0]}' uploaded successfully")
                    elif status == 'unsupported_file_type' and file_path != []:
                        logger.warning("This file type is not supported. Please try again with a different file.")
                    elif status == 'reached_limit':
                        raise RuntimeError(f"Daily limit reached for {bot}.")
                    elif status == 'too_many_tokens':
                        raise RuntimeError(f"{message_data['data']['messageEdgeCreate']['statusMessage']}")
                del self.active_messages["pending"]
            except Exception as e:
                del self.active_messages["pending"]
                raise e
                    
            try:
                human_message = message_data["data"]["messageEdgeCreate"]["message"]
                human_message_id = human_message["node"]["messageId"]
            except TypeError:
                raise RuntimeError(f"An unknown error occurred. Raw response data: {message_data}")
        
        self.message_generating = True
        self.active_messages[human_message_id] = None
        self.message_queues[human_message_id] = queue.Queue()

        last_text = ""
        message_id = None
        
        stateChange = False
        
        while True:
            try:
                response = self.message_queues[human_message_id].get(timeout=timeout)
            except queue.Empty:
                try:
                    if self.retry_attempts > 0:
                        self.retry_attempts -= 1
                        logger.warning(f"Retrying request {3-self.retry_attempts}/3 times...")
                    else:
                        self.retry_attempts = 3
                        del self.active_messages[human_message_id]
                        del self.message_queues[human_message_id]
                        raise RuntimeError("Timed out waiting for response.")
                    await self.connect_ws()
                    continue
                except Exception as e:
                    raise e
            
            response["chatCode"] = chatCode
            response["chatId"] = chatId
            response["title"] = title
            response["msgPrice"] = msgPrice

            if response["state"] == "error_user_message_too_long":
                response["response"]  = 'Message too long. Please try again!'
                yield response
                break
            
            if (response['author'] == 'pacarana' and response['text'].strip() == last_text.strip()):
                response["response"] = ''
            elif response['author'] == 'pacarana' and (last_text == '' or bot != 'web-search'):
                response["response"] = f'{response["text"]}\n'
            else:
                if stateChange == False:
                    response["response"] = response["text"]
                    stateChange = True
                else:
                    response["response"] = response["text"][len(last_text):]
            
            yield response
            
            if response["state"] == "complete" or not self.message_generating:
                if last_text and response["messageId"] == message_id:
                    break
                else:
                    continue
            
            last_text = response["text"]
            message_id = response["messageId"]
            
        async def recv_post_thread():
            bot_message_id = self.active_messages[human_message_id]
            await asyncio.sleep(2.5)
            await self.send_request("receive_POST", "recv", {
                "bot_name": bot,
                "time_to_first_typing_indicator": 300,
                "time_to_first_subscription_response": 600,
                "time_to_full_bot_response": 1100,
                "full_response_length": len(last_text) + 1,
                "full_response_word_count": len(last_text.split(" ")) + 1,
                "human_message_id": human_message_id,
                "bot_message_id": bot_message_id,
                "chat_id": chatId,
                "bot_response_status": "success",
            })
            await asyncio.sleep(0.5)
        
        if response["state"] != "error_user_message_too_long": 
            await recv_post_thread()
            
            if suggest_replies:
                self.suggestions_queue = queue.Queue()
                await self.get_suggestions(self.suggestions_queue, response, chatId, title, chatCode, 10)
                try:
                    suggestions = self.suggestions_queue.get(timeout=10)
                    yield suggestions
                except queue.Empty:
                    yield {'text': response["text"], 'response':'', 'suggestedReplies': [], 'state': None, 'chatCode': chatCode, 'chatId': chatId, 'title': title}
                del self.suggestions_queue
        
        del self.active_messages[human_message_id]
        del self.message_queues[human_message_id]
        self.retry_attempts = 3
        
    async def cancel_message(self, chunk: dict):
        self.message_generating = False
        variables = {"messageId": chunk["messageId"], "textLength": len(chunk["text"])}
        await self.send_request('gql_POST', 'StopMessage_messageCancel_Mutation', variables)
        
    async def chat_break(self, bot: str, chatId: int=None, chatCode: str=None):
        bot = bot_map(bot)
        chatdata = await self.get_threadData(bot, chatCode, chatId)
        chatId = chatdata['chatId']
        variables = {'chatId': chatId, 'clientNonce': generate_nonce()}
        await self.send_request('gql_POST', 'SendChatBreakMutation', variables)
            
    async def delete_message(self, message_ids):
        variables = {'messageIds': message_ids}
        await self.send_request('gql_POST', 'DeleteMessageMutation', variables)
    
    async def purge_conversation(self, bot: str, chatId: int=None, chatCode: str=None, count: int=50, del_all: bool=False):
        bot = bot_map(bot)
        if chatId != None and chatCode == None:
            chatdata = await self.get_threadData(bot, chatCode, chatId)
            chatCode = chatdata['chatCode']
        variables = {'chatCode': chatCode}
        response_json = await self.send_request('gql_POST', 'ChatPageQuery', variables)
        if response_json['data'] == None and response_json["errors"]:
            raise RuntimeError(f"An unknown error occurred. Raw response data: {response_json}")
        edges = response_json['data']['chatOfCode']['messagesConnection']['edges']
        
        if del_all == True:
            while True:
                if len(edges) == 0:
                    break
                message_ids = []
                for edge in edges:
                    message_ids.append(edge['node']['messageId'])
                await self.delete_message(message_ids)
                await asyncio.sleep(0.5)
                response_json = await self.send_request('gql_POST', 'ChatPageQuery', variables)
                edges = response_json['data']['chatOfCode']['messagesConnection']['edges']
            logger.info(f"Deleted {len(message_ids)} messages of {chatCode}")
        else:
            num = count
            while True:
                if len(edges) == 0 or num == 0:
                    break
                message_ids = []
                for edge in edges:
                    message_ids.append(edge['node']['messageId'])
                await self.delete_message(message_ids)
                await asyncio.sleep(0.5)
                num -= len(message_ids)
                if len(edges) < num:
                    response_json = await self.send_request('gql_POST', 'ChatPageQuery', variables)
                    edges = response_json['data']['chatOfCode']['messagesConnection']['edges']
            logger.info(f"Deleted {count-num} messages of {chatCode}")
            
    async def purge_all_conversations(self):
        self.current_thread = {}
        await self.send_request('gql_POST', 'DeleteUserMessagesMutation', {})
    
    async def delete_chat(self, bot: str, chatId: any=None, chatCode: any=None, del_all: bool=False):
        bot = bot_map(bot)
        try:
            chatdata = await self.get_chat_history(bot=bot)['data'][bot]
        except:
            raise RuntimeError(f"No chat found for {bot}. Make sure the bot has a chat history before deleting.")
        if chatId != None and not isinstance(chatId, list):
            if bot in self.current_thread:
                for thread in range(len(self.current_thread[bot])):
                    if self.current_thread[bot][thread]['chatId'] == chatId:
                        del self.current_thread[bot][thread]
                        break
            await self.send_request('gql_POST', 'DeleteChat', {'chatId': chatId})
            logger.info(f"Chat {chatId} deleted")
        if del_all == True:
            if bot in self.current_thread:
                del self.current_thread[bot]
            for chat in chatdata:
                await self.send_request('gql_POST', 'DeleteChat', {'chatId': chat['chatId']})
                logger.info(f"Chat {chat['chatId']} deleted")
        if chatCode != None:
                for chat in chatdata:
                    if isinstance(chatCode, list):
                        if chat['chatCode'] in chatCode:
                            chatId = chat['chatId']
                            if bot in self.current_thread:
                                for thread in range(len(self.current_thread[bot])):
                                    if self.current_thread[bot][thread]['chatId'] == chatId:
                                        del self.current_thread[bot][thread]
                                        break
                            await self.send_request('gql_POST', 'DeleteChat', {'chatId': chatId})
                            logger.info(f"Chat {chatId} deleted")
                    else:
                        if chat['chatCode'] == chatCode:
                            chatId = chat['chatId']
                            if bot in self.current_thread:
                                for thread in range(len(self.current_thread[bot])):
                                    if self.current_thread[bot][thread]['chatId'] == chatId:
                                        del self.current_thread[bot][thread]
                                        break
                            await self.send_request('gql_POST', 'DeleteChat', {'chatId': chatId})
                            logger.info(f"Chat {chatId} deleted")
                            break               
        elif chatId != None and isinstance(chatId, list):
            for chat in chatId:
                if bot in self.current_thread:
                    if self.current_thread[bot]:
                        for thread in range(len(self.current_thread[bot])):
                            if self.current_thread[bot][thread]['chatId'] == chat:
                                del self.current_thread[bot][thread]
                                break
                await self.send_request('gql_POST', 'DeleteChat', {'chatId': chat})
                logger.info(f"Chat {chat} deleted")  
                
    async def get_previous_messages(self, bot: str, chatId: int = None, chatCode: str = None, count: int = 50, get_all: bool = False):
        bot = bot_map(bot)
        try:
            getchatdata = await self.get_threadData(bot, chatCode, chatId)
        except:
            raise RuntimeError(f"Thread not found. Make sure the thread exists before getting messages.")
        chatCode = getchatdata['chatCode']
        id = getchatdata['id']
        messages = []
        cursor = None
        edges = True

        if get_all:
            while edges:
                variables = {'count': 100, 'cursor': cursor, 'id': id}
                response_json = await self.send_request('gql_POST', 'ChatListPaginationQuery', variables)
                chatdata = response_json['data']['node']
                edges = chatdata['messagesConnection']['edges'][::-1]
                for edge in edges:
                    messages.append({'author': edge['node']['author'], 'text': edge['node']['text'], 'messageId': edge['node']['messageId'], 'contentType': edge['node']['contentType']})
                cursor = chatdata['messagesConnection']['pageInfo']['startCursor']
        else:
            num = count
            while edges and num > 0:
                variables = {'count': 100, 'cursor': cursor, 'id': id}
                response_json = await self.send_request('gql_POST', 'ChatListPaginationQuery', variables)
                chatdata = response_json['data']['node']
                edges = chatdata['messagesConnection']['edges'][::-1]
                for edge in edges:
                    messages.append({'author': edge['node']['author'], 'text': edge['node']['text'], 'messageId': edge['node']['messageId'], 'contentType': edge['node']['contentType']})
                    num -= 1
                    if len(messages) == count:
                        break
                cursor = chatdata['messagesConnection']['pageInfo']['startCursor']

        logger.info(f"Found {len(messages)} messages of {chatCode}")
        return messages[::-1]
        
    async def get_user_bots(self, user: str):
        variables = {'handle': user}
        response_json = await self.send_request('gql_POST', 'HandleProfilePageQuery', variables)
        if response_json['data'] == None and response_json["errors"]:
            raise RuntimeError(f"User {user} not found. Make sure the user exists before getting bots.")
        userData = response_json['data']['user']
        logger.info(f"Found {userData['createdBotCount']} bots of {user}")
        botsData = userData['createdBots']
        bots = [each['handle'] for each in botsData]
        return bots
        
    async def complete_profile(self, handle: str=None):
        if handle == None:
            handle = ''.join(secrets.choice(string.ascii_letters + string.digits) for i in range(10))
        variables = {"handle" : handle}
        await self.send_request('gql_POST', 'NuxInitialModal_poeSetHandle_Mutation', variables)
        await self.send_request('gql_POST', 'MarkMultiplayerNuxCompleted', {})
    
    async def get_available_knowledge(self, botName: str, count: int=10, get_all: bool=False):
        response = await self.get_botInfo(botName)
        if response['viewerIsCreator'] == False:
            raise RuntimeError(f"You are not the creator of {botName}.")
        id = response["id"]
        sources_ids = {}
        new_variables = {"after": "5", "first": count, "id": id}
        response = await self.send_request('gql_POST', 'BotKnowledgeSourcesModalPaginationQuery', new_variables)
        edges = response['data']['node']['knowledgeSourceConnection']['edges']
        if edges:
            for edge in edges:
                if edge['node']['title'] not in sources_ids:
                    sources_ids[edge['node']['title']] = [edge['node']['knowledgeSourceId']]
                else:
                    sources_ids[edge['node']['title']].append(edge['node']['knowledgeSourceId'])
                total_sources = edge['cursor']
            while (len(sources_ids) < count or get_all):
                if response['data']['node']['knowledgeSourceConnection']['pageInfo']['hasNextPage']:
                    cursor = response['data']['node']['knowledgeSourceConnection']['pageInfo']['endCursor']
                else:
                    break
                new_variables = {"after": cursor, "first": count, "id": id }
                response = await self.send_request('gql_POST', 'BotKnowledgeSourcesModalPaginationQuery', new_variables)
                if edges:
                    edges = response['data']['node']['knowledgeSourceConnection']['edges']
                    for edge in edges:
                        if edge['node']['title'] not in sources_ids:
                            sources_ids[edge['node']['title']] = [edge['node']['knowledgeSourceId']]
                        else:
                            sources_ids[edge['node']['title']].append(edge['node']['knowledgeSourceId'])
                        total_sources = edge['cursor']
        logger.info(f"Found {len(sources_ids)} unique knowledge sources out of {int(total_sources)+1} sources from {botName}")
        return sources_ids

    async def upload_knowledge(self, file_path: list=[], text_knowledge: list=[]):
        ids = {}
        if text_knowledge != []:
            for text in text_knowledge:
                if text != {} and "title" not in text and "content" not in text:
                    error_msg = f"Invalid text knowledge {text}. \nPlease make sure the text knowledge is in the format of " + "{'title': <str>, 'content': <str>}"
                    raise ValueError(error_msg)
                else:
                    response = await self.send_request('gql_POST', 'Knowledge_CreateKnowledgeSourceMutation', {"sourceInput":{"text_input":{"title":text["title"],"content":text["content"]}}})
                    if response['data']['knowledgeSourceCreate']['status'] != 'success':
                        raise RuntimeError(f"Failed to upload text '{text['title']}'. \nRaw response data: {response}")
                    title = response['data']['knowledgeSourceCreate']['source']['title']
                    sourceid = response['data']['knowledgeSourceCreate']['source']['knowledgeSourceId']
                    if title not in ids:
                        ids[title] = [sourceid]
                    else:
                        ids[title].append(sourceid)
                    logger.info(f"Text '{text['title']}' uploaded successfully")
                    await asyncio.sleep(2)        
        if file_path != []:
            for path in file_path:
                file_form, file_size = generate_file([path], self.client.proxies)
                if file_size > 50000000:
                    raise RuntimeError("File size too large. Please try again with a smaller file.")
                response = await self.send_request('gql_upload_POST', 'Knowledge_CreateKnowledgeSourceMutation', {"sourceInput":{"file_upload":{"attachment":"file"}}}, file_form, knowledge=True)
                if response['data']['knowledgeSourceCreate']['status'] != 'success':
                    raise RuntimeError(f"Failed to upload file '{path}'. \nRaw response data: {response}")
                title = response['data']['knowledgeSourceCreate']['source']['title']
                sourceid = response['data']['knowledgeSourceCreate']['source']['knowledgeSourceId']
                if title not in ids:
                    ids[title] = [sourceid]
                else:
                    ids[title].append(sourceid)
                for file in file_form:
                    logger.info(f"File '{file[0]}' uploaded successfully")
                await asyncio.sleep(2)
        logger.info(f"Knowledge uploaded successfully | {ids}")
        return ids
        
    async def edit_knowledge(self, knowledgeSourceId: int, title: str=None, content: str=None):
        variables = {"knowledgeSourceId": knowledgeSourceId, 
                     "sourceInput":{
                        "text_input":{
                            "title": title,
                            "content": content
                        }
                    }}
        response = await self.send_request('gql_POST', 'Knowledge_EditKnowledgeSourceMutation', variables)
        if response['data']['knowledgeSourceEdit']['status'] != 'success':
            raise RuntimeError(f"Failed to edit knowledge source {knowledgeSourceId}. \nRaw response data: {response}")
        logger.info(f"Knowledge source {knowledgeSourceId} edited successfully")
        
    async def get_citations(self, messageId: int):
        variables = {"messageId": messageId}
        response = await self.send_request('gql_POST', 'MessageCitationSourceModalQuery', variables)
        if response['data']['message'] == None:
            logger.info(f"No citations found for message {messageId}")
        else:
            citations = response['data']['message']['citations']
            logger.info(f"Found {len(citations)} citations for message {messageId}")
            return citations
        
    async def get_available_creation_models(self):
        response = await self.send_request('gql_POST', 'CreateBotIndexPageQuery', {'messageId': None})
        if response['data'] == None and response["errors"]:
            raise RuntimeError(f"An unknown error occurred. Raw response data: {response}")
        models_data = response['data']['viewer']['botsAllowedForUserCreation']
        models = [
          bot['model'] for bot in models_data
        ]
        return models
            
    async def create_bot(self, handle, prompt, display_name=None, base_model="chinchilla", description="", intro_message="", 
                   api_key=None, api_bot=False, api_url=None, prompt_public=True, pfp_url=None, linkification=False,  
                   markdown_rendering=True, suggested_replies=False, private=False, temperature=None, customMessageLimit=None, 
                   messagePriceCc=None, shouldCiteSources=True, knowledgeSourceIds:dict = {}):
        bot_models = await self.get_available_creation_models()
        if base_model not in bot_models:
            raise ValueError(f"Invalid base model {base_model}. Please choose from {bot_models}")
        # Auto complete profile
        try:
            await self.send_request('gql_POST', 'MarkMultiplayerNuxCompleted', {})
        except:
            await self.complete_profile()
        if knowledgeSourceIds != {}:
            sourceIds = [item for sublist in knowledgeSourceIds.values() for item in sublist]
        else:
            sourceIds = []
        variables = {
            "model": base_model,
            "displayName": display_name,
            "handle": handle,
            "prompt": prompt,
            "isPromptPublic": prompt_public,
            "introduction": intro_message,
            "description": description,
            "profilePictureUrl": pfp_url,
            "apiUrl": api_url,
            "apiKey": api_key,
            "isApiBot": api_bot,
            "hasLinkification": linkification,
            "hasMarkdownRendering": markdown_rendering,
            "hasSuggestedReplies": suggested_replies,
            "isPrivateBot": private,
            "temperature": temperature,
            "customMessageLimit": customMessageLimit,
            "knowledgeSourceIds": sourceIds,
            "messagePriceCc": messagePriceCc,
            "shouldCiteSources": shouldCiteSources
        }
        result = await self.send_request('gql_POST', 'PoeBotCreate', variables)['data']['poeBotCreate']
        if result["status"] != "success":
           logger.error(f"Poe returned an error while trying to create a bot: {result['status']}")
        else:
           logger.info(f"Bot created successfully | {handle}")
        
    # get_bot logic 
    async def get_botData(self, handle):
        variables = {"useChat":False,"useBotName":True,"useBotId":False,"useShareCode":False,"usePostId":False,"chatCode":0,"botName":handle,"botId":0,"shareCode":"","postId":0}
        try:
            response_json = await self.send_request('gql_POST', 'LayoutRightSidebarQuery', variables)
            return response_json['data']['bot']
        except Exception as e:
            raise ValueError(
                f"Fail to get botId from {handle}. Make sure the bot exists and you have access to it."
            ) from e

    async def edit_bot(self, handle, prompt, display_name=None, base_model="chinchilla", description="",
                intro_message="", api_key=None, api_url=None, private=False,
                prompt_public=True, pfp_url=None, linkification=False,
                markdown_rendering=True, suggested_replies=False, temperature=None, customMessageLimit=None, 
                knowledgeSourceIdsToAdd:dict = {}, knowledgeSourceIdsToRemove:dict = {}, messagePriceCc=None, shouldCiteSources=True):  
        bot_models = await self.get_available_creation_models() 
        if base_model not in bot_models:
            raise ValueError(f"Invalid base model {base_model}. Please choose from {bot_models}")  
        
        if knowledgeSourceIdsToAdd != {}:
            addIds = [item for sublist in knowledgeSourceIdsToAdd.values() for item in sublist]
        else:
            addIds = []
        if knowledgeSourceIdsToRemove != {}:
            removeIds = [item for sublist in knowledgeSourceIdsToRemove.values() for item in sublist]
        else:
            removeIds = []
        variables = {
        "baseBot": base_model,
        "botId": await self.get_botData(handle)['botId'],
        "handle": handle,
        "displayName": display_name,
        "prompt": prompt,
        "isPromptPublic": prompt_public,
        "introduction": intro_message,
        "description": description,
        "profilePictureUrl": pfp_url,
        "apiUrl": api_url,
        "apiKey": api_key,
        "hasLinkification": linkification,
        "hasMarkdownRendering": markdown_rendering,
        "hasSuggestedReplies": suggested_replies,
        "isPrivateBot": private,
        "temperature": temperature,
        "customMessageLimit": customMessageLimit,
        "knowledgeSourceIdsToAdd": addIds,
        "knowledgeSourceIdsToRemove": removeIds,
        "messagePriceCc": messagePriceCc,
        "shouldCiteSources": shouldCiteSources
        }
        result = await self.send_request('gql_POST', 'PoeBotEdit', variables)["data"]["poeBotEdit"]
        if result["status"] != "success":
            logger.error(f"Poe returned an error while trying to edit a bot: {result['status']}")
        else:
            logger.info(f"Bot edited successfully | {handle}")
      
    async def delete_bot(self, handle):
        isCreator = await self.get_botData(handle)['viewerIsCreator']
        botId = await self.get_botData(handle)['botId']
        try:
            if isCreator == True:
                response = await self.send_request('gql_POST', "BotInfoCardActionBar_poeBotDelete_Mutation", {"botId": botId})
            else:
                response = await self.send_request('gql_POST',
                    "BotInfoCardActionBar_poeRemoveBotFromUserList_Mutation",
                    {"connections": [
                        "client:Vmlld2VyOjA=:__HomeBotSelector_viewer_availableBotsConnection_connection"],
                        "botId": botId}
                )
        except Exception:
            raise ValueError(
                f"Failed to delete bot {handle}. Make sure the bot exists and belongs to you."
            )
        if response["data"] is None and response["errors"]:
            raise ValueError(
                f"Failed to delete bot {handle} :{response['errors'][0]['message']}"
            )
        else:
            logger.info(f"Bot deleted successfully | {handle}")
            
    async def get_available_categories(self):
        categories = []
        response_json = await self.send_request('gql_POST', 'ExploreBotsIndexPageQuery', {"categoryName":"defaultCategory"})
        if response_json['data'] == None and response_json["errors"]:
            raise RuntimeError(f"An unknown error occurred. Raw response data: {response_json}")
        else:
            for category in response_json['data']['exploreBotsCategoryObjects']:
                categories.append(category['categoryName'])
        return categories
                
    async def explore(self, categoryName: str='defaultCategory', search: str=None, entity_type: str = "bot", count: int = 50, explore_all: bool = False):
        if entity_type not in ["bot", "user"]:
            raise ValueError(f"Entity type {entity_type} not found. Make sure the entity type is either bot or user.")
        if categoryName != 'defaultCategory' and categoryName not in await self.get_available_categories():
            raise ValueError(f"Category {categoryName} not found. Make sure the category exists before exploring.")
        bots = []
        if search == None:
            query_name = "ExploreBotsListPaginationQuery"
            variables = {"categoryName": categoryName, "count": count}
            connectionType = "exploreBotsConnection"
        else:
            query_name = "SearchResultsListPaginationQuery"
            variables = {"query": search, "entityType": entity_type, "count": 50}
            connectionType = "searchEntityConnection"
            
        result = await self.send_request("gql_POST", query_name, variables)
        if search == None:
            new_cursor = result["data"][connectionType]["edges"][-1]["cursor"]
        else:
            new_cursor = 60
            
        if entity_type == "bot":
            bots += [
                each["node"]['handle'] for each in result["data"][connectionType]["edges"]
            ]
        else:
            bots += [
                each["node"]['nullableHandle'] for each in result["data"][connectionType]["edges"]
            ]
        if len(bots) >= count and not explore_all:
            if entity_type == "bot":
                logger.info("Succeed to explore bots")
            else:
                logger.info("Succeed to explore users")
            return bots[:count]
        while len(bots) < count or explore_all:
            if search == None:
                result = await self.send_request("gql_POST", query_name, {"categoryName": categoryName, "count": count, "cursor": new_cursor})
            else:
                result = await self.send_request("gql_POST", query_name, {"query": search, "entityType": entity_type, "count": 50, "cursor": new_cursor})
            if len(result["data"][connectionType]["edges"]) == 0:
                if not explore_all:
                    if entity_type == "bot":
                        logger.info(f"No more bots could be explored, only {len(bots)} bots found.")
                    else:
                        logger.info(f"No more users could be explored, only {len(bots)} users found.")
                return bots
            if search == None:
                new_cursor = result["data"][connectionType]["edges"][-1]["cursor"]
            else:
                new_cursor += 50
            if entity_type == "bot":
                new_bots = [
                    each["node"]['handle'] for each in result["data"][connectionType]["edges"]
                ]
            else:
                new_bots = [
                    each["node"]['nullableHandle'] for each in result["data"][connectionType]["edges"]
                ]
            bots += new_bots
        
        if entity_type == "bot":
            logger.info("Succeed to explore bots")
        else:
            logger.info("Succeed to explore users")
        return bots[:count]
    
    async def share_chat(self, bot: str, chatId: int=None, chatCode: str=None, count: int=None):
        bot = bot_map(bot)
        chatdata = await self.get_threadData(bot, chatCode, chatId)
        chatCode = chatdata['chatCode']
        chatId = chatdata['chatId']
        variables = {'chatCode': chatCode}
        response_json = await self.send_request('gql_POST', 'ChatPageQuery', variables)
        edges = response_json['data']['chatOfCode']['messagesConnection']['edges']
        if count == None:
            count = len(edges)
        message_ids = []
        for edge in edges:
            message_ids.append(edge['node']['messageId'])
        variables = {'chatId': chatId, 'messageIds': message_ids if count == None else message_ids[:count]}
        response_json = await self.send_request('gql_POST', 'ShareMessageMutation', variables)
        if response_json['data']['messagesShare']:
            shareCode = response_json['data']['messagesShare']["shareCode"]
            logger.info(f'Shared {count} messages with code: {shareCode}')
            return shareCode
        else:
            logger.error(f'An error occurred while sharing the messages')
            return None
        
    async def import_chat(self, bot:str="", shareCode: str=""):
        bot = bot_map(bot)
        variables = {'botName': bot, 'shareCode': shareCode, 'postId': None}
        response_json = await self.send_request('gql_POST', 'ContinueChatCTAButton_continueChatFromPoeShare_Mutation', variables)
        if response_json['data']['continueChatFromPoeShare']['status'] == 'success':
            logger.info(f'Chat imported successfully')
            chatCode = response_json['data']['continueChatFromPoeShare']['messages'][0]['node']['chat']['chatCode']
            chatdata = await self.get_threadData(bot, chatCode=chatCode)
            chatId = chatdata['chatId']
            return {'chatId': chatId, 'chatCode': chatCode}
        else:
            logger.error(f'An error occurred while importing the chat')
            return None
        
    async def create_group(self, group_name: str=None, bots: list = []): 
        if group_name == None:
            group_name = ''.join(secrets.choice(string.ascii_letters + string.digits) for i in range(10))
        else:
            group_name = group_name.replace(" ", "_")
            
        if bots == []:
            raise ValueError(f"Please provide at least one bot to create a group.")
            
        if group_name in self.groups:
            raise ValueError(f"Group {group_name} already exists. Please try again with a different group name.")
        
        bots_list = []
        for bot in bots:
            if 'name' not in bot:
                bot['name'] = bot['bot']
            if 'talkativeness' not in bot:
                bot['talkativeness'] = 0.5
            bots_list.append({'bot': bot_map(bot['bot']), 'name': bot['name'].lower(), 'chatId': None, 'chatCode': None, 'priority': 0, 'bot_log': [], 'talkativeness': bot['talkativeness']})
        self.groups[group_name] = {'bots': bots_list, 'conversation_log': [], 'previous_bot': '', 'dual_lock': ['','']}
        logger.info(f"Group {group_name} created with the following bots: {bots}")
        return group_name
    
    async def delete_group(self, group_name: str):
        if group_name not in self.groups:
            raise ValueError(f"Group {group_name} not found. Make sure the group exists before deleting.")
        if self.groups[group_name]['bots'] != {}:
            for bot, chatdata in self.groups[group_name]['bots'].items():
                if chatdata['chatId'] != None:
                    await self.delete_chat(bot, chatdata['chatId'])
        del self.groups[group_name]
        logger.info(f"Group {group_name} deleted")
        
    async def get_available_groups(self):
        return self.groups
    
    async def get_group(self, group_name: str):
        if group_name not in self.groups:
            raise ValueError(f"Group {group_name} not found. Make sure the group exists before getting.")
        return self.groups[group_name]
    
    async def save_group_history(self, group_name: str, file_path: str=None):
        try:
            oldData = await self.load_group_history(group_name, file_path=file_path)
            oldData = oldData['group_data']['conversation_log']
        except:
            oldData = None
        
        groupData = self.groups[group_name]
        if oldData != None:
            new_conversation_log = oldData + groupData['conversation_log']
        else:
            new_conversation_log = groupData['conversation_log']
        saveData = {
            'bots' : groupData['bots'],
            'conversation_log' : new_conversation_log,
            'previous_bot' : groupData['previous_bot'],
            'dual_lock' : groupData['dual_lock']
        }
        if file_path == None:
            file_path = group_name + '.json'
        else:
            # check if file path is valid and is a json file
            if not os.path.exists(file_path):
                raise ValueError(f"File path {file_path} is invalid.")
            if not file_path.endswith('.json'):
                raise ValueError(f"File path {file_path} is not a json file.")
        with open(file_path, 'w') as f:
            json.dump(saveData, f)
        logger.info(f"Group {group_name} saved to {file_path}")
        return file_path
        
    async def load_group_history(self, file_path: str=None):
        if file_path == None:
            raise ValueError(f"Please provide a valid file path.")
        else:
            if not os.path.exists(file_path):
                raise ValueError(f"File path {file_path} is invalid.")
            if not file_path.endswith('.json'):
                raise ValueError(f"File path {file_path} is not a json file.")
            if os.stat(file_path).st_size == 0:
                raise ValueError(f"File path {file_path} is empty.")
        with open(file_path, 'r') as f:
            groupData = json.load(f)
        group_name = file_path.split('.')[0]
        self.groups[group_name] = groupData
        logger.info(f"Group {group_name} loaded from {file_path}")
        return {'group_name': group_name, 'group_data': groupData}
    
    async def get_most_mentioned(self, group_name: str, message: str):
        mod_message = message.lower()
        bots = self.groups[group_name]['bots']
        if len(bots) == 1:
            return bots[0]
        if any(bot['name'] in mod_message for bot in bots):
            for bot in bots:
                bot['priority'] = 0
            for bot in bots:
                bot_model = bot['bot']
                bot_name = bot['name']
                bot['priority'] += mod_message.count(bot_model)
                bot['priority'] += mod_message.count(bot_name)
            sorted_bots = sorted(bots, key=lambda k: k['priority'], reverse=True)
            if sorted_bots[0]['name'] != self.groups[group_name]['previous_bot']:
                topBot = sorted_bots[0]
            else:
                topBot = sorted_bots[1]
        else:
            topBot = random.choice(bots)
            while topBot['name'] == self.groups[group_name]['previous_bot']:
                topBot = random.choice(bots)
        self.groups[group_name]['previous_bot'] = topBot['name']
        return topBot
        
    
    async def send_message_to_group(self, group_name: str, message: str='', timeout: int=60, user: str="User", autosave:bool=False, autoplay:bool=False, preset_history: str=''):
        if group_name not in self.groups:
            raise ValueError(f"Group {group_name} not found. Make sure the group exists before sending message.")
        
        bots = self.groups[group_name]['bots']
        bot_names = [bot['name'] for bot in bots]
        
        last_text = ""
        preset_log = []
        
        if preset_history == '':
            if self.groups[group_name]['conversation_log'] != []:
                # load all the messages in the conversation log from oldest to newest
                old_logs = self.groups[group_name]['conversation_log'][1:]
                for text in old_logs:
                    if text.split(":")[0].strip() in bot_names:
                        last_text += text
                        last_text += "\n"
        else:
            preset_log = await self.load_group_history(file_path=preset_history)['group_data']['conversation_log']
            if preset_log != []:
                for text in preset_log:
                    if text.split(":")[0].strip() in bot_names:
                        last_text += text
                        last_text += "\n"
        
        if autoplay == False:
            previous_text = ""
            current_bot = await self.get_most_mentioned(group_name, message)
            if self.groups[group_name]['conversation_log'] != [] or preset_log != []:
                next_message = f"\n[System Notice : You are participating in a role-playing chat. You will act as {current_bot['name']} in a multiway roleplay between {user}, and other parties including {bot_names}, You will only act as {current_bot['name']} and stay in character at all times. As the AI language model, Your role is to portray {current_bot['name']} in this chat using the first-person narrative. Let's engage in immersive roleplay and respond to the previous message without addressing it as a system message or revealing our roles as {current_bot['name']} or the fact that we are roleplaying. You must respond to the previous message without explicitly writing '{current_bot['name']}' at the start.]\nChat history updated with new responses:\n\n" + f"{last_text}\n" + f"{user} : {message}\n"
            else:
                next_message = f"\n[System Notice : You are participating in a role-playing chat. You will act as {current_bot['name']} in a multiway roleplay between {user}, and other parties including {bot_names}, You will only act as {current_bot['name']} and stay in character at all times. As the AI language model, Your role is to portray {current_bot['name']} in this chat using the first-person narrative. Let's engage in immersive roleplay and respond to the previous message without addressing it as a system message or revealing our roles as {current_bot['name']} or the fact that we are roleplaying. You must respond to the previous message without explicitly writing '{current_bot['name']}' at the start. You will start with a greeting to {user}.]\nChat history updated with new responses:\n\n" + f"{user} : {message}\n"
        else:
            try:
                previous_text = self.groups[group_name]['conversation_log'][-1].split(":")[1].strip()
            except:
                previous_text = ""
            current_bot = await self.get_most_mentioned(group_name, previous_text)
            if self.groups[group_name]['conversation_log'] != []:
                next_message = f"\n[System Notice : You are participating in a role-playing chat. You will act as {current_bot['name']} in a multiway roleplay between other parties including {bot_names}, You will only act as {current_bot['name']} and stay in character at all times. As the AI language model, Your role is to portray {current_bot['name']} in this chat using the first-person narrative. Let's engage in immersive roleplay and respond to the previous message without addressing it as a system message or revealing our roles as {current_bot['name']} or the fact that we are roleplaying. You must respond to the previous message without explicitly writing '{current_bot['name']}' at the start.]\nChat history updated with new responses:\n\n" + f"{last_text}\n"
            else:
                next_message = f"\n[System Notice : You are participating in a role-playing chat. You will act as {current_bot['name']} in a multiway roleplay between other parties including {bot_names}, You will only act as {current_bot['name']} and stay in character at all times. As the AI language model, Your role is to portray {current_bot['name']} in this chat using the first-person narrative. Let's engage in immersive roleplay and respond to the previous message without addressing it as a system message or revealing our roles as {current_bot['name']} or the fact that we are roleplaying. You must respond to the previous message without explicitly writing '{current_bot['name']}' at the start. You will start with a greeting to everyone.]\n\n"
        
        self.groups[group_name]['conversation_log'] = []
        
        max_turns = random.randint(len(bots), int(len(bots)*2))
        async for _ in range(max_turns):
            await asyncio.sleep(random.randint(3, 5))

            async for chunk in self.send_message(current_bot['bot'], next_message, chatCode=current_bot['chatCode']):
                yield {'bot': current_bot['name'], 'response': chunk['response']}
                
            current_bot['chatCode'] = chunk['chatCode']
            current_bot['chatId'] = chunk['chatId']
            
            self.groups[group_name]['conversation_log'].append(f"{current_bot['name']} : {chunk['text']}\n")
            previous_text = chunk['text']
            prev_bot = current_bot

            if current_bot['name'] not in self.groups[group_name]['dual_lock']:
                self.groups[group_name]['dual_lock'][0] = current_bot['name']
                 
            # Fetch the next most mentioned bot
            current_bot = await self.get_most_mentioned(group_name, previous_text)
            
            # Append the second bot to dual lock  
            if current_bot['name'] in self.groups[group_name]['dual_lock']:
                # The same dual lock
                current_bot['bot_log'] = [self.groups[group_name]['conversation_log'][-1]]
            else:
                # New dual lock
                if len(self.groups[group_name]['conversation_log']) > 10:
                    current_bot['bot_log'] = self.groups[group_name]['conversation_log'][-10:]
                else:
                    current_bot['bot_log'] = self.groups[group_name]['conversation_log']  
                    
                for index in range(len(self.groups[group_name]['dual_lock'])):
                    if self.groups[group_name]['dual_lock'][index] != prev_bot['name']:
                        self.groups[group_name]['dual_lock'][index] = current_bot['name']
                        break
                    
            if autoplay == False:
                next_message = f"\n[System Notice : You are participating in a role-playing chat. You will act as {current_bot['name']} in a multiway roleplay between {user}, and other parties including {bot_names}, You will only act as {current_bot['name']} and stay in character at all times. As the AI language model, Your role is to portray {current_bot['name']} in this chat using the first-person narrative. Let's engage in immersive roleplay and respond to the previous message without addressing it as a system message or revealing our roles as {current_bot['name']} or the fact that we are roleplaying. You must respond to the previous message without explicitly writing '{current_bot['name']}' at the start.]\nChat history updated with new responses:\n\n"
            else:
                next_message = f"\n[System Notice : You are participating in a role-playing chat. You will act as {current_bot['name']} in a multiway roleplay between other parties including {bot_names}, You will only act as {current_bot['name']} and stay in character at all times. As the AI language model, Your role is to portray {current_bot['name']} in this chat using the first-person narrative. Let's engage in immersive roleplay and respond to the previous message without addressing it as a system message or revealing our roles as {current_bot['name']} or the fact that we are roleplaying. You must respond to the previous message without explicitly writing '{current_bot['name']}' at the start.]\nChat history updated with new responses:\n\n"

            for text in current_bot['bot_log']:
                if text.split(":")[0].strip() in bot_names:
                    next_message += text
                    next_message += "\n"
                    
        if autosave:
            await self.save_group_history(group_name)