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
        {"subscriptionName":"messageAdded","query":None,"queryHash":"993dcce616ce18788af3cce85e31437abf8fd64b14a3daaf3ae2f0e02d35aa03"},
        {"subscriptionName":"messageCancelled","query":None,"queryHash":"14647e90e5960ec81fa83ae53d270462c3743199fbb6c4f26f40f4c83116d2ff"},
        {"subscriptionName":"messageDeleted","query":None,"queryHash":"91f1ea046d2f3e21dabb3131898ec3c597cb879aa270ad780e8fdd687cde02a3"},
        {"subscriptionName":"messageRead","query":None,"queryHash":"8c80ca00f63ad411ba7de0f1fa064490ed5f438d4a0e60fd9caa080b11af9495"},
        {"subscriptionName":"messageCreated","query":None,"queryHash":"47ee9830e0383f002451144765226c9be750d6c2135e648bced2ca7efc9d8a67"},
        {"subscriptionName":"messageStateUpdated","query":None,"queryHash":"117a49c685b4343e7e50b097b10a13b9555fedd61d3bf4030c450dccbeef5676"},
        {"subscriptionName":"messageAttachmentAdded","query":None,"queryHash":"65798bb2f409d9457fc84698479f3f04186d47558c3d7e75b3223b6799b6788d"},
        {"subscriptionName":"messageFollowupActionAdded","query":None,"queryHash":"d2e770beae7c217c77db4918ed93e848ae77df668603bc84146c161db149a2c7"},
        {"subscriptionName":"messageMetadataUpdated","query":None,"queryHash":"71c247d997d73fb0911089c1a77d5d8b8503289bc3701f9fb93c9b13df95aaa6"},
        {"subscriptionName":"messageTextUpdated","query":None,"queryHash":"800eea48edc9c3a81aece34f5f1ff40dc8daa71dead9aec28f2b55523fe61231"},
        {"subscriptionName":"jobStarted","query":None,"queryHash":"17099b40b42eb9f7e32323aa6badc9283b75a467bc8bc40ff5069c37d91856f6"},
        {"subscriptionName":"jobUpdated","query":None,"queryHash":"e8e492bfaf5041985055d07ad679e46b9a6440ab89424711da8818ae01d1a1f1"},
        {"subscriptionName":"viewerStateUpdated","query":None,"queryHash":"3b2014dba11e57e99faa68b6b6c4956f3e982556f0cf832d728534f4319b92c7"},
        {"subscriptionName":"unreadChatsUpdated","query":None,"queryHash":"5b4853e53ff735ae87413a9de0bce15b3c9ba19102bf03ff6ae63ff1f0f8f1cd"},
        {"subscriptionName":"chatTitleUpdated","query":None,"queryHash":"ee062b1f269ecd02ea4c2a3f1e4b2f222f7574c43634a2da4ebeb616d8647e06"},
        {"subscriptionName":"knowledgeSourceUpdated","query":None,"queryHash":"7de63f89277bcf54f2323008850573809595dcef687f26a78561910cfd4f6c37"},
        {"subscriptionName":"messagePointLimitUpdated","query":None,"queryHash":"ed3857668953d6e8849c1562f3039df16c12ffddaaac1db930b91108775ee16d"},
        {"subscriptionName":"chatMemberAdded","query":None,"queryHash":"21ef45e20cc8120c31a320c3104efe659eadf37d49249802eff7b15d883b917b"},
        {"subscriptionName":"chatSettingsUpdated","query":None,"queryHash":"3b370c05478959224e3dbf9112d1e0490c22e17ffb4befd9276fc62e196b0f5b"},
        {"subscriptionName":"chatModalStateChanged","query":None,"queryHash":"f641bc122ac6a31d466c92f6c724343688c2f679963b7769cb07ec346096bfe7"}]
}


BOTS_LIST = {
    'Assistant': 'capybara',
    'Claude-3.5-Sonnet': 'claude_3_igloo',
    'Claude-3-Opus': 'claude_2_1_cedar',
    'Claude-3-Sonnet': 'claude_2_1_bamboo',
    'Claude-3-Haiku': 'claude_3_haiku',
    'Claude-3-Opus-200k': 'claude_3_opus_200k',
    'Claude-3.5-Sonnet-200k': 'claude_3_igloo_200k',
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