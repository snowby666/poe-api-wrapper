try:
    from ballyregan import ProxyFetcher
    from ballyregan.models import Protocols, Anonymities
    PROXY = True
except ImportError:
    PROXY = False

if PROXY:
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
        return [{'http': f'http://{proxy.ip}:{proxy.port}'} for proxy in proxies]