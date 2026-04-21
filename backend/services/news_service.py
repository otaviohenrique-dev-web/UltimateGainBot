import aiohttp
import asyncio
from typing import List

class NewsService:
    """Serviço de notícias do mercado."""
    
    def __init__(self, api_key=""):
        self.api_key = api_key
        self.cached_news = []
        self.last_fetch_ts = 0
    
    async def fetch_news(self, query="BTC", lang="PT") -> List[str]:
        """Busca notícias de criptografia."""
        import time
        now = time.time()
        
        # Cache de 5 minutos
        if self.last_fetch_ts > 0 and (now - self.last_fetch_ts) < 300:
            return self.cached_news
        
        try:
            url = f"https://min-api.cryptocompare.com/data/v2/news/"
            params = {
                'categories': query,
                'lang': lang,
                'api_key': self.api_key
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.get(url, params=params, timeout=10) as resp:
                    if resp.status == 200:
                        data = await resp.json()
                        headlines = [
                            item['title'] 
                            for item in data.get('Data', [])[:10]
                        ]
                        self.cached_news = headlines
                        self.last_fetch_ts = now
                        return headlines
        
        except Exception as e:
            print(f">>> ❌ Erro ao buscar notícias: {e}")
        
        return self.cached_news