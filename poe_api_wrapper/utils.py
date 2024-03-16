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
    'GPT-4-32k': 'vizcacha',
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

BOT_CREATION_MODELS = [
    'dalle3',
    'stablediffusionxl',
    'playgroundv25',
    'chinchilla',
    'mixtral8x7bchat',
    'a2',
    'gemini_pro',
    'llama_2_70b_chat',
    'beaver',
    'a2_2',
    'a2_100k'
]

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