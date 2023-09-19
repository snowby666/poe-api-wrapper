from poe_api_wrapper import PoeApi, PoeExample

PoeExample('tI3cMXb6Ei3aOEGiHBn8OA==').chat_with_bot()

client = PoeApi('tI3cMXb6Ei3aOEGiHBn8OA==')

for chunk in client.send_message('a2', 'Nice to meet you'):
    print(chunk['response'], end='', flush=True)