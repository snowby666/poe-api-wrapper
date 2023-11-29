from poe_api_wrapper import PoeApi
import unittest, random, string, loguru

loguru.logger.disable('poe_api_wrapper')

TOKEN = input("Enter your token: ")

def testObjectGenerator(length):
       return ''.join(random.choice(string.ascii_letters) for _ in range(length))
   

class PoeApiTest(unittest.TestCase):
    
    @classmethod
    def setUpClass(cls):
        cls.botName = testObjectGenerator(20)
        cls.botName2 = testObjectGenerator(20)
        print("Initializing tests")
                
    def test_get_subscription_info(self):
        client = PoeApi(cookie=TOKEN)
        client.get_channel_settings()
        client.subscribe()
        
    def test_get_available_bots(self):
        client = PoeApi(cookie=TOKEN)
        client.get_available_bots()
        
    def test_get_available_categories(self):
        client = PoeApi(cookie=TOKEN)
        client.get_available_categories()
        
    def test_get_user_bots(self):
        client = PoeApi(cookie=TOKEN)
        client.get_user_bots(user='poe')
        
    def test_explore(self):
        client = PoeApi(cookie=TOKEN)
        client.explore(count=10)
        client.explore(search="Midjourney", count=30)
        client.explore(categoryName="Popular", count=30)
        client.explore(search="Poe", entity_type='user', count=30)
        
    def test_get_chat_history(self):
        client = PoeApi(cookie=TOKEN)
        client.get_chat_history(count=200)
    
    def test_send_message(self):
        client = PoeApi(cookie=TOKEN)
        for _ in client.send_message(bot='a2', message='Nice to meet you. Write a 100 word essay about the moon', suggest_replies=True):
            pass
        
    def test_upload_file(self):
        client = PoeApi(cookie=TOKEN)
        file_urls = ["https://sweet.ua.pt/jpbarraca/course/er-2122/slides/er-1-intro_to_re.pdf", 
                    "https://www.kcl.ac.uk/warstudies/assets/automation-and-artificial-intelligence.pdf"]
        for _ in client.send_message(bot="a2", message="Compare 2 files and describe them in 100 words", file_path=file_urls):
            pass
    
    def test_get_threadData(self):
        client = PoeApi(cookie=TOKEN)
        client.get_threadData(bot="a2")
    
    def test_cancel_message(self):
        client = PoeApi(cookie=TOKEN)
        i = 0
        for chunk in client.send_message(bot="a2", message="What is the meaning of life (100 words)?"):
            i += 1
            if i >= 2:
                client.cancel_message(chunk)
                break 
    def test_retry_message(self):
        client = PoeApi(cookie=TOKEN)
        for _ in client.send_message(bot="capybara", message="Explain Quantaum Mechanics in 50 words"):
            pass
        chatCode = client.get_chat_history("capybara")['data']['capybara'][0]['chatCode']
        for _ in client.retry_message(chatCode=chatCode):
            pass
    
    def test_clear_conversation(self):
        client = PoeApi(cookie=TOKEN)
        chatCode = client.get_chat_history("a2")['data']['a2'][0]['chatCode']
        client.chat_break(bot="a2", chatCode=chatCode)

    def test_purge_conversation(self):
        client = PoeApi(cookie=TOKEN)
        chatCode = client.get_chat_history("a2")['data']['a2'][0]['chatCode']
        client.purge_conversation(bot="a2", chatCode=chatCode)
        
    def test_get_previous_messages(self):
        client = PoeApi(cookie=TOKEN)
        chatCode = client.get_chat_history("a2")['data']['a2'][0]['chatCode']
        client.get_previous_messages('a2', chatCode=chatCode, count=2)
    
    def test_upload_knowledge(self):
        client = PoeApi(cookie=TOKEN)
        
        # Web urls
        file_urls = ["https://sweet.ua.pt/jpbarraca/course/er-2122/slides/er-1-intro_to_re.pdf", 
            "https://www.kcl.ac.uk/warstudies/assets/automation-and-artificial-intelligence.pdf"]
        client.upload_knowledge(file_path=file_urls)
        
        # Text knowledge
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
        client.upload_knowledge(text_knowledge=knowledges)
        
    def test_edit_knowledge(self):
        client = PoeApi(cookie=TOKEN)
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
        client.edit_knowledge(knowledgeSourceId=source_ids['What is Quora?'][-1], title='What is Quora?', content='Quora is a question-and-answer platform where users can ask questions, provide answers, and engage in discussions on various topics.')

    def test_create_bot(self):
        client = PoeApi(cookie=TOKEN)
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
        client.create_bot(handle=self.botName, prompt='You are a helpful assitant', base_model='a2', knowledgeSourceIds=source_ids)
        
    def test_get_available_knowledge(self):
        client = PoeApi(cookie=TOKEN)
        client.get_available_knowledge(botName=self.botName)
        
    def test_delete_bot(self):
        client = PoeApi(cookie=TOKEN)
        client.delete_bot(handle=self.botName)
        
    def test_edit_bot(self):
        client = PoeApi(cookie=TOKEN)
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
        client.create_bot(handle=self.botName2, prompt='You are a helpful assitant', base_model='a2', knowledgeSourceIds=source_ids)
        client.edit_bot(handle=self.botName2, prompt='You are a helpful assitant', base_model='chinchilla', knowledgeSourceIdsToRemove=source_ids)
        client.delete_bot(handle=self.botName2)
        
    def test_shareCode(self):
        client = PoeApi(cookie=TOKEN)
        chatCode = client.get_chat_history("capybara")['data']['capybara'][0]['chatCode']
        shareCode = client.share_chat("capybara", chatCode=chatCode, count=2)
        client.import_chat("capybara", shareCode=shareCode)
        
unittest.main(verbosity=2)