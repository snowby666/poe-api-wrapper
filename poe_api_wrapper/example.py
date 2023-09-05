from .api import PoeApi
import keyboard

class Poe:
    @staticmethod
    def select_bot(cls, cookie, client):
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
                        '[16] Add you own bot\n\n'
                        'Your choice: ')
            if choice == '0':
                cls.continue_thread(cls, client.get_chat_history(), '!history 1', cookie, client)
                
            elif choice.isdigit() and 1 <= int(choice) <= 16:
                if choice == '16':
                    bot = input('Enter the bot name: ')
                else:
                    bot = bots[int(choice)]
                break
            else:
                print('Invalid choice. Please select a valid option.\n')
        return bot
    
    @staticmethod
    def chat_thread(threads, cookie, client):
        while True:
            print('\nChoose a Thread to chat with:\n'
                '\033[38;5;121m[1]\033[0m Return to Bot selection\n'
                '\033[38;5;121m[2]\033[0m Create a new Thread')
            for i,k in enumerate(threads):
                i += 3    
                print(f'\033[38;5;121m[{i}]\033[0m Thread {k["chatCode"]} | {k["title"]}')
                
            choice = input('\nYour choice: ')
            if choice.isdigit() and 1 <= int(choice) <= len(threads)+2:
                if choice == '1':
                    Poe.chat_with_bot(cookie, new_thread=True, client=client)
                elif choice == '2':
                    return None
                else:
                    response = threads[int(choice)-3]     
                break
            else:
                print('Invalid choice. Please select a valid option.')        
        return response
    
    @staticmethod
    def continue_thread(cls, bots, message, cookie, client):
        
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
                cls.continue_thread(cls, bots, message, cookie, client)
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
                    cls.continue_thread(cls, bots, message, cookie, client)
                    break
                else:
                    print('\n\033[38;2;255;203;107mYou are already on the first page\033[0m\n')
                    continue
            elif valid_page and choice == '>':
                if page < start_cursor // pagination + (start_cursor % pagination > 0):
                    page += 1
                    message = f'!history {page}'
                    cls.continue_thread(cls, bots, message, cookie, client)
                    break
                else:
                    print('\n\033[38;2;255;203;107mYou are already on the last page\033[0m\n')
                    continue
            
            elif choice.isdigit() and 1 <= int(choice) <= len(orders):
                selected_order = orders[int(choice) - 1]
                Poe.chat_with_bot(cookie, new_thread=True, client=client, bot=selected_order[0], chatId=selected_order[1], chatCode=selected_order[2])
                break
            else:
                print('Invalid choice. Please select a valid option.\n')
                continue

    @classmethod
    def chat_with_bot(cls, cookie, new_thread=False, client=None, bot=None, chatId=None, chatCode=None):
        
        while chatCode == None:
            try:
                if not new_thread:
                    client = PoeApi(cookie=cookie)
                bot = cls.select_bot(cls, cookie, client)
                break            
            except:
                print('Invalid cookie. Please try again.\n')
                continue
        
        if (chatCode == None):
            print(f'The selected bot is: {bot}')
            try:
                threads = client.get_chat_history(bot=bot)[bot]
                thread = cls.chat_thread(threads, cookie, client)
            except KeyError:
                thread = None
            
            if (thread != None):
                chatId = thread["chatId"]
                print(f'The selected thread is: {thread["chatCode"]}')
            else:
                chatId = None
        else:
            print(f'Continue chatting with {bot} | {chatCode}')
    
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
                    '\033[38;5;121mPress Q key\033[0m : Stop message generation\n'
                    '------------------------------------------------------------\n') 
            elif message == '!switch':
                try:
                    threads = client.get_chat_history(bot=bot)[bot]
                    thread = cls.chat_thread(threads, cookie, client)
                except KeyError:
                    thread = None
                    print('No threads found. Please type a message to create a new thread first.\n')
                if (thread != None):
                    chatId = thread["chatId"]
                    print(f'The selected thread is: {thread["chatCode"]}')
                else:
                    chatId = None
            elif message == '!clear':
                client.chat_break(bot, chatId)
                print("Context is now cleared")
            elif message == '!exit':
                break
            elif message == '!reset':
                print('\n')
                Poe.chat_with_bot(cookie, new_thread=True, client=client)
            elif message == '!purge':
                client.purge_conversation(bot, chatId)
                print("Conversation is now purged")
            elif message == '!purgeall':
                client.purge_all_conversations()
                print("All conversations are now purged\n")
                Poe.chat_with_bot(cookie, new_thread=True, client=client)
            elif message == '!delete':
                client.delete_chat(bot, chatId)
                print('\n')
                Poe.chat_with_bot(cookie, new_thread=True, client=client)
            elif message.startswith('!history'):
                bots = client.get_chat_history()
                if not bots:
                    print("No history found. Please type a message to create a new thread first.\n")
                    continue
                else:
                    cls.continue_thread(cls, bots, message, cookie, client)
            elif message == '!load':
                if chatId is None:
                    print("Please type a message to create a new thread first.\n")
                    continue
                previous_messages = client.get_previous_messages(bot=bot, chatId=chatId, get_all=True)
                for message in previous_messages:
                    if message['author'] == 'human':
                        print(f'\033[38;5;121mYou\033[0m : {message["text"]}\n')
                    elif message['author'] == 'chat_break':
                        print('--------------------------------------- Context cleared ---------------------------------------\n')
                    else:
                        print(f'\033[38;5;20m{bot}\033[0m : {message["text"]}\n')
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