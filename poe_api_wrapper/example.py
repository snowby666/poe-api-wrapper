from .api import PoeApi
from os import _exit
from rich.markdown import Markdown
from rich.console import Console
from rich.live import Live

BANNER = """ 
\033[38;2;140;84;228m
$$$$$$$\                             $$$$$$\  $$$$$$$\ $$$$$$\ 
$$  __$$\                           $$  __$$\ $$  __$$\\ _$$  _|
$$ |  $$ | $$$$$$\   $$$$$$\        $$ /  $$ |$$ |  $$ | $$ |  
$$$$$$$  |$$  __$$\ $$  __$$\       $$$$$$$$ |$$$$$$$  | $$ |  
$$  ____/ $$ /  $$ |$$$$$$$$ |      $$  __$$ |$$  ____/  $$ |  
$$ |      $$ |  $$ |$$   ____|      $$ |  $$ |$$ |       $$ |  
$$ |      \$$$$$$  |\$$$$$$$\       $$ |  $$ |$$ |     $$$$$$\ 
\__|       \______/  \_______|      \__|  \__|\__|     \______|
\033[0m                                                                  
""" 
class PoeExample:
    def __init__(self, cookie):
        self.cookie = cookie
        self.client = PoeApi(cookie=self.cookie)
        
    def select_bot(self):
        bots = {}
        while True:
            print(BANNER)
            print(
                "This is an example of how to use the PoeApi wrapper.\n\n"
                "[0] : Exit the program\n"
                "[1] : Add a bot directly\n"
                "[2] : Search for a bot by category\n"
                "[3] : Search for a bot by query\n"
                "[4] : Search for a user's bots\n"
                "[5] : Search for users and their bots\n"
                "[6] : See the chat history\n"
            )
            
            selection = input('Your choice: ')
            
            if selection == '0':
                return 'exit'
            elif selection == '1':
                bot = input('Enter the bot name: ')
                return bot
            elif selection == '2':
                self.categories = self.client.get_available_categories()
                print('\nAvailable categories:\n')
                for category in self.categories:
                    print(f'[{self.categories.index(category)+1}] {category}')
                while True:
                    cateChoice = input('\nYour choice: ')
                    if cateChoice.isdigit() and 1 <= int(cateChoice) <= len(self.categories):
                        category = self.categories[int(cateChoice)-1]
                        break
                    else:
                        print('Invalid choice. Please select a valid option.\n')
                        continue
                    
                print('\nEnter the number of bots you want to explore or type \033[38;5;121mall\033[0m to explore all the bots in this category.\n')
                
                while True:
                    exploreChoice = input('Your choice: ')
                    if exploreChoice.isdigit() and int(exploreChoice) > 0:
                        available_bots = self.client.explore(categoryName=category, count=int(exploreChoice))
                        break
                    elif exploreChoice == 'all':
                        available_bots = self.client.explore(categoryName=category, explore_all=True)
                        break
                    else:
                        print('Invalid choice. Please select a valid option.\n')
                        continue
                    
                if available_bots == []:
                    print('No bots found. Please try again.\n')
                    continue         
                break
            elif selection == '3': 
                while True:
                    query = input('\nEnter the search query: ')
                    if query == '':
                        print('Invalid query. Please try again.\n')
                        continue
                    else:
                        while True:
                            exploreChoice = input('\nEnter the number of bots you want to explore or type \033[38;5;121mall\033[0m to explore all the bots.\nYour choice: ')
                            if exploreChoice.isdigit() and int(exploreChoice) > 0:
                                available_bots = self.client.explore(search=query, count=int(exploreChoice))
                                break
                            elif exploreChoice == 'all':
                                available_bots = self.client.explore(search=query, explore_all=True)
                                break
                            else:
                                print('Invalid choice. Please select a valid option.\n')
                                continue
                        break
                    
                if available_bots == []:
                    print('No bots found. Please try again.\n')
                    continue
                break
            elif selection == '4':
                while True:
                    username = input('\nEnter the username: ')
                    if username == '':
                        print('Invalid username. Please try again.\n')
                        continue
                    else:
                        try:
                            available_bots = self.client.get_user_bots(user=username)
                        except:
                            print('User does not exist. Please try again.\n')
                            continue
                        break
                    
                if available_bots == []:
                    print('No bots found. Please try again.\n')
                    continue
                break
            elif selection == '5':
                while True:
                    user_query = input('\nEnter the user query: ')
                    if user_query == '':
                        print('Invalid user query. Please try again.\n')
                        continue
                    else:
                        while True:
                            userChoice = input('\nEnter the number of users you want to explore or type \033[38;5;121mall\033[0m to explore all the users.\nYour choice: ')
                            if userChoice.isdigit() and int(userChoice) > 0:
                                people = self.client.explore(search=user_query, entity_type='user', count=int(userChoice))
                                break
                            elif userChoice == 'all':
                                people = self.client.explore(search=user_query, entity_type='user', explore_all=True)
                                break
                            else:
                                print('Invalid choice. Please select a valid option.\n')
                                continue

                        if people == []:
                            print('No users found. Please try again.\n')
                            continue
                        break
                    
                while True:
                    print('\nAvailable users:\n')
                    for person in range(len(people)):
                        print(f'[{person+1}] {people[person]}')
                    user_choice = input('\nChoose a user: ')
                    if user_choice.isdigit() and 1 <= int(user_choice) <= len(people):
                        user = people[int(user_choice)-1]
                        available_bots = self.client.get_user_bots(user=user)
                        break
                    else:
                        print('Invalid choice. Please select a valid option.\n')
                        continue
                    
                if available_bots == []:
                    print('No bots found. Please try again.\n')
                    continue
                break
            elif selection == '6':
                data = self.client.get_chat_history(interval=500)
                self.continue_thread(data['data'], '!history 1')
                break
            else:
                print('Invalid choice. Please select a valid option.\n')
                continue

        for bot in range(len(available_bots)):
            bots[bot+1] = available_bots[bot]
        
        while True:
            print('Who do you want to talk to?\n')
            for index, bot in bots.items():
                print(f'[{index}] {bot}')       
            choice = input('\nYour choice: ')
            if choice.isdigit() and 1 <= int(choice) <= len(bots):
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
            print('\nChoose a Thread to chat with:\n\n'
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
                    if new_data['data'][self.bot.lower().replace(' ', '')] == [] or new_data['cursor'] == None:
                        has_next_page = False
                    if page == len(threads):
                        threads.append(new_data['data'][self.bot.lower().replace(' ', '')])
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
        print(' \033[38;5;121mNo.\033[0m|  \033[38;5;121mChat ID\033[0m   |     \033[38;5;121mChat Code\033[0m       |           \033[38;5;121mBot Name\033[0m             |    \033[38;5;121mChat Title\033[0m')
        print('-' * 90)
        
        orders = {}
        for index, (bot, bot_chats) in enumerate(new_bots.items()):
            for chat in bot_chats:
                orders[len(orders)] = [bot, chat["chatId"], chat["chatCode"], chat["title"]]
                print(f'[{len(orders)}] | {chat["chatId"]}'+ (11-len(str(chat["chatId"])))*' ' +f'| {chat["chatCode"]} | {bot:<30} | {chat["title"]}')
        
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
                if self.bot == 'exit':
                    print('Poe Example is now closed.')
                    _exit(0)
                break            
            except:
                print('Invalid cookie. Please try again.\n')
                continue
        
        if (self.chatCode == None):
            print(f'The selected bot is: {self.bot}')
            try:
                data = self.client.get_chat_history(bot=self.bot, count=20)
                threads = [data['data'][self.bot.lower().replace(' ', '')]]
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
            console_ = Console()
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
                    '\033[38;5;121m!purgeall\033[0m : Delete all conversations (be careful)\n'
                    '\033[38;5;121m!delete\033[0m : Delete the conversation\n'
                    '\033[38;5;121m!reset\033[0m : Choose a new Bot\n'
                    '\033[38;5;121m!exit\033[0m : Exit the program\n'
                    '------------------------------------------------------------\n') 
            elif message == '!switch':
                try:
                    data = self.client.get_chat_history(bot=self.bot, count=20)
                    threads = [data['data'][self.bot.lower().replace(' ', '')]]
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
                print('Poe Example is now closed.')
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
                        with Live(
                            console=console_,
                            refresh_per_second=16,
                            vertical_overflow='ellipsis',
                        ) as live:
                            live.update(
                                Markdown(f'\033[38;5;20m{self.bot}\033[0m : {message["text"]}', code_theme='monokai')
                            ) if message['contentType']=="text_markdown" else ''
                print("\n")
            else:
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
                with Live(
                        console=console_,
                        refresh_per_second=16,
                        vertical_overflow='ellipsis',
                    ) as live:
                        for chunk in self.client.send_message(self.bot, message, self.chatId, suggest_replies=True, file_path=file_urls):
                            content_type:str = chunk.get('contentType',"text_markdown")
                            live.update(
                                Markdown(f'\033[38;5;20m{self.bot}\033[0m : {chunk["text"]}', code_theme='monokai') if content_type=="text_markdown" else ''
                            )
                print("\n")
                if chunk["suggestedReplies"] != []:
                    for reply in range(len(chunk["suggestedReplies"])):
                        print(f"\033[38;2;255;203;107m[Type !suggest {reply+1}] : {chunk['suggestedReplies'][reply]}\033[0m\n")
                if self.chatId is None:
                    self.chatId = chunk["chatId"]