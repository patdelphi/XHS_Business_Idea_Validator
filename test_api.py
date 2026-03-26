"""测试 TikHub API"""
import asyncio
import os
from dotenv import load_dotenv
from pathlib import Path
from urllib.parse import quote_plus
import aiohttp

load_dotenv(Path(__file__).parent / '.env')

async def test():
    tikhub_token = os.getenv('TIKHUB_TOKEN')
    tikhub_base = "https://api.tikhub.io/api/v1/xiaohongshu/web"
    
    headers = {
        "Authorization": f"Bearer {tikhub_token}",
        "Accept": "application/json",
        "User-Agent": "Mozilla/5.0"
    }
    
    keyword = "保险理财"
    encoded_keyword = quote_plus(keyword)
    url = f"{tikhub_base}/search_notes"
    params = {
        "keyword": encoded_keyword,
        "page": 1,
        "sort": "general",
        "noteType": "_0"
    }
    
    print(f"URL: {url}")
    print(f"Params: {params}\n")
    
    async with aiohttp.ClientSession() as session:
        async with session.get(url, headers=headers, params=params) as resp:
            print(f"Status: {resp.status}")
            print(f"Headers: {dict(resp.headers)}\n")
            
            body = await resp.json()
            print(f"Response: {body}")

asyncio.run(test())
