from ballyregan import ProxyFetcher
from ballyregan.models import Protocols, Anonymities

def fetch_proxy():
    fetcher = ProxyFetcher()
    try:
        proxies = fetcher.get(
        limit=10,
        protocols=[Protocols.HTTP],
        anonymities=[Anonymities.ANONYMOUS],
        )
    except:
        print("No Anonymous proxies found. Switching to normal proxies ...") 
        proxies = fetcher.get(
        limit=10,
        protocols=[Protocols.HTTP],
        )
    return proxies