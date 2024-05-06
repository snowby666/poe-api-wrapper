import os, string, secrets
from urllib.parse import urlparse
import cloudscraper

BASE_URL = 'https://www.quora.com'
HEADERS = {
    'Host': 'www.quora.com',
    'Accept': '*/*',
    'apollographql-client-version': '1.1.6-65',
    'Accept-Language': 'en-US,en;q=0.9',
    'User-Agent': 'Poe 1.1.6 rv:65 env:prod (iPhone14,2; iOS 16.2; en_US)',
    'apollographql-client-name': 'com.quora.app.Experts-apollo-ios',
    'Connection': 'keep-alive',
    'Content-Type': 'application/json'  
}

SubscriptionsMutation = {
    "subscriptions": [
                        {
                            "subscriptionName":"messageAdded",
                            "query":None,
                            "queryHash":"b739399cc69af7bb45a16c889a6ca6c24d3456337fde805ee7f480e6195a3eb7"
                        },
                        {
                            "subscriptionName":"messageCancelled",
                            "query":None,
                            "queryHash":"14647e90e5960ec81fa83ae53d270462c3743199fbb6c4f26f40f4c83116d2ff"
                        },
                        {
                            "subscriptionName":"messageDeleted",
                            "query":None,
                            "queryHash":"91f1ea046d2f3e21dabb3131898ec3c597cb879aa270ad780e8fdd687cde02a3"
                        },
                        {
                            "subscriptionName":"messageCreated",
                            "query":None,
                            "queryHash":"0445ef6a92aebf368dfb87659d2593b07a17d62ff48d0c0c8a0ae6ab2afd362c"
                        },
                        {
                            "subscriptionName":"viewerStateUpdated",
                            "query":None,
                            "queryHash":"cf9d367b40f59f4d087437912206dc0e3d344fb5085d0aba46cd88222a33edee"
                        },
                        {
                            "subscriptionName":"messageLimitUpdated",
                            "query":None,
                            "queryHash":"daec317b69fed95fd7bf1202c4eca0850e6a9740bc8412af636940227359a211"
                        },
                        {
                            "subscriptionName":"chatTitleUpdated",
                            "query":None,
                            "queryHash":"ee062b1f269ecd02ea4c2a3f1e4b2f222f7574c43634a2da4ebeb616d8647e06"
                        },
                        {
                            "subscriptionName":"knowledgeSourceUpdated",
                            "query":None,
                            "queryHash":"7de63f89277bcf54f2323008850573809595dcef687f26a78561910cfd4f6c37"
                        },
                        {
                            "subscriptionName":"messagePointLimitUpdated",
                            "query":None,
                            "queryHash":"94789388515b3c125c4a45d3c5112edffd102f8b72d4f152404f58e2aed9ec6d"
                        },
                        {
                            "subscriptionName":"chatMemberAdded",
                            "query":None,
                            "queryHash":"08b46c791cbb98b7e729c435d6b736ec60871dff58ec3a377ce818e30b50c1c8"
                        }
    ]
    
}
BOTS_LIST = {
    'Assistant': 'capybara',
    'Claude-3-Opus': 'claude_2_1_cedar',
    'Claude-3-Sonnet': 'claude_2_1_bamboo',
    'Claude-3-Opus-200k': 'claude_3_opus_200k',
    'Claude-3-Sonnet-200k': 'claude_3_sonnet_200k',
    'Claude-instant-100k': 'a2_100k',
    'Claude-2': 'claude_2_short',
    'Claude-2-100k': 'a2_2',
    'Claude-instant': 'a2',
    'ChatGPT': 'chinchilla',
    'GPT-3.5-Turbo': 'gpt3_5',
    'GPT-3.5-Turbo-Instruct': 'chinchilla_instruct',
    'ChatGPT-16k': 'agouti',
    'GPT-4': 'beaver',
    'GPT-4-128k': 'vizcacha',
    'Google-PaLM': 'acouchy',
    'Llama-2-7b': 'llama_2_7b_chat',
    'Llama-2-13b': 'llama_2_13b_chat',
    'Llama-2-70b': 'llama_2_70b_chat',
    'Code-Llama-7b': 'code_llama_7b_instruct',
    'Code-Llama-13b': 'code_llama_13b_instruct',
    'Code-Llama-34b': 'code_llama_34b_instruct',
    'Solar-Mini':'upstage_solar_0_70b_16bit',
}

REVERSE_BOTS_LIST = {v: k for k, v in BOTS_LIST.items()}

EXTENSIONS = {
    '.md': 'application/octet-stream',
    '.lua': 'application/octet-stream',
    '.rs': 'application/octet-stream',
    '.rb': 'application/octet-stream',
    '.go': 'application/octet-stream',
    '.java': 'application/octet-stream',
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

MEDIA_EXTENSIONS = {
    '.png': 'image/png',
    '.jpg': 'image/jpeg',
    '.jpeg': 'image/jpeg',
    '.gif': 'image/gif',
    '.mp4': 'video/mp4',
    '.mov': 'video/quicktime',
    '.mp3': 'audio/mpeg',
    '.wav': 'audio/wav',
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
    
def generate_file(file_path: list, proxy: dict=None):
    files = []   
    file_size = 0
    for file in file_path:
        if is_valid_url(file):
            # Handle URL files
            file_name = file.split('/')[-1]
            file_extension = os.path.splitext(file_name)[1].lower()
            content_type = MEDIA_EXTENSIONS.get(file_extension, EXTENSIONS.get(file_extension, None))
            if not content_type:
                raise RuntimeError("This file type is not supported. Please try again with a different file.")
            with cloudscraper.create_scraper() as fetcher:
                response = fetcher.get(file, proxies=proxy)
                file_data = response.content
            files.append((file_name, file_data, content_type))
            file_size += len(file_data)
        else:
            # Handle local files
            file_extension = os.path.splitext(file)[1].lower()
            content_type = MEDIA_EXTENSIONS.get(file_extension, EXTENSIONS.get(file_extension, None))
            if not content_type:
                raise RuntimeError("This file type is not supported. Please try again with a different file.")
            file_name = os.path.basename(file)
            with open(file, 'rb') as f:
                file_data = f.read()
                files.append((file_name, file_data, content_type))
                file_size += len(file_data)
    return files, file_size
