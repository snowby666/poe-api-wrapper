from .api import PoeApi

class PoeExample:
    def __init__(self, cookie):
        self.cookie = cookie
        self.client = PoeApi(cookie=self.cookie)
        
    def select_bot(self):
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
            15: 'code_llama_34b_instruct',
            16: 'upstage_solar_0_70b_16bit'
        }
        while True:
            choice = input('Who do you want to talk to?\n'
                        '[0] See the chat history\n'
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
                        '[16] Solar-0-70b (upstage_solar_0_70b_16bit)\n'
                        '[17] Add you own bot\n\n'
                        'Your choice: ')
            if choice == '0':
                data = self.client.get_chat_history(interval=500)
                self.continue_thread(data['data'], '!history 1')
                
            elif choice.isdigit() and 1 <= int(choice) <= 17:
                if choice == '17':
                    bot = input('Enter the bot name: ')
                else:
                    bot = bots[int(choice)]
                break
            else:
                print('Invalid choice. Please select a valid option.\n')
        return bot
    
    def chat_thread(self, threads, cursor, page=0):
        if cursor == None:
            has_next_page = False
            pagination = False
        else:
            has_next_page = True
            pagination = True  
        while True:
            print('\nChoose a Thread to chat with:\n'
                '\033[38;5;121m[0]\033[0m Return to Bot selection\n'
                '\033[38;5;121m[1]\033[0m Create a new Thread')
            for i,k in enumerate(threads[page]):
                i += 2  
                print(f'\033[38;5;121m[{i}]\033[0m Thread {k["chatCode"]} | {k["title"]}')
            if pagination:
                if page+1 == len(threads):
                    print(
                        '\n'
                        '\033[38;5;121m[>]\033[0m : Load 20 more threads\n'
                        '\033[38;5;121m[<]\033[0m : Previous page\n'
                    )
                else:
                    print(
                        '\n'
                        '\033[38;5;121m[>]\033[0m : Next page\n'
                        '\033[38;5;121m[<]\033[0m : Previous page\n'
                    )
                
                print(f"You are on page {page+1} of {len(threads)}")
                
            choice = input('\nYour choice: ')
            if choice.isdigit() and 0 <= int(choice) <= len(threads[page])+1:
                if choice == '0':
                    self.chat_with_bot()
                elif choice == '1':
                    return None
                else:
                    response = threads[page][int(choice)-2]     
                break
            elif pagination and choice == '<':
                has_next_page = True
                if page > 0:
                    page -= 1
                    continue
                else:
                    print('\n\033[38;2;255;203;107mYou are already on the first page\033[0m')
                    continue
            elif pagination and choice == '>':
                if has_next_page:
                    page += 1
                    new_data = self.client.get_chat_history(bot=self.bot, count=20, cursor=cursor)
                    if new_data['data'][self.bot] == [] or new_data['cursor'] == None:
                        has_next_page = False
                    if page == len(threads):
                        threads.append(new_data['data'][self.bot])
                    cursor = new_data['cursor']
                    continue
                else:
                    print('\n\033[38;2;255;203;107mYou are already on the last page\033[0m')
                    continue
            else:
                print('Invalid choice. Please select a valid option.')        
        return response
    
    def continue_thread(self, bots, message):
        if len(message.split(' ')) == 2 and (message.split(' ')[1].isdigit() or (message.split(' ')[1].startswith('-') and message.split(' ')[1][1:].isdigit())):
            page = int(message.split(' ')[1])
            if message.split(' ')[1].startswith('-'):
                page = 1
                print('\n\033[38;2;255;203;107mPage number is out of range. Redirecting to the first page...\033[0m\n')
            
            valid_page = True
            pagination = 9
            start_cursor = 0
            new_bots = {}
            
            for bot, bot_chats in bots.items():
                for chat in bot_chats:
                    start_cursor += 1
                    
                    if start_cursor > (page - 1) * pagination and start_cursor <= pagination * page:
                        new_bots.setdefault(bot, []).append(chat)
            
            if page > start_cursor // pagination + (start_cursor % pagination > 0):
                page = start_cursor // pagination + (start_cursor % pagination > 0)
                message = f'!history {page}'
                print('\n\033[38;2;255;203;107mPage number is out of range. Redirecting to the last page...\033[0m\n')
                self.continue_thread(bots, message)
                return
        else:
            new_bots = bots
            valid_page = False
            
        print('-' * 38 + ' \033[38;5;121mChat History\033[0m ' + '-' * 38)
        print(' \033[38;5;121mNo.\033[0m | \033[38;5;121mChat ID\033[0m  |     \033[38;5;121mChat Code\033[0m       |           \033[38;5;121mBot Name\033[0m             |    \033[38;5;121mChat Title\033[0m')
        print('-' * 90)
        
        orders = {}
        for index, (bot, bot_chats) in enumerate(new_bots.items()):
            for chat in bot_chats:
                orders[len(orders)] = [bot, chat["chatId"], chat["chatCode"], chat["title"]]
                print(f' [{len(orders)}] | {chat["chatId"]} | {chat["chatCode"]} | {bot:<30} | {chat["title"]}')
        
        print('-' * 90)
        
        while True:
            if valid_page:
                print(
                    '[0] : Return\n'
                    '[>] : Next page\n'
                    '[<] : Previous page\n'
                )
                print(f'You are on page {page} of {start_cursor // pagination + (start_cursor % pagination > 0)}')
            else:
                print('[0] : Return to current thread\n')
            
            choice = input('Choose a chat to continue: ')
            
            if choice == '0':
                break
            elif valid_page and choice == '<':
                if page > 1:
                    page -= 1
                    message = f'!history {page}'
                    self.continue_thread(bots, message)
                    break
                else:
                    print('\n\033[38;2;255;203;107mYou are already on the first page\033[0m\n')
                    continue
            elif valid_page and choice == '>':
                if page < start_cursor // pagination + (start_cursor % pagination > 0):
                    page += 1
                    message = f'!history {page}'
                    self.continue_thread(bots, message)
                    break
                else:
                    print('\n\033[38;2;255;203;107mYou are already on the last page\033[0m\n')
                    continue
            
            elif choice.isdigit() and 1 <= int(choice) <= len(orders):
                selected_order = orders[int(choice) - 1]
                self.chat_with_bot(bot=selected_order[0], chatId=selected_order[1], chatCode=selected_order[2])
                break
            else:
                print('Invalid choice. Please select a valid option.\n')
                continue

    def chat_with_bot(self, bot=None, chatId=None, chatCode=None):
        
        self.bot = bot
        self.chatId = chatId
        self.chatCode = chatCode
        
        while self.chatCode == None:
            try:
                self.bot = self.select_bot()
                break            
            except:
                print('Invalid cookie. Please try again.\n')
                continue
        
        if (self.chatCode == None):
            print(f'The selected bot is: {self.bot}')
            try:
                data = self.client.get_chat_history(bot=self.bot, count=20)
                threads = [data['data'][self.bot]]
                cursor = data['cursor']
                thread = self.chat_thread(threads, cursor)
            except KeyError:
                thread = None
            
            if (thread != None):
                self.chatId = thread["chatId"]
                print(f'The selected thread is: {thread["chatCode"]}')
            else:
                self.chatId = None
        else:
            print(f'Continue chatting with {self.bot} | {self.chatCode}')
    
        print('\n🔰 Type \033[38;5;121m!help\033[0m for more commands 🔰\n')
        
        while True:
            message = input('\033[38;5;121mYou\033[0m : ').lower() 
            if message == '':
                continue
            elif message == '!help':
                print('--------------------------- \033[38;5;121mCMDS\033[0m ---------------------------\n'
                    '\033[38;5;121m!upload --query_here --url1|url2|url3|...\033[0m : Add attachments\n'
                    '\033[38;5;121m!history page_number\033[0m : Show specific page of chat history\n'
                    '\033[38;5;121m!history\033[0m : Show all chat history\n'
                    '\033[38;5;121m!switch\033[0m : Switch to another Thread\n'
                    '\033[38;5;121m!load\033[0m : Load previous messages\n'
                    '\033[38;5;121m!clear\033[0m : Clear the context\n'
                    '\033[38;5;121m!purge\033[0m : Delete the last 50 messages\n'
                    '\033[38;5;121m!purgeall\033[0m : Delete all the messages\n'
                    '\033[38;5;121m!delete\033[0m : Delete the conversation\n'
                    '\033[38;5;121m!reset\033[0m : Choose a new Bot\n'
                    '\033[38;5;121m!exit\033[0m : Exit the program\n'
                    '------------------------------------------------------------\n') 
            elif message == '!switch':
                try:
                    data = self.client.get_chat_history(bot=self.bot, count=20)
                    threads = [data['data'][self.bot]]
                    cursor = data['cursor']
                    thread = self.chat_thread(threads, cursor)
                except KeyError:
                    thread = None
                    print('No threads found. Please type a message to create a new thread first.\n')
                if (thread != None):
                    self.chatId = thread["chatId"]
                    print(f'The selected thread is: {thread["chatCode"]}')
                else:
                    self.chatId = None
            elif message == '!clear':
                self.client.chat_break(self.bot, self.chatId)
                print("Context is now cleared")
            elif message == '!exit':
                break
            elif message == '!reset':
                print('\n')
                self.chat_with_bot()
            elif message == '!purge':
                self.client.purge_conversation(self.bot, self.chatId)
                print("Conversation is now purged")
            elif message == '!purgeall':
                self.client.purge_all_conversations()
                print("All conversations are now purged\n")
                self.chat_with_bot()
            elif message == '!delete':
                self.client.delete_chat(self.bot, self.chatId)
                print('\n')
                self.chat_with_bot()
            elif message.startswith('!history'):
                chat_data = self.client.get_chat_history(interval=500)
                bots = chat_data['data']
                # cursor = chat_data['cursor']
                if not bots:
                    print("No history found. Please type a message to create a new thread first.\n")
                    continue
                else:
                    self.continue_thread(bots, message)
            elif message == '!load':
                if self.chatId is None:
                    print("Please type a message to create a new thread first.\n")
                    continue
                previous_messages = self.client.get_previous_messages(bot=self.bot, chatId=self.chatId, get_all=True)
                for message in previous_messages:
                    if message['author'] == 'human':
                        print(f'\033[38;5;121mYou\033[0m : {message["text"]}\n')
                    elif message['author'] == 'chat_break':
                        print('--------------------------------------- Context cleared ---------------------------------------\n')
                    else:
                        print(f'\033[38;5;20m{self.bot}\033[0m : {message["text"]}\n')
            else:
                print(f'\033[38;5;20m{self.bot}\033[0m : ', end='')
                
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
                for chunk in self.client.send_message(self.bot, message, self.chatId, suggest_replies=True, file_path=file_urls):
                    print(chunk["response"], end="", flush=True)
                print("\n")
                if chunk["suggestedReplies"] != []:
                    for reply in range(len(chunk["suggestedReplies"])):
                        print(f"\033[38;2;255;203;107m[Type !suggest {reply+1}] : {chunk['suggestedReplies'][reply]}\033[0m\n")
                if self.chatId is None:
                    self.chatId = chunk["chatId"]