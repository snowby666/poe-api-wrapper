import argparse
from importlib import metadata

def main():
    parser = argparse.ArgumentParser(prog='poe',description='Poe.com wrapper. Have free access to ChatGPT, Claude, Llama, Gemini, Google-PaLM and more!')
    parser.add_argument('--b', help='p-b token for poe.com | m-b token for quora.com', required=True)
    parser.add_argument('--lat', help='p-lat token for poe.com | m-lat token for quora.com', required=True)
    parser.add_argument('-v','--version',action='version', version='v'+metadata.version('poe-api-wrapper'))
    args = parser.parse_args()
    from poe_api_wrapper import PoeExample
    PoeExample({'b': args.b, 'lat': args.lat}).chat_with_bot()

if __name__=='__main__':
    main()