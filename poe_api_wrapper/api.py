from re import search
from time import sleep
from httpx import Client
from requests_toolbelt import MultipartEncoder
import os, secrets, string, random, websocket, json, threading, queue, keyboard
from urllib.parse import urlparse
from .queries import generate_payload
from .proxies import fetch_proxy

"""
This API is modified and maintained by @snowby666
Credit to @ading2210 for the GraphQL queries
"""

BOTS_LIST = {
    'Assistant': 'capybara',
    'Claude-instant-100k': 'a2_100k',
    'Claude-2-100k': 'a2_2',
    'Claude-instant': 'a2',
    'ChatGPT': 'chinchilla',
    'ChatGPT-16k': 'agouti',
    'GPT-4': 'beaver',
    'GPT-4-32k': 'vizcacha',
    'Google-PaLM': 'acouchy',
    'Llama-2-7b': 'llama_2_7b_chat',
    'Llama-2-13b': 'llama_2_13b_chat',
    'Llama-2-70b': 'llama_2_70b_chat',
    'Code-Llama-7b': 'code_llama_7b_instruct',
    'Code-Llama-13b': 'code_llama_13b_instruct',
    'Code-Llama-34b': 'code_llama_34b_instruct'
}

EXTENSIONS = {
    '.pdf': 'application/pdf',
    '.docx': 'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
    '.txt': 'text/plain',
    '.py': 'text/x-python',
    '.js': 'text/javascript',
    '.ts': 'text/plain',
    '.html': 'text/html',
    '.css': 'text/css',
    '.csv': 'text/csv',
    '.c' : 'text/plain',
    '.cs': 'text/plain',
    '.cpp': 'text/plain',
}

def bot_map(bot):
    if bot in BOTS_LIST:
        return BOTS_LIST[bot]
    return bot.lower().replace(' ', '')
    
def generate_nonce(length:int=16):
      return "".join(secrets.choice(string.ascii_letters + string.digits) for i in range(length))

def is_valid_url(url):
    try:
        result = urlparse(url)
        return all([result.scheme, result.netloc])
    except ValueError:
        return False
    
def generate_file(file_path: list):
    files = []   
    for file in file_path: 
        if is_valid_url(file):  
            with Client() as fetcher:
                response = fetcher.get(file)
                file_data = response.read()
            file_name = file.split('/')[-1]
            file_extension = os.path.splitext(file_name)[1].lower()
        else: 
            file_extension = os.path.splitext(file)[1].lower()
            file_name = os.path.basename(file)
            file_data = open(file, 'rb')
            
        if file_extension in EXTENSIONS:
            content_type = EXTENSIONS[file_extension]
        else:
            raise RuntimeError("This file type is not supported. Please try again with a different file.") 
        files.append((file_name, file_data, content_type))
    return files

class PoeApi:
    BASE_URL = 'https://www.quora.com'
    HEADERS = {
        'Host': 'www.quora.com',
        'Accept': '*/*',
        'apollographql-client-version': '1.1.6-65',
        'Accept-Language': 'en-US,en;q=0.9',
        'User-Agent': 'Poe 1.1.6 rv:65 env:prod (iPhone14,2; iOS 16.2; en_US)',
        'apollographql-client-name': 'com.quora.app.Experts-apollo-ios',
        'Connection': 'keep-alive',
        'Content-Type': 'application/json',
    }
    FORMKEY_PATTERN = r'formkey": "(.*?)"'

    def __init__(self, cookie: str, proxy: bool=False):
        if proxy == True:
            proxies = fetch_proxy()
            for p in range(len(proxies)):
                try:
                    self.client = Client(timeout=180, proxies= {"http://": f"{proxies[p]}"})
                    print(f"Connection established with {proxies[p]}")
                    self.proxy = proxies[p]
                    break
                except:
                    print(f"Connection failed with {proxies[p]}. Trying {p+1}/{len(proxies)} ...")
                    sleep(1)
        else:
            self.client = Client(timeout=180)
        self.client.cookies.set('m-b', cookie)
        self.client.headers.update({
            **self.HEADERS,
            'Quora-Formkey': self.get_formkey,
        })
        
        self.ws_connecting = False
        self.ws_connected = False
        self.ws_error = False
        self.active_messages = {}
        self.message_queues = {}
        self.message_generating = True
        self.ws_domain = f"tch{random.randint(1, int(1e6))}"[:9]
        
        self.connect_ws()
        
    def __del__(self):
        self.client.close()

    @property
    def get_formkey(self):
        response = self.client.get(self.BASE_URL, headers=self.HEADERS, follow_redirects=True)
        formkey = search(self.FORMKEY_PATTERN, response.text)[1]
        return formkey
    
    def send_request(self, path: str, query_name: str="", variables: dict={}, file_form: list=[]):
        payload = generate_payload(query_name, variables)
        if file_form == []:
            headers= {'Content-Type': 'application/x-www-form-urlencoded'}
        else:
            fields = {'queryInfo': payload}
            for i in range(len(file_form)):
                fields[f'file{i}'] = file_form[i]
            payload = MultipartEncoder(
                fields=fields
                )
            headers = {'Content-Type': payload.content_type}
            payload = payload.to_string()
        response = self.client.post(f'{self.BASE_URL}/poe_api/{path}', data=payload, headers=headers)
        return response.json()
    
    def get_channel_settings(self):
        response = self.client.get(f'{self.BASE_URL}/poe_api/settings', headers=self.HEADERS, follow_redirects=True)
        self.tchannel_data = response.json()["tchannelData"]
        self.client.headers["Quora-Tchannel"] = self.tchannel_data["channel"]
        self.channel_url = f'wss://{self.ws_domain}.tch.{self.tchannel_data["baseHost"]}/up/{self.tchannel_data["boxName"]}/updates?min_seq={self.tchannel_data["minSeq"]}&channel={self.tchannel_data["channel"]}&hash={self.tchannel_data["channelHash"]}'
        return self.channel_url
    
    def subscribe(self):
        try:
            self.send_request('gql_POST', "SubscriptionsMutation",
                {
                    "subscriptions": [
                        {
                            "subscriptionName": "messageAdded",
                            "query": None,
                            "queryHash": "6d5ff500e4390c7a4ee7eeed01cfa317f326c781decb8523223dd2e7f33d3698",
                        },
                        {
                            "subscriptionName": "messageCancelled",
                            "query": None,
                            "queryHash": "dfcedd9e0304629c22929725ff6544e1cb32c8f20b0c3fd54d966103ccbcf9d3",
                        },
                        {
                            "subscriptionName": "messageDeleted",
                            "query": None,
                            "queryHash": "91f1ea046d2f3e21dabb3131898ec3c597cb879aa270ad780e8fdd687cde02a3",
                        },
                        {
                            "subscriptionName": "viewerStateUpdated",
                            "query": None,
                            "queryHash": "ee640951b5670b559d00b6928e20e4ac29e33d225237f5bdfcb043155f16ef54",
                        },
                        {
                            "subscriptionName": "messageLimitUpdated",
                            "query": None,
                            "queryHash": "d862b8febb4c058d8ad513a7c118952ad9095c4ec0a5471540133fc0a9bd3797",
                        },
                        {
                            "subscriptionName": "chatTitleUpdated",
                            "query": None,
                            "queryHash": "740e2c7ab27297b7a8acde39a400b932c71beb7e9b525280fc99c1639f1be93a",
                        },
                    ]
                },
            )
        except Exception as e:
            raise Exception(
                "Failed to subscribe by sending SubscriptionsMutation"
            ) from e
            
    def ws_run_thread(self):
        kwargs = {}
        self.ws.run_forever(**kwargs)

    def connect_ws(self, timeout=5):
        if self.ws_connected:
            return

        if self.ws_connecting:
            while not self.ws_connected:
                sleep(0.01)
            return

        self.ws_connecting = True
        self.ws_connected = False

        self.get_channel_settings()
        self.subscribe()

        ws = websocket.WebSocketApp(self.channel_url, on_message=self.on_message, on_open=self.on_ws_connect, on_error=self.on_ws_error, on_close=self.on_ws_close)
        
        self.ws = ws

        t = threading.Thread(target=self.ws_run_thread, daemon=True)
        t.start()

        timer = 0
        while self.ws_error:
            sleep(0.01)
            timer += 0.01
            if timer > timeout:
                self.ws_connecting = False
                self.ws_connected = False
                self.ws_error = True
                ws.close()
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
            self.ws_error = False
            self.connect_ws()

    def on_ws_error(self, ws, error):
        self.ws_connecting = False
        self.ws_connected = False
        self.ws_error = True

    def on_message(self, ws, msg):
        try:
            data = json.loads(msg)
            if not "messages" in data:
                return
            for message_str in data["messages"]:
                message_data = json.loads(message_str)
                if message_data["message_type"] != "subscriptionUpdate":
                    continue
                message = message_data["payload"]["data"]["messageAdded"]
        
                copied_dict = self.active_messages.copy()
                for key, value in copied_dict.items():
                    if value == message["messageId"] and key in self.message_queues:
                        self.message_queues[key].put(message)
                        return

                    elif key != "pending" and value == None and message["state"] != "complete":
                        self.active_messages[key] = message["messageId"]
                        self.message_queues[key].put(message)
                        return
        except Exception:
            self.disconnect_ws()
            self.connect_ws()
    
    def get_available_bots(self, count: int=25, get_all: bool=False):
        self.bots = {}
        if not (get_all or count):
            raise TypeError("Please provide at least one of the following parameters: get_all=<bool>, count=<int>")
        response = self.send_request('gql_POST',"AvailableBotsSelectorModalPaginationQuery", {}) 
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
            response = self.send_request("gql_POST", "AvailableBotsSelectorModalPaginationQuery", {"cursor": cursor})
            new_bots = [
                each["node"]
                for each in response["data"]["viewer"]["availableBotsConnection"]["edges"]
                if each["node"]["deletionState"] == "not_deleted"
            ]
            cursor = response["data"]["viewer"]["availableBotsConnection"]["pageInfo"]["endCursor"]
            bots += new_bots
            if len(new_bots) == 0:
                if not get_all:
                    print(f"Only {len(bots)} bots found on this account")
                else:
                    print("Succeed to get all available bots")
                self.bots.update({bot["handle"]: {"bot": bot} for bot in bots})
                return self.bots
            
        print("Succeed to get available bots")
        self.bots.update({bot["handle"]: {"bot": bot} for bot in bots})
        return self.bots
    
    def get_chat_history(self, bot: str=None): 
        if bot == None:
            useBot = False
            handle = ""
        else:
            useBot = True    
            model = bot.lower().replace(' ', '')
            handle = model
            for key, value in BOTS_LIST.items():
                if model == value:
                    handle = key
                    break
                
        variables = {'handle': handle, 'useBot': useBot}
        response_json = self.send_request('gql_POST', 'ChatsHistoryPageQuery', variables)
        chat_bots = {}
        
        if bot == None:
            edges = response_json['data']['chats']['edges']
            print('-'*18+' \033[38;5;121mChat History\033[0m '+'-'*18)
            print('\033[38;5;121mChat ID\033[0m  |     \033[38;5;121mChat Code\033[0m       | \033[38;5;121mBot Name\033[0m')
            print('-' * 50)
            for edge in edges:
                chat = edge['node']
                model = bot_map(chat["defaultBotObject"]["displayName"])
                print(f'{chat["chatId"]} | {chat["chatCode"]} | {model}')
                if model in chat_bots:
                    chat_bots[model].append({"chatId": chat["chatId"],"chatCode": chat["chatCode"], "id": chat["id"]})
                else:
                    chat_bots[model] = [{"chatId": chat["chatId"], "chatCode": chat["chatCode"], "id": chat["id"]}]
            print('-' * 50)
        else:
            edges = response_json['data']['filteredChats']['edges']
            for edge in edges:
                chat = edge['node']
                try:
                    if model in chat_bots:
                        chat_bots[model].append({"chatId": chat["chatId"],"chatCode": chat["chatCode"], "id": chat["id"]})
                    else:
                        chat_bots[model] = [{"chatId": chat["chatId"], "chatCode": chat["chatCode"], "id": chat["id"]}]
                except:
                    pass           
        return chat_bots
    
    def create_new_chat(self, bot: str="a2", message: str="", file_form: list=[]):
        attachments = []
        if file_form == []:
            apiPath = 'gql_POST'
        else:
            apiPath = 'gql_upload_POST'
            for i in range(len(file_form)):
                attachments.append(f'file{i}')
        variables = {"bot":bot,"query":message,"source":{"sourceType":"chat_input","chatInputMetadata":{"useVoiceRecord":False,"newChatContext":"chat_settings_new_chat_button"}},"sdid":"","attachments":attachments}
        response_json = self.send_request(apiPath, 'ChatHelpersSendNewChatMessageMutation', variables, file_form)
        if response_json["data"] is None and response_json["errors"]:
            raise ValueError(
                f"Bot {bot} not found. Make sure the bot exists before creating new chat."
            )
        if response_json['data']['messageEdgeCreate']['status'] == 'reached_limit':
            raise RuntimeError(f"Daily limit reached for {bot}.")
        print(f"New Thread created | {response_json['data']['messageEdgeCreate']['chat']['chatCode']}")
        
        if file_form != []:
            status = response_json['data']['messageEdgeCreate']['status']
            if status == 'success':
                for file in file_form:
                    print(f"File {file[0]} uploaded successfully")
            elif status == 'unsupported_file_type':
                print("This file type is not supported. Please try again with a different file.")
            else:
                print("An unknown error occurred. Please try again.")
        return response_json['data']['messageEdgeCreate']['chat']

    def send_message(self, bot: str, message: str, chatId: int=None, chatCode: str=None, file_path: list=[], suggest_replies: bool=False, timeout=20):
        bot = bot.lower().replace(' ', '')
        timer = 0
        while None in self.active_messages.values():
            sleep(0.01)
            timer += 0.01
            if timer > timeout:
                raise RuntimeError("Timed out waiting for other messages to send.")
        self.active_messages["pending"] = None
        
        while self.ws_error:
            sleep(0.01)
        self.connect_ws()
        
        attachments = []
        if file_path == []:
            apiPath = 'gql_POST'
            file_form = []
        else:
            apiPath = 'gql_upload_POST'
            file_form = generate_file(file_path)
            for i in range(len(file_form)):
                attachments.append(f'file{i}')
        
        if (chatId == None and chatCode == None):
            try:
                message_data = self.create_new_chat(bot, message, file_form)
                chatCode = message_data['chatCode']
                chatId = message_data['chatId']
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
            chat_data = self.get_chat_history(bot=bot)[bot]
            for chat in chat_data:
                if chatCode == None and chat['chatId'] == chatId:
                    chatCode = chat['chatCode']
                    break
                if chatId == None and chat['chatCode'] == chatCode:  
                    chatId = chat['chatId']
                    break  
                  
            variables = {'bot': bot, 'chatId': chatId, 'query': message, 'source': { "sourceType": "chat_input", "chatInputMetadata": {"useVoiceRecord": False}}, 'withChatBreak': False, "clientNonce": generate_nonce(), 'sdid':"", 'attachments': attachments}
            
            try:
                message_data = self.send_request(apiPath, 'SendMessageMutation', variables, file_form)
                if file_path != []:
                    status = message_data['data']['messageEdgeCreate']['status']
                    if status == 'success':
                        for file in file_form:
                            print(f"File {file[0]} uploaded successfully")
                    elif status == 'unsupported_file_type':
                        print("This file type is not supported. Please try again with a different file.")
                    else:
                        print("An unknown error occurred. Please try again.")
                        
                del self.active_messages["pending"]
            except Exception as e:
                del self.active_messages["pending"]
                raise e
            try:
                if message_data['data']['messageEdgeCreate']['status'] == 'reached_limit':
                    raise RuntimeError(f"Daily limit reached for {bot}.")
                try:
                    human_message = message_data["data"]["messageEdgeCreate"]["message"]
                    human_message_id = human_message["node"]["messageId"]
                except TypeError:
                    raise RuntimeError(f"An unknown error occurred. Raw response data: {message_data}")
            except:
                raise RuntimeError(f"An unknown error occurred. Raw response data: {message_data}")
            
        self.message_generating = True
        self.active_messages[human_message_id] = None
        self.message_queues[human_message_id] = queue.Queue()

        last_text = ""
        message_id = None
        
        while True:
            try:
                message = self.message_queues[human_message_id].get(timeout=timeout)
            except queue.Empty:
                del self.active_messages[human_message_id]
                del self.message_queues[human_message_id]
                raise RuntimeError("Response timed out.")
            
            message["chatCode"] = chatCode
            message["chatId"] = chatId
            if message["state"] == "error_user_message_too_long":
                message["response"]  = 'Message too long. Please try again!'
                yield message
                break
            
            message["response"] = message["text"][len(last_text):]
            
            yield message
            
            if message["state"] == "complete" or not self.message_generating:
                if last_text and message["messageId"] == message_id:
                    break
                else:
                    continue
            
            last_text = message["text"]
            message_id = message["messageId"]
            
        def recv_post_thread():
            bot_message_id = self.active_messages[human_message_id]
            sleep(2.5)
            self.send_request("receive_POST", "recv", {
                "bot_name": bot,
                "time_to_first_typing_indicator": 300, # randomly select
                "time_to_first_subscription_response": 600,
                "time_to_full_bot_response": 1100,
                "full_response_length": len(last_text) + 1,
                "full_response_word_count": len(last_text.split(" ")) + 1,
                "human_message_id": human_message_id,
                "bot_message_id": bot_message_id,
                "chat_id": chatId,
                "bot_response_status": "success",
            })
            sleep(0.5)
            
        def get_suggestions(queue, chatCode: str=None):
            variables = {'chatCode': chatCode}
            state = 'incomplete'
            suggestions = []
            while True:
                sleep(0.1)
                response_json = self.send_request('gql_POST', 'ChatPageQuery', variables)
                hasSuggestedReplies = response_json['data']['chatOfCode']['defaultBotObject']['hasSuggestedReplies']
                edges = response_json['data']['chatOfCode']['messagesConnection']['edges']
                if hasSuggestedReplies and edges:
                    latest_message = edges[-1]['node']
                    suggestions = latest_message['suggestedReplies']
                    state = latest_message['state']
                    if state == 'complete' and suggestions:
                        break
                    if state == 'error_user_message_too_long':
                        break
                else:
                    break
            queue.put({'text': message["text"], 'response':'', 'suggestedReplies': suggestions, 'state': state, 'chatCode': chatCode, 'chatId': chatId})
            
        t1 = threading.Thread(target=recv_post_thread, daemon=True)
        t1.start()
        
        if suggest_replies:
            suggestions_queue = queue.Queue()
            t2 = threading.Thread(target=get_suggestions, args=(suggestions_queue, chatCode), daemon=True)
            t2.start()
            suggestions = suggestions_queue.get()
            yield suggestions
        
        del self.active_messages[human_message_id]
        del self.message_queues[human_message_id]
        
    def cancel_message(self, chunk: dict):
        self.message_generating = False
        variables = {"messageId": chunk["messageId"], "textLength": len(chunk["text"]), "linkifiedTextLength": len(chunk["linkifiedText"])}
        self.send_request('gql_POST', 'ChatHelpers_messageCancel_Mutation', variables)
        
    def chat_break(self, bot: str, chatId: int=None, chatCode: str=None):
        bot = bot.lower().replace(' ', '')
        chat_data = self.get_chat_history(bot=bot)[bot]
        for chat in chat_data:
            if chat['chatId'] == chatId or chat['chatCode'] == chatCode:
                chatId = chat['chatId']
                id = chat['id']
                break
        variables = {"connections": [
                f"client:{id}:__ChatMessagesView_chat_messagesConnection_connection"],
                "chatId": chatId}
        self.send_request('gql_POST', 'ChatHelpers_addMessageBreakEdgeMutation_Mutation', variables)
            
    def delete_message(self, message_ids):
        variables = {'messageIds': message_ids}
        self.send_request('gql_POST', 'DeleteMessageMutation', variables)
    
    def purge_conversation(self, bot: str, chatId: int=None, chatCode: str=None, count: int=50):
        bot = bot.lower().replace(' ', '')
        if chatId != None and chatCode == None:
            chatdata = self.get_chat_history(bot=bot)[bot]
            for chat in chatdata:
                if chat['chatId'] == chatId:
                    chatCode = chat['chatCode']
                    break
        variables = {'chatCode': chatCode}
        response_json = self.send_request('gql_POST', 'ChatPageQuery', variables)
        edges = response_json['data']['chatOfCode']['messagesConnection']['edges']
        
        num = count
        while True:
            if len(edges) == 0 or num == 0:
                break
            message_ids = []
            for edge in edges:
                message_ids.append(edge['node']['messageId'])
            self.delete_message(message_ids)
            num -= len(message_ids)
            if len(edges) < num:
                response_json = self.send_request('gql_POST', 'ChatPageQuery', variables)
                edges = response_json['data']['chatOfCode']['messagesConnection']['edges']
                
        print(f"Deleted {count-num} messages")
            
    def purge_all_conversations(self):
        self.send_request('gql_POST', 'DeleteUserMessagesMutation', {})
    
    def delete_chat(self, bot: str, chatId: any=None, chatCode: any=None, del_all: bool=False):
        bot = bot.lower().replace(' ', '')
        chatdata = self.get_chat_history(bot=bot)[bot]
        if chatId != None and not isinstance(chatId, list):
            self.send_request('gql_POST', 'DeleteChat', {'chatId': chatId})
            print(f'Chat {chatId} deleted') 
        if del_all == True:
            for chat in chatdata:
                self.send_request('gql_POST', 'DeleteChat', {'chatId': chat['chatId']})
                print(f'Chat {chat["chatId"]} deleted')
        if chatCode != None:
                for chat in chatdata:
                    if isinstance(chatCode, list):
                        if chat['chatCode'] in chatCode:
                            chatId = chat['chatId']
                            self.send_request('gql_POST', 'DeleteChat', {'chatId': chatId})
                            print(f'Chat {chatId} deleted')
                    else:
                        if chat['chatCode'] == chatCode:
                            chatId = chat['chatId']
                            self.send_request('gql_POST', 'DeleteChat', {'chatId': chatId})
                            print(f'Chat {chatId} deleted')
                            break               
        elif chatId != None and isinstance(chatId, list):
            for chat in chatId:
                self.send_request('gql_POST', 'DeleteChat', {'chatId': chat})
                print(f'Chat {chat} deleted')   
        
    def complete_profile(self, handle: str=None):
        if handle == None:
            handle = ''.join(secrets.choice(string.ascii_letters + string.digits) for i in range(10))
        variables = {"handle" : handle}
        self.send_request('gql_POST', 'NuxInitialModal_poeSetHandle_Mutation', variables)
        self.send_request('gql_POST', 'MarkMultiplayerNuxCompleted', {})
    
    def create_bot(self, handle, prompt, display_name=None, base_model="chinchilla", description="", intro_message="", api_key=None, api_bot=False, api_url=None, prompt_public=True, pfp_url=None, linkification=False,  markdown_rendering=True, suggested_replies=False, private=False, temperature=None):
        # Auto complete profile
        try:
            self.send_request('gql_POST', 'MarkMultiplayerNuxCompleted', {})
        except:
            self.complete_profile()
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
            "temperature": temperature
        }
        result = self.send_request('gql_POST', 'PoeBotCreate', variables)['data']['poeBotCreate']
        if result["status"] != "success":
           print(f"Poe returned an error while trying to create a bot: {result['status']}")
        else:
           print("Bot created successfully")
        
    # get_bot logic 
    def get_botData(self, handle):
        variables = {"botHandle": handle}
        try:
            response_json = self.send_request('gql_POST', 'BotLandingPageQuery', variables)
            return response_json['data']['bot']
        except Exception as e:
            raise ValueError(
                f"Fail to get botId from {handle}. Make sure the bot exists and you have access to it."
            ) from e

    def edit_bot(self, handle, prompt, display_name=None, base_model="chinchilla", description="",
                intro_message="", api_key=None, api_url=None, private=False,
                prompt_public=True, pfp_url=None, linkification=False,
                markdown_rendering=True, suggested_replies=False, temperature=None):     
        variables = {
        "baseBot": base_model,
        "botId": self.get_botData(handle)['botId'],
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
        "temperature": temperature
        }
        result = self.send_request('gql_POST', 'PoeBotEdit', variables)["data"]["poeBotEdit"]
        if result["status"] != "success":
             print(f"Poe returned an error while trying to edit a bot: {result['status']}")
        else:
             print("Bot edited successfully")
      
    def delete_bot(self, handle):
        isCreator = self.get_botData(handle)['viewerIsCreator']
        botId = self.get_botData(handle)['botId']
        try:
            if isCreator == True:
                response = self.send_request('gql_POST', "BotInfoCardActionBar_poeBotDelete_Mutation", {"botId": botId})
            else:
                response = self.send_request('gql_POST',
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
            print("Bot deleted successfully")
            
    def explore_bots(self, search: str=None, count: int = 50, explore_all: bool = False):
        bots = []
        if search == None:
            query_name = "ExploreBotsListPaginationQuery"
            variables = {"count": count}
            connectionType = "exploreBotsConnection"
        else:
            query_name = "SearchResultsListPaginationQuery"
            variables = {"query": search, "entityType":"bot", "count": 10}
            connectionType = "searchEntityConnection"
            
        result = self.send_request("gql_POST", query_name, variables)
        if search == None:
            new_cursor = result["data"][connectionType]["edges"][-1]["cursor"]
        else:
            new_cursor = 20
        bots += [
            each["node"] for each in result["data"][connectionType]["edges"]
        ]
        if len(bots) >= count and not explore_all:
            return bots[:count]
        while len(bots) < count or explore_all:
            if search == None:
                result = self.send_request("gql_POST", query_name, {"count": count, "cursor": new_cursor})
            else:
                result = self.send_request("gql_POST", query_name, {"query": search, "entityType":"bot", "count": 10, "cursor": new_cursor})
            if len(result["data"][connectionType]["edges"]) == 0:
                if not explore_all:
                    print(f"No more bots could be explored, only {len(bots)} bots found.")
                return bots
            if search == None:
                new_cursor = result["data"][connectionType]["edges"][-1]["cursor"]
            else:
                new_cursor += 10
            new_bots = [
                each["node"]
                for each in result["data"][connectionType]["edges"]
            ]
            bots += new_bots
            
        print("Succeed to explore bots")
        return bots[:count]
        
class Poe:
    @staticmethod
    def select_bot():
        bots = {
            1: 'capybara',
            2: 'a2_100k',
            3: 'a2_2',
            4: 'a2',
            5: 'chinchilla',
            6: 'agouti',
            7: 'beaver',
            8: 'vizcacha',
            9: 'acouchy',
            10: 'llama_2_7b_chat',
            11: 'llama_2_13b_chat',
            12: 'llama_2_70b_chat',
            13: 'code_llama_7b_instruct',
            14: 'code_llama_13b_instruct',
            15: 'code_llama_34b_instruct'
        }
        while True:
            choice = input('Who do you want to talk to?\n'
                        '[1] Assistant (capybara)\n'
                        '[2] Claude-instant-100k (a2_100k)\n'
                        '[3] Claude-2-100k (a2_2)\n'
                        '[4] Claude-instant (a2)\n'
                        '[5] ChatGPT (chinchilla)\n'
                        '[6] ChatGPT-16k (agouti)\n'
                        '[7] GPT-4 (beaver)\n'
                        '[8] GPT-4-32k (vizcacha)\n'
                        '[9] Google-PaLM (acouchy)\n'
                        '[10] Llama-2-7b (llama_2_7b_chat)\n'
                        '[11] Llama-2-13b (llama_2_13b_chat)\n'
                        '[12] Llama-2-70b (llama_2_70b_chat)\n'
                        '[13] Code-Llama-7b (code_llama_7b_instruct)\n'
                        '[14] Code-Llama-13b (code_llama_13b_instruct)\n'
                        '[15] Code-Llama-34b (code_llama_34b_instruct)\n'
                        '[16] Add you own bot\n\n'
                        'Your choice: ')
            if choice.isdigit() and 1 <= int(choice) <= 16:
                if choice == '16':
                    bot = input('Enter the bot name: ')
                else:
                    bot = bots[int(choice)]
                break
            else:
                print('Invalid choice. Please select a valid option.\n')
        return bot
    
    @staticmethod
    def chat_thread(threads):
        while True:
            print('\nChoose a Thread to chat with:\n'
                '\033[38;5;121m[1]\033[0m Create a new Thread')
            for i,k in enumerate(threads):
                i += 2      
                print(f'\033[38;5;121m[{i}]\033[0m Thread {k["chatCode"]}')
                
            choice = input('\nYour choice: ')
            if choice.isdigit() and 1 <= int(choice) <= len(threads)+1:
                if choice == '1':
                    return None
                else:
                    response = threads[int(choice)-2]     
                break
            else:
                print('Invalid choice. Please select a valid option.')        
        return response
    
    @classmethod
    def chat_with_bot(cls, cookie):
        
        while True:
            bot = cls.select_bot()
            try:
                client = PoeApi(cookie=cookie)
                client.get_chat_history(bot=bot)
                break            
            except ValueError:
                print("Invalid bot name. Please try again.\n")  
            
        print(f'The selected bot is: {bot}')
        try:
            threads = client.get_chat_history(bot=bot)[bot]
            thread = cls.chat_thread(threads)
        except KeyError:
            thread = None
        
        if (thread != None):
            chatId = thread["chatId"]
            print(f'The selected thread is: {thread["chatCode"]}')
            client.chat_break(bot, chatId)
            print("Context is now cleared")
        else:
            chatId = None
            
        print('\n🔰 Type !help for more commands 🔰\n')
        
        while True:
            message = input('\033[38;5;121mYou\033[0m : ').lower() 
            if message == '':
                continue
            elif message == '!help':
                print('--------------------------- CMDS ---------------------------\n'
                    '\033[38;5;121m!upload --query_here --url1|url2|url3|...\033[0m : Add attachments\n'
                    '\033[38;5;121m!clear\033[0m : Clear the context\n'
                    '\033[38;5;121m!purge\033[0m : Delete the last 50 messages\n'
                    '\033[38;5;121m!purgeall\033[0m : Delete all the messages\n'
                    '\033[38;5;121m!delete\033[0m : Delete the conversation\n'
                    '\033[38;5;121m!history\033[0m : Show the chat history\n'
                    '\033[38;5;121m!reset\033[0m : Choose a new Bot\n'
                    '\033[38;5;121m!exit\033[0m : Exit the program\n'
                    '\033[38;5;121mPress Q key\033[0m : Stop message generation\n'
                    '------------------------------------------------------------\n') 
            elif message == '!clear':
                client.chat_break(bot, chatId)
                print("Context is now cleared")
            elif message == '!exit':
                break
            elif message == '!reset':
                print('\n')
                Poe.chat_with_bot(cookie)
            elif message == '!purge':
                client.purge_conversation(bot, chatId)
                print("Conversation is now purged")
            elif message == '!purgeall':
                client.purge_all_conversations()
                print("All conversations are now purged\n")
                Poe.chat_with_bot(cookie)
            elif message == '!delete':
                client.delete_chat(bot, chatId)
                print('\n')
                Poe.chat_with_bot(cookie)
            elif message == '!history':
                client.get_chat_history()
            else:
                print(f'\033[38;5;20m{bot}\033[0m : ', end='')
                
                if message == '!suggest 1':
                    message =  chunk["suggestedReplies"][0]
                elif message == '!suggest 2':
                    message =  chunk["suggestedReplies"][1]
                elif message == '!suggest 3':
                    message =  chunk["suggestedReplies"][2]
                    
                if message.startswith('!upload'):
                    try:
                        file_urls = message.split('--')[2].strip().split('|')
                        message = message.split('--')[1].split('--')[0].strip()
                    except:
                        print("Invalid command. Please try again.\n")
                        continue  
                else:
                    file_urls = []
                for chunk in client.send_message(bot, message, chatId, suggest_replies=True, file_path=file_urls):
                    print(chunk["response"], end="", flush=True)
                    if keyboard.is_pressed('q'):
                        client.cancel_message(chunk)
                        print("\nMessage is now cancelled")
                        break 
                print("\n")
                if chunk["suggestedReplies"] != []:
                    for reply in range(len(chunk["suggestedReplies"])):
                        print(f"\033[38;2;255;203;107m[Type !suggest {reply+1}] : {chunk['suggestedReplies'][reply]}\033[0m\n")
                if chatId is None:
                    chatId = chunk["chatId"]