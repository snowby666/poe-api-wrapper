import os, string, secrets, base64
from urllib.parse import urlparse
from httpx import Client
from loguru import logger

BASE_URL = 'https://poe.com'
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36 Edg/115.0.1901.203",
    "Accept": "*/*",
    "Accept-Language": "en-US,en;q=0.5",
    "Sec-Ch-Ua": '"Microsoft Edge";v="123", "Not:A-Brand";v="8", "Chromium";v="123"',
    "Sec-Ch-Ua-Mobile": "?0",
    "Sec-Ch-Ua-Platform": '"Windows"',
    "Upgrade-Insecure-Requests": "1",
    "Origin": "https://poe.com",
    "Referer": "https://poe.com/",
}

SubscriptionsMutation = {
    "subscriptions":[
        {"subscriptionName":"messageAdded","query":None,"queryHash":"41ca89f5809bf7fd210b10dedacd28d872f63ab5c434766e639530dd396ef48d"},
        {"subscriptionName":"messageCancelled","query":None,"queryHash":"14647e90e5960ec81fa83ae53d270462c3743199fbb6c4f26f40f4c83116d2ff"},
        {"subscriptionName":"messageDeleted","query":None,"queryHash":"91f1ea046d2f3e21dabb3131898ec3c597cb879aa270ad780e8fdd687cde02a3"},
        {"subscriptionName":"messageCreated","query":None,"queryHash":"2b51823489f77348fb74e6d6b4defbca1d5f18ff67ceec12529c36e894a10399"},
        {"subscriptionName":"viewerStateUpdated","query":None,"queryHash":"03169de18b76396784ed970bd6f33eb48763d763b3732711525181bf8a3a6bc2"},
        {"subscriptionName":"chatTitleUpdated","query":None,"queryHash":"ee062b1f269ecd02ea4c2a3f1e4b2f222f7574c43634a2da4ebeb616d8647e06"},
        {"subscriptionName":"knowledgeSourceUpdated","query":None,"queryHash":"7de63f89277bcf54f2323008850573809595dcef687f26a78561910cfd4f6c37"},
        {"subscriptionName":"messagePointLimitUpdated","query":None,"queryHash":"ed3857668953d6e8849c1562f3039df16c12ffddaaac1db930b91108775ee16d"},
        {"subscriptionName":"chatMemberAdded","query":None,"queryHash":"365b7b0352ff8b6267801b0a54c7f5567651cae30fa2d54ba5ee2931141ad5f0"},
        {"subscriptionName":"chatSettingsUpdated","query":None,"queryHash":"3b370c05478959224e3dbf9112d1e0490c22e17ffb4befd9276fc62e196b0f5b"},
        {"subscriptionName":"chatModalStateChanged","query":None,"queryHash":"8dcd92366d3ea9a867957f1ac9443d8ca25140a206dff4957b99f40ec6f46994"}
    ]
}


BOTS_LIST = {
    'Assistant': 'capybara',
    'Claude-3-Opus': 'claude_2_1_cedar',
    'Claude-3-Sonnet': 'claude_2_1_bamboo',
    'Claude-3-Haiku': 'claude_3_haiku',
    'Claude-3-Opus-200k': 'claude_3_opus_200k',
    'Claude-3-Sonnet-200k': 'claude_3_sonnet_200k',
    'Claude-3-Haiku-200k': 'claude_3_haiku_200k',
    'Claude-2': 'claude_2_short',
    'Claude-2-100k': 'a2_2',
    'Claude-instant': 'a2',
    'Claude-instant-100k': 'a2_100k',
    'GPT-3.5-Turbo': 'chinchilla',
    'GPT-3.5-Turbo-Raw': 'gpt3_5',
    'GPT-3.5-Turbo-Instruct': 'chinchilla_instruct',
    'ChatGPT-16k': 'agouti',
    'GPT-4-Classic': 'gpt4_classic',
    'GPT-4-Turbo': 'beaver',
    'GPT-4-Turbo-128k': 'vizcacha',
    'GPT-4o': 'gpt4_o',
    'GPT-4o-128k': 'gpt4_o_128k',
    'GPT-4o-Mini': 'gpt4_o_mini',
    'GPT-4o-Mini-128k': 'gpt4_o_mini_128k',
    'Google-PaLM': 'acouchy',
    'Code-Llama-13b': 'code_llama_13b_instruct',
    'Code-Llama-34b': 'code_llama_34b_instruct',
    'Solar-Mini':'upstage_solar_0_70b_16bit',
    'Gemini-1.5-Flash-Search': 'gemini_pro_search',
    'Gemini-1.5-Pro-2M': 'gemini_1_5_pro_1m',
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
        if isinstance(file, str) and file.startswith("data:image"):
            file_extension = file.split(";")[0].split("/")[-1]
            content_type = MEDIA_EXTENSIONS.get(f".{file_extension}", "image/png")
            file_data = base64.b64decode(file.split(",")[1])
            file_name = f"{generate_nonce(8)}.{file_extension}"
            files.append((file_name, file_data, content_type))
            file_size += len(file_data)
            
        elif is_valid_url(file):
            # Handle URL files
            file_name = file.split('/')[-1]
            file_extension = os.path.splitext(file_name)[1].lower()
            content_type = MEDIA_EXTENSIONS.get(file_extension, EXTENSIONS.get(file_extension, None))
            if not content_type:
                raise RuntimeError("This file type is not supported. Please try again with a different file.")
            logger.info(f"Downloading file from {file}")
            with Client(proxies=proxy, http2=True) as fetcher:
                response = fetcher.get(file)
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