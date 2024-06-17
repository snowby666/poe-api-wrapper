import argparse
from importlib import metadata
from poe_api_wrapper import PoeExample

def main():
    parser = argparse.ArgumentParser(prog='poe',description='Poe.com wrapper. Have free access to ChatGPT, Claude, Llama, Gemini, Google-PaLM and more!')
    parser.add_argument('-b', help='p-b token for poe.com', required=True)
    parser.add_argument('-lat', help='p-lat token for poe.com', required=True)
    parser.add_argument('-f', help='formkey for poe.com')
    parser.add_argument('-v', '--version',action='version', version='v'+metadata.version('poe-api-wrapper'))
    args = parser.parse_args()
    PoeExample({'p-b': args.b, 'p-lat': args.lat, 'formkey': args.f}).chat_with_bot()

if __name__=='__main__':
    main()