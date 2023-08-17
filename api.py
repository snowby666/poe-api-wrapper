from re import search
from time import sleep
from httpx import Client

"""
This API is modified and maintained by @snowby666
Credit to @ading2210 for the GraphQL queries
"""

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
    GRAPHQL_QUERIES = {
        'ChatFragment': '''
            fragment ChatFragment on Chat {
                __typename
                id
                chatId
                defaultBotNickname
                shouldShowDisclaimer
            }
        ''',
        'MessageFragment': '''
            fragment MessageFragment on Message {
                id
                __typename
                messageId
                text
                linkifiedText
                authorNickname
                state
                vote
                voteReason
                creationTime
                suggestedReplies
            }
        '''
    }

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
        response = self.client.get(self.BASE_URL, headers=self.HEADERS)
        formkey = search(self.FORMKEY_PATTERN, response.text)[1]
        return formkey

    def send_request(self, path: str, data: dict):
        response = self.client.post(f'{self.BASE_URL}/poe_api/{path}', json=data)
        return response.json()

    def get_chatid(self, bot: str='a2'):
        query = f'''
            query ChatViewQuery($bot: String!) {{
                chatOfBot(bot: $bot) {{
                    __typename
                    ...ChatFragment
                }}
            }}
            {self.GRAPHQL_QUERIES['ChatFragment']}
        '''
        variables = {'bot': bot}
        data = {'operationName': 'ChatViewQuery', 'query': query, 'variables': variables}
        response_json = self.send_request('gql_POST', data)
        chat_data = response_json.get('data')
        if chat_data is None:
            raise ValueError('Chat data not found!')
        return chat_data['chatOfBot']['chatId']

    def send_message(self, bot: str, message: str):
        query = f'''
            mutation AddHumanMessageMutation($chatId: BigInt!, $bot: String!, $query: String!, $source: MessageSource, $withChatBreak: Boolean! = false) {{
                messageCreate(
                    chatId: $chatId
                    bot: $bot
                    query: $query
                    source: $source
                    withChatBreak: $withChatBreak
                ) {{
                    __typename
                    message {{
                        __typename
                        ...MessageFragment
                        chat {{
                            __typename
                            id
                            shouldShowDisclaimer
                        }}
                    }}
                    chatBreak {{
                        __typename
                        ...MessageFragment
                    }}
                }}
            }}
            {self.GRAPHQL_QUERIES['MessageFragment']}
        '''
        variables = {'bot': bot, 'chatId': self.get_chatid(bot), 'query': message, 'source': None, 'withChatBreak': False}
        data = {'operationName': 'AddHumanMessageMutation', 'query': query, 'variables': variables}
        self.send_request('gql_POST', data)

    def chat_break(self, bot: str):
        query = f'''
            mutation AddMessageBreakMutation($chatId: BigInt!) {{
                messageBreakCreate(chatId: $chatId) {{
                    __typename
                    message {{
                        __typename
                        ...MessageFragment
                    }}
                }}
            }}
            {self.GRAPHQL_QUERIES['MessageFragment']}
        '''
        variables = {'chatId': self.get_chatid(bot)}
        data = {'operationName': 'AddMessageBreakMutation', 'query': query, 'variables': variables}
        self.send_request('gql_POST', data)
    
    def delete_message(self, message_ids):
        query = f'''
            mutation deleteMessageMutation($messageIds: [BigInt!]!) {{
                messagesDelete(messageIds: $messageIds) {{
                    edgeIds
                }}
            }}
        '''
        variables = {'messageIds': message_ids}
        data = {'operationName': 'DeleteMessageMutation', 'query': query, 'variables': variables}
        self.send_request('gql_POST', data)
    
    def purge_conversation(self, bot: str, count: int=50):
        query = f'''
            query ChatPaginationQuery($bot: String!, $before: String, $last: Int! = {count}) {{
                chatOfBot(bot: $bot) {{
                    id
                    __typename
                    messagesConnection(before: $before, last: $last) {{
                        __typename
                        pageInfo {{
                            __typename
                            hasPreviousPage
                        }}
                        edges {{
                            __typename
                            node {{
                                __typename
                                ...MessageFragment
                            }}
                        }}
                    }}
                }}
            }}
            {self.GRAPHQL_QUERIES['MessageFragment']}
        '''
        variables = {'before': None, 'bot': bot, 'last': count}
        data = {'operationName': 'ChatPaginationQuery', 'query': query, 'variables': variables}
        response_json = self.send_request('gql_POST', data)
        edges = response_json['data']['chatOfBot']['messagesConnection']['edges']
        if edges:
            message_ids = [edge['node']['messageId'] for edge in edges]
            self.delete_message(message_ids)
        else:
            print('No messages found!')
            
    def purge_all_conversations(self):
        query = f'''
            mutation SettingsDeleteAllMessagesButton_deleteUserMessagesMutation_Mutation {{
                deleteUserMessages {{
                    viewer {{
                        uid
                        id
                    }}
                }}
            }}
        '''
        data = {'operationName': 'SettingsDeleteAllMessagesButton_deleteUserMessagesMutation_Mutation', 'query': query}
        self.send_request('gql_POST', data)
        
    def get_latest_message(self, bot: str):
        query = f'''
            query ChatPaginationQuery($bot: String!, $before: String, $last: Int! = 10) {{
                chatOfBot(bot: $bot) {{
                    id
                    __typename
                    messagesConnection(before: $before, last: $last) {{
                        __typename
                        pageInfo {{
                            __typename
                            hasPreviousPage
                        }}
                        edges {{
                            __typename
                            node {{
                                __typename
                                ...MessageFragment
                            }}
                        }}
                    }}
                }}
            }}
            {self.GRAPHQL_QUERIES['MessageFragment']}
        '''
        variables = {'before': None, 'bot': bot, 'last': 1}
        data = {'operationName': 'ChatPaginationQuery', 'query': query, 'variables': variables}

        # author_nickname = ''
        state = 'incomplete'
        while True:
            sleep(0.1)
            response_json = self.send_request('gql_POST', data)
            edges = response_json['data']['chatOfBot']['messagesConnection']['edges']
            if edges:
                latest_message = edges[-1]['node']
                text = latest_message['text']
                state = latest_message['state']
                # author_nickname = latest_message['authorNickname']
                if state == 'complete':
                    break
            else:
                text = 'Fail to get a message. Please try again!'
                break

        return text
    
    def create_bot(self, handle, prompt, display_name=None, base_model="chinchilla", description="", intro_message="", api_key=None, api_bot=False, api_url=None, prompt_public=True, pfp_url=None, linkification=False,  markdown_rendering=True, suggested_replies=False, private=False, temperature=None):
        query = '''
        mutation CreateBotMain_poeBotCreate_Mutation(
            $model: String!
            $displayName: String
            $handle: String!
            $prompt: String!
            $isPromptPublic: Boolean!
            $introduction: String!
            $description: String!
            $profilePictureUrl: String
            $apiUrl: String
            $apiKey: String
            $isApiBot: Boolean
            $hasLinkification: Boolean
            $hasMarkdownRendering: Boolean
            $hasSuggestedReplies: Boolean
            $isPrivateBot: Boolean
            $temperature: Float
        ) {
            poeBotCreate(
            model: $model
            handle: $handle
            displayName: $displayName
            promptPlaintext: $prompt
            isPromptPublic: $isPromptPublic
            introduction: $introduction
            description: $description
            profilePicture: $profilePictureUrl
            apiUrl: $apiUrl
            apiKey: $apiKey
            isApiBot: $isApiBot
            hasLinkification: $hasLinkification
            hasMarkdownRendering: $hasMarkdownRendering
            hasSuggestedReplies: $hasSuggestedReplies
            isPrivateBot: $isPrivateBot
            temperature: $temperature
            ) {
            status
            bot {
                id
                ...BotHeader_bot
            }
            }
        }

        fragment BotHeader_bot on Bot {
            displayName
            isLimitedAccess
            ...BotImage_bot
            ...BotLink_bot
            ...IdAnnotation_node
            ...botHelpers_useViewerCanAccessPrivateBot
            ...botHelpers_useDeletion_bot
        }

        fragment BotImage_bot on Bot {
            displayName
            ...botHelpers_useDeletion_bot
            ...BotImage_useProfileImage_bot
        }

        fragment BotImage_useProfileImage_bot on Bot {
            image {
            __typename
            ... on LocalBotImage {
                localName
            }
            ... on UrlBotImage {
                url
            }
            }
            ...botHelpers_useDeletion_bot
        }

        fragment BotLink_bot on Bot {
            handle
        }

        fragment IdAnnotation_node on Node {
            __isNode: __typename
            id
        }

        fragment botHelpers_useDeletion_bot on Bot {
            deletionState
        }

        fragment botHelpers_useViewerCanAccessPrivateBot on Bot {
            isPrivateBot
            viewerIsCreator
            isSystemBot
        }
        '''
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
        data = {'operationName': 'PoeBotCreateMutation', 'query': query, 'variables': variables}
        result = self.send_request('gql_POST', data)["data"]["poeBotCreate"]
        if result["status"] != "success":
           print(f"Poe returned an error while trying to create a bot: {result['status']}")
        else:
           print("Bot created successfully")
        
    # get_bot logic 
    def edit_bot(self, handle, prompt, bot_id, display_name=None, base_model="chinchilla", description="",
                intro_message="", api_key=None, api_url=None, private=False,
                prompt_public=True, pfp_url=None, linkification=False,
                markdown_rendering=True, suggested_replies=False, temperature=None):     
        query = '''
        mutation EditBotMain_poeBotEdit_Mutation(
        $botId: BigInt!
        $handle: String!
        $displayName: String
        $description: String!
        $introduction: String!
        $isPromptPublic: Boolean!
        $baseBot: String!
        $profilePictureUrl: String
        $prompt: String!
        $apiUrl: String
        $apiKey: String
        $hasLinkification: Boolean
        $hasMarkdownRendering: Boolean
        $hasSuggestedReplies: Boolean
        $isPrivateBot: Boolean
        $temperature: Float
        ) {
        poeBotEdit(botId: $botId, handle: $handle, displayName: $displayName, description: $description, introduction: $introduction, isPromptPublic: $isPromptPublic, model: $baseBot, promptPlaintext: $prompt, profilePicture: $profilePictureUrl, apiUrl: $apiUrl, apiKey: $apiKey, hasLinkification: $hasLinkification, hasMarkdownRendering: $hasMarkdownRendering, hasSuggestedReplies: $hasSuggestedReplies, isPrivateBot: $isPrivateBot, temperature: $temperature) {
            status
            bot {
            handle
            id
            }
        }
        }
        '''
        variables = {
        "baseBot": base_model,
        "botId": bot_id,
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
        
        data = {'operationName': 'PoeBotEditMutation', 'query': query, 'variables': variables}
        result = self.send_request('gql_POST', data)["data"]["poeBotEdit"]
        if result["status"] != "success":
             print(f"Poe returned an error while trying to edit a bot: {result['status']}")
        else:
             print("Bot edited successfully")
        
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

    @classmethod
    def chat_with_bot(cls, cookie):
        
        while True:
            try:
                bot = cls.select_bot()
                client = PoeApi(cookie=cookie)
                client.get_chatid(bot)
                break
            except ValueError:
                print('Invalid bot name. Please try again.\n')
                
        print(f'The selected bot is: {bot}')
        client.chat_break(bot)
        print("Context is now cleared")
        
        while True:
            message = input('\033[38;5;121mYou\033[0m : ').lower() 
            if message == '!clear':
                client.chat_break(bot)
                print("Context is now cleared")
            elif message == '!exit':
                break
            elif message == '!reset':
                print('\n')
                Poe.chat_with_bot(cookie)
            elif message == '!purge':
                client.purge_conversation(bot)
                print("Conversation is now purged")
            elif message == '!purgeall':
                client.purge_all_conversations()
                print("All conversations are now purged")
            else:
                client.send_message(bot, message)
                result = client.get_latest_message(bot)
                print(f'\033[38;5;20m{bot}\033[0m : {result.strip()}')