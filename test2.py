from poe_api_wrapper import PoeApi

# def get_word_definition(word):
#     client = PoeApi('cEkRoOK7Lic-vGKbMdjS4g==')
#     bot = "chinchilla"
#     prompt = "Hello"
#     message = (
#         "Explain the meaning of the word " + word +
#         " to a child in less than 30 words. You must give me 4 values: the word, the definition, word type and the example sentence. Your response should be in the following format: word:definition:word type:example sentence. There should be no spaces between the colon and the word. There should be no additional colons in the example sentence. Here is an example output - luminary:someone who is well known:noun:marie curie was a luminary"
#     )
#     print(message)

#     for chunk in client.send_message(bot, message):
#         pass

#     print(chunk["text"])

#     chunk = chunk["text"].split(":")

#     return {
#         "word": chunk[0].strip(),
#         "definition": chunk[1].strip(),
#         "word_type": chunk[2].strip(),
#         "example_sentence": chunk[3].strip()
#     }

# get_word_definition("luminary")

from poe_api_wrapper import PoeApi
token = "cEkRoOK7Lic-vGKbMdjS4g=="
client = PoeApi(token)
# client.chat_with_bot()
print(client)

bot = "gpt3_5"
message = "What is reverse engineering?"

# Create new chat thread
# Streamed example:
for chunk in client.send_message(bot, message):
    print(chunk["response"], end="", flush=True)
print("\n")