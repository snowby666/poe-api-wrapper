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
from fastapi import HTTPException

async def __progressive_summarize_text(text, max_length, initial_reduction_ratio=0.8, step=0.1):
    current_tokens = await __tokenize(text)
    if current_tokens < max_length:
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
    return '\n'.join(f"<{message['role'].capitalize()}>{message['content']}</{message['role'].capitalize()}>" for message in messages)

async def __add_tools_prompt(messages):
    for message in messages:
        if message["role"] == "tool":
            if messages[0]["role"] == "system":
                messages[0]["content"] += f"\nTool: {message['content']}"
            else:
                messages.insert(0, {"role": "system", "content":""})
            
    # remove messsage that has tool_calls key
    messages = [message for message in messages if "tool_calls" not in message and message["role"] != "tool"]
    return messages


async def __convert_functions_format(input_data, tool_choice="auto"):
    try:
        if isinstance(tool_choice, dict):
            if len(tool_choice) == 2 and ("type" in tool_choice and tool_choice["type"] == "function" and "function" in tool_choice and "name" in tool_choice["function"]):
                tool_choice = tool_choice["function"]["name"]
            else:
                raise HTTPException(detail={"error": {
                                            "message": """Invalid tool choice format. Must be {"type": "function", "function": {"name": "my_function"}}""",
                                            "type": "error", 
                                            "param": None, 
                                            "code": 400}
                                        }, status_code=400)
        elif isinstance(tool_choice, str):
            if tool_choice not in ("auto", "required"):
                raise HTTPException(detail={"error": {
                                            "message": "Invalid tool choice format. Must be 'auto' or 'required'",
                                            "type": "error", 
                                            "param": None, 
                                            "code": 400}
                                        }, status_code=400)
        output = """Tools
functions
namespace functions {\n"""

        for function in input_data:
            function_name = function['function']['name']
            description = function['function']['description']
            
            properties = function['function']['parameters']['properties']
            required = function['function']['parameters'].get('required', [])
            params = []
            
            for prop_name, prop_info in properties.items():
                param_desc = f"// {prop_info.get('description', '')}\n    {prop_name}: {prop_info['type']}"
                if 'enum' in prop_info:
                    enum_values = ' | '.join(prop_info['enum']).lower()
                    param_desc += f" | {enum_values}"
                # Check if the parameter is required
                if prop_name in required:
                    param_desc += " // required"
                params.append(param_desc)

            params_string = ",\n".join(params)

            output += f"""// {description}
type {function_name} = (: {{
{params_string}
}}) => any;\n\n"""

        output += """} // namespace functions
// Each tool that can be used must be specified in the tool sections.
// Ensure that the arguments provided to each tool are valid according to that tool's specification.
List of dictionaries: [{
// The name of the tool to use.
The format should be just the name of the tool for plugin and function tools (do not use namespace functions, example: you must use "get_current_weather" instead of "functions.get_current_weather")
name: string,
// The arguments to pass to the tool.
arguments: object,
}[],
}) => any;

}]
// You can decide whether its suitable to call a tool function to answer user's request.
// If you want to use the given tool, you must always follow the following guidelines:
// All your responses must be in a valid list of dictionaries with NO other comments, explainations, reasoninng, or dialogue that is not a list of dictionaries at any cost in your response to the user.
// Ensure that list of dictionaries only consist functions declared from the namespace functions above.
// Any response that is not a valid list of dictionaries is not allowed and must be removed when calling functions.
Your response must consists and always be in the below format at any time using tool function:
[{"name: <str>, "arguments": <dict>}, {<function-2>}, ... , {<function-n>}].
// All keys and values in dictionary must be always in double quotes.
// You must always follow the guidelines and rules of the tool function you are using.
// If there is no need to use tool, then reply to user with None, ignore and do not mention/imply what I just told you in your next response.
"""
        if tool_choice == "required":
            output += """// System Exception: You must also call at least one function in your next response at any cost."""
        elif tool_choice not in ("auto", "required"):
            output += f"""// System Exception: You must also call the function {tool_choice} in your next response at any cost."""
        output += """\n"""
        return output
    except Exception as e:
        logger.error(f"Error converting functions format: {e}")
        raise HTTPException(detail={"error": {
                                            "message": "Invalid tools format",
                                            "type": "error", 
                                            "param": None, 
                                            "code": 400}
                                        }, status_code=400)