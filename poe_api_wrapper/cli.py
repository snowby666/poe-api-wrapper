import argparse
from importlib import metadata

def main():
    parser = argparse.ArgumentParser(prog='poe',description='Poe.com wrapper. Have free access to ChatGPT, Claude, Llama, Google-PaLM and more!')
    parser.add_argument('key',help="'p-b' cookie value for poe.com")
    parser.add_argument('-v','--version',action='version', version='v'+metadata.version('poe-api-wrapper'))
    args = parser.parse_args()
    from poe_api_wrapper import PoeExample
    PoeExample(args.key).chat_with_bot()

if __name__=='__main__':
    main()