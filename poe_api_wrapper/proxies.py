from ballyregan import ProxyFetcher
from ballyregan.models import Protocols, Anonymities
fetcher = ProxyFetcher()

def fetch_proxy():
    proxies = fetcher.get(
    limit=10,
    protocols=[Protocols.HTTP],
    anonymities=[Anonymities.ANONYMOUS],
    )
    return proxies