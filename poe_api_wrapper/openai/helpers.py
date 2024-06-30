import random, string, time
from heapq import nlargest
from loguru import logger

from nltk.data import find as resource_find
from nltk import download as nltk_download

try:
    resource_find('corpora/stopwords')
except LookupError:
    logger.warning("NLTK stopwords not found. Downloading...")
    nltk_download('stopwords')
try:
    resource_find('tokenizers/punkt')
except LookupError:
    logger.warning("NLTK punkt not found. Downloading...")
    nltk_download('punkt')
    
from nltk.corpus import stopwords
from nltk.probability import FreqDist
from nltk.stem import PorterStemmer
from nltk.tokenize import sent_tokenize, word_tokenize
import tiktoken

async def __progressive_summarize_text(text, max_length, initial_reduction_ratio=0.8, step=0.1):
    if len(text) < max_length:
        return text
    
    stop_words = set(stopwords.words("english"))
    ps = PorterStemmer()
    sentences = sent_tokenize(text)

    # Remove stopwords and apply stemming
    words = [ps.stem(word) for word in word_tokenize(text.lower()) if word not in stop_words]
    
    # Calculate word frequencies
    word_freqs = FreqDist(words)

    # Score sentences based on word frequency
    sentence_scores = {idx: sum(word_freqs.get(word, 0) for word in word_tokenize(sentence.lower())) for idx, sentence in enumerate(sentences)}
    
    reduction_ratio = initial_reduction_ratio

    # Extract top N sentences based on their scores
    while True:
        num_sentences = max(1, round(len(sentences) * reduction_ratio))
        selected_indexes = nlargest(num_sentences, sentence_scores, key=sentence_scores.get)
        summary = '\n'.join(sentences[idx] for idx in sorted(selected_indexes))

        if 0 < len(summary.strip()) <= max_length or reduction_ratio - step < 0:
            break
        else:
            reduction_ratio -= step

    return summary

async def __validate_messages_format(messages):
    if not messages:
        return False
    if not isinstance(messages, list) or not all(isinstance(message, dict) for message in messages):
        return False
    if messages[0]["role"] == "assistant" or messages[-1]["role"] == "assistant":
        return False
    if any(message["role"] == "system" for message in messages[1:]):
        return False
    return True

async def __split_content(messages):
    text_messages = []
    image_urls = []
    
    for message in messages:
        if "content" in message and isinstance(message["content"], list):
            for item in message["content"]:
                if item["type"] == "text":
                    if "text" in item:
                        text_messages.append({"role": message["role"], "content": item["text"]})
                elif item["type"] == "image_url":
                    if "image_url" in item:
                        if isinstance(item["image_url"], str):
                            image_urls.append(item["image_url"])  
                        elif isinstance(item["image_url"], dict) and "url" in item["image_url"]:
                            if item["image_url"]["url"] not in image_urls:
                                image_urls.append(item["image_url"]["url"])
                        else:
                            logger.error(f"Invalid image URL format: {item['image_url']}")
        elif "content" in message and isinstance(message["content"], str):
            text_messages.append({"role": message["role"], "content": message["content"]})  
               
    return text_messages, image_urls

async def __generate_completion_id():
    return "".join(random.choices(string.ascii_letters + string.digits, k=28))

async def __generate_timestamp():
    return int(time.time())

async def __tokenize(text):
    enconder = tiktoken.get_encoding("cl100k_base")
    return len(enconder.encode(text))

async def __stringify_messages(messages):
    return '\n'.join(f"{message['role'].capitalize()}: {message['content']}" for message in messages)