from re import search
from time import sleep
from httpx import Client
import secrets, string
from .queries import generate_payload
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
}

def bot_map(bot):
    if bot in BOTS_LIST:
        return BOTS_LIST[bot]
    return bot.lower().replace(' ', '')
    
def generate_nonce(length:int=16):
      return "".join(secrets.choice(string.ascii_letters + string.digits) for i in range(length))
  
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

    def __init__(self, cookie: str):
        self.client = Client(timeout=180)
        self.client.cookies.set('m-b', cookie)
        self.client.headers.update({
            **self.HEADERS,
            'Quora-Formkey': self.get_formkey(),
        })
   
    def __del__(self):
        self.client.close()

    def get_formkey(self):
        response = self.client.get(self.BASE_URL, headers=self.HEADERS, follow_redirects=True)
        formkey = search(self.FORMKEY_PATTERN, response.text)[1]
        return formkey
    
    def send_request(self, path: str, query_name:str="", variables:dict={}):
        payload = generate_payload(query_name, variables)
        response = self.client.post(f'{self.BASE_URL}/poe_api/{path}', data=payload, headers={'Content-Type': 'application/x-www-form-urlencoded'})
        return response.json()
    
    def get_available_bots(self, count: int=25, get_all: bool=False):
        self.bots = {}
        if not (get_all or count):
            raise TypeError(
                "Please provide at least one of the following parameters: get_all=<bool>, count=<int>"
            )
        response = self.send_request('gql_POST',"AvailableBotsSelectorModalPaginationQuery", {}) 
        bots = [
            each["node"]
            for each in response["data"]["viewer"]["availableBotsConnection"]["edges"]
            if each["node"]["deletionState"] == "not_deleted"
        ]
        cursor = response["data"]["viewer"]["availableBotsConnection"]["pageInfo"][
            "endCursor"
        ]
        if len(bots) >= count and not get_all:
            self.bots.update({bot["handle"]: {"bot": bot} for bot in bots})
            return self.bots
        while len(bots) < count or get_all:
            response = self.send_request("gql_POST", "AvailableBotsSelectorModalPaginationQuery", {"cursor": cursor})
            new_bots = [
                each["node"]
                for each in response["data"]["viewer"]["availableBotsConnection"][
                    "edges"
                ]
                if each["node"]["deletionState"] == "not_deleted"
            ]
            cursor = response["data"]["viewer"]["availableBotsConnection"]["pageInfo"][
                "endCursor"
            ]
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
     
    def get_chat_history(self, bot:str=None, handle:str="", useBot:bool=False): 
        variables = {'handle': handle, 'useBot': useBot}
        response_json = self.send_request('gql_POST', 'ChatsHistoryPageQuery', variables)
        edges = response_json['data']['chats']['edges']
        
        chat_bots = {}
        
        if bot == None:
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
            for edge in edges:
                chat = edge['node']
                try:
                    model = bot_map(chat["defaultBotObject"]["displayName"])
                    if model == bot:
                        if model in chat_bots:
                            chat_bots[model].append({"chatId": chat["chatId"],"chatCode": chat["chatCode"], "id": chat["id"]})
                        else:
                            chat_bots[model] = [{"chatId": chat["chatId"], "chatCode": chat["chatCode"], "id": chat["id"]}]
                except:
                    pass           
        return chat_bots
    
    def create_new_chat(self, bot: str="a2", message: str=""):
        variables = {"bot":bot,"query":message,"source":{"sourceType":"chat_input","chatInputMetadata":{"useVoiceRecord":False,"newChatContext":"chat_settings_new_chat_button"}},"sdid":"","attachments":[]}
        response_json = self.send_request('gql_POST', 'ChatHelpersSendNewChatMessageMutation', variables)
        chatCode = response_json['data']['messageEdgeCreate']['chat']['chatCode']
        print(f'New Thread created | {chatCode}')
        return chatCode

    def send_message(self, bot: str, message: str, chatId: int=None, chatCode: str=None):
        if chatId is None:
            chatCode = self.create_new_chat(bot, message)
        else:
            variables = {'bot': bot, 'chatId': chatId, 'query': message, 'source': { "sourceType": "chat_input", "chatInputMetadata": {"useVoiceRecord": False}}, 'withChatBreak': False, "clientNonce": generate_nonce(), 'sdid':"", 'attachments': []}
            self.send_request('gql_POST', 'SendMessageMutation', variables)
            if chatCode is None:
                chat_data = self.get_chat_history(bot=bot)[bot]
                for chat in chat_data:
                    if chat['chatId'] == chatId:
                        chatCode = chat['chatCode']
                        break
        return self.get_latest_message(chatCode)
        
    def chat_break(self, bot: str, chatId: int=None, chatCode: str=None):
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
        
    def get_latest_message(self, chatCode: str=""):
        variables = {'chatCode': chatCode}
        state = 'incomplete'
        while True:
            sleep(0.1)
            response_json = self.send_request('gql_POST','ChatPageQuery', variables)
            edges = response_json['data']['chatOfCode']['messagesConnection']['edges']
            if edges:
                latest_message = edges[-1]['node']
                text = latest_message['text']
                state = latest_message['state']
                if state == 'complete':
                    break
            else:
                text = 'Fail to get a message. Please try again!'
                break
        return text
    
    def delete_chat(self, bot: str, chatId: any=None, chatCode: any=None, del_all: bool=False):
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
        }
        while True:
            choice = input('Who do you want to talk to?\n'
                        '1. Assistant (capybara)\n'
                        '2. Claude-instant-100k (a2_100k)\n'
                        '3. Claude-2-100k (a2_2)\n'
                        '4. Claude-instant (a2)\n'
                        '5. ChatGPT (chinchilla)\n'
                        '6. ChatGPT-16k (agouti)\n'
                        '7. GPT-4 (beaver)\n'
                        '8. GPT-4-32k (vizcacha)\n'
                        '9. Google-PaLM (acouchy)\n'
                        '10. Llama-2-7b (llama_2_7b_chat)\n'
                        '11. Llama-2-13b (llama_2_13b_chat)\n'
                        '12. Llama-2-70b (llama_2_70b_chat)\n'
                        '13. Add you own bot\n\n'
                        'Your choice: ')
            if choice.isdigit() and 1 <= int(choice) <= 13:
                if choice == '13':
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
                '\033[38;5;121m1\033[0m. Create a new Thread')
            for i,k in enumerate(threads):
                i += 2      
                print(f'\033[38;5;121m{i}\033[0m. Thread {k["chatCode"]}')
                
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
        
        while True:
            message = input('\033[38;5;121mYou\033[0m : ').lower() 
            if message == '!clear':
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
                print("All conversations are now purged")
            elif message == '!delete':
                client.delete_chat(bot, chatId)
            elif message == '!history':
                client.get_chat_history()
            else:
                result = client.send_message(bot, message, chatId)
                if chatId is None:
                    chatId = client.get_chat_history(bot=bot)[bot][0]['chatId']
                print(f'\033[38;5;20m{bot}\033[0m : {result.strip()}')