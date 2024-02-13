from poe_api_wrapper import PoeApi, PoeExample
import json, time, threading

client = PoeApi('bdSY2TII4MUoXuDjb9H7oA%3D%3D')
# # for chunk in client.send_message('gemini-pro', 'Nice to meet you. Write a 300 word essay about the moon'):
# #          print(chunk['response'], end='', flush=True)
PoeExample('bdSY2TII4MUoXuDjb9H7oA%3D%3D').chat_with_bot()
# knowledgeSourceIds = {'What is Quora?': [142449], 'Founders of Quora': [142455]}
# print([item for sublist in knowledgeSourceIds.values() for item in sublist])
# client = PoeApi('bdSY2TII4MUoXuDjb9H7oA%3D%3D')
# knowledges = [
#             {
#                 "title": "What is Quora?",
#                 "content": "Quora is a popular online platform that enables users to ask questions on various topics and receive answers from a diverse community. It covers a wide range of subjects, from academic and professional queries to personal experiences and opinions, fostering knowledge-sharing and meaningful discussions among its users worldwide."
#             },
#             {
#                 "title": "Founders of Quora",
#                 "content": "Quora was founded by two individuals, Adam D'Angelo and Charlie Cheever. Adam D'Angelo, who previously served as the Chief Technology Officer (CTO) at Facebook, and Charlie Cheever, a former Facebook employee as well, launched Quora in June 2009. They aimed to create a platform that would enable users to ask questions and receive high-quality answers from knowledgeable individuals. Since its inception, Quora has grown into a widely used question-and-answer platform with a large user base and a diverse range of topics covered."
#             },
#         ]
# source_ids = client.upload_knowledge(text_knowledge=knowledges)
# source_id_2 = client.upload_knowledge(text_knowledge=knowledges)
# client.create_bot(handle="rsdvsvsv", prompt='You are a helpful assitant', base_model='a2', knowledgeSourceIds=source_id_2)
# client.edit_bot(handle="rsdvsvsv", prompt='You are a helpful assitant', base_model='chinchilla', knowledgeSourceIdsToRemove=source_ids)
# print(client.get_botData('bkjDjangXaqsRNOmLlfD'))

# file_urls = ["https://sweet.ua.pt/jpbarraca/course/er-2122/slides/er-1-intro_to_re.pdf", 
#             "https://www.kcl.ac.uk/warstudies/assets/automation-and-artificial-intelligence.pdf"]
# local_path = ["D:\\poe-api-wrapper\\README.md"]
# for chunk in client.send_message('a2', "What is this file about. Explain in detail. Rate the usefulness of the docs on a scale of 10", file_path=local_path):
#     print(chunk["response"], end="", flush=True)
# knowledges = [
#     {
#         "title": "What is Quora?",
#         "content": "Quora is a popular online platform that enables users to ask questions on various topics and receive answers from a diverse community. It covers a wide range of subjects, from academic and professional queries to personal experiences and opinions, fostering knowledge-sharing and meaningful discussions among its users worldwide."
#     },
#     {
#         "title": "Founders of Quora",
#         "content": "Quora was founded by two individuals, Adam D'Angelo and Charlie Cheever. Adam D'Angelo, who previously served as the Chief Technology Officer (CTO) at Facebook, and Charlie Cheever, a former Facebook employee as well, launched Quora in June 2009. They aimed to create a platform that would enable users to ask questions and receive high-quality answers from knowledgeable individuals. Since its inception, Quora has grown into a widely used question-and-answer platform with a large user base and a diverse range of topics covered."
#     },
# ]
# # file_urls = ["https://sweet.ua.pt/jpbarraca/course/er-2122/slides/er-1-intro_to_re.pdf", 
# #             "https://www.kcl.ac.uk/warstudies/assets/automation-and-artificial-intelligence.pdf"]
# source_ids = client.upload_knowledge(text_knowledge=knowledges)
# print(source_ids)
# {'What is Quora?': [86615, 888626], 'Founders of Quora': [86620]}
# only get the values of each list in the value of each key in the dict into a list 
# print(client.get_available_knowledge(botName='agagagagahaagjaa'))
# client.edit_knowledge(knowledgeSourceId=86819, title='What is Quora?', content='Quora is a question-and-answer platform where users can ask questions, provide answers, and engage in discussions on various topics.')
# token  = 'bdSY2TII4MUoXuDjb9H7oA%3D%3D'

# client1 = PoeApi(token)
# client2 = PoeApi(token)

# def t1_send():
#     for chunk in client1.send_message('a2', 'Nice to meet you. Write a 300 word essay about the moon'):
#         print(chunk['response'], end='', flush=True)
    
# def t2_send():
#     for chunk in client1.send_message('chinchilla', 'What day is it today? Write a 300 word essay about the sun'):
#         print(chunk['response'], end='', flush=True)
# t1 = threading.Thread(target=t1_send)
# t2 = threading.Thread(target=t2_send)

# t1.start()
# t2.start()

# t1.join()
# t2.join()
# # file_path = 'log.json'
# # with open(file_path, 'r') as f:
# #             groupData = json.load(f)
# # print(groupData)
import loguru
loguru.logger.disable('poe_api_wrapper')
prev_bot = ""
client.create_group('test', [{'bot': 'StalinJoseph', 'name': 'Stalin'}, {'bot': 'ChurchillGPT', 'name': 'Churchill'}])    
for chunk in client.send_message_to_group('test', autosave=True):
    if chunk['bot'] != prev_bot:
        print(f"\n\033[38;5;121m{chunk['bot']} : \033[0m", end='', flush=True)
        prev_bot = chunk['bot']
    print(chunk['response'], end='', flush=True)
while True: 
    message = str(input('\n\033[38;5;121mYou : \033[0m'))
    prev_bot = ""
    for chunk in client.send_message_to_group('test', message=message, autosave=True):
        if chunk['bot'] != prev_bot:
            print(f"\n\033[38;5;121m{chunk['bot']} : \033[0m", end='', flush=True)
            prev_bot = chunk['bot']
        print(chunk['response'], end='', flush=True)
    print('\n')
    time.sleep(2)

# for chunk in client.send_message('a2', '50 words to desrcribe the almighty sun'):
#     print(chunk['response'], end='', flush=True)
# print('\n')

# # chatCode = chunk['chatCode']

# # for chunk in client.retry_message(chatCode):
# #     print(chunk['response'], end='', flush=True)
# print(len(client.get_available_categories()))
    

