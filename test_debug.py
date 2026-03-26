import asyncio
import os
from pathlib import Path
from dotenv import load_dotenv
import aiohttp
from urllib.parse import quote_plus

load_dotenv(Path(__file__).parent / '.env')

async def test():
    tikhub_token = os.getenv('TIKHUB_TOKEN')
    
    headers = {
        "Authorization": f"Bearer {tikhub_token}",
        "Accept": "application/json",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    }
    
    business_idea = "保险理财"
    encoded_keyword = quote_plus(business_idea)
    
    url = "https://api.tikhub.io/api/v1/xiaohongshu/web/search_notes"
    
    # 完全按照测试脚本的参数
    params = {
        "keyword": encoded_keyword,
        "page": 1,
        "sort": "general",
        "note_type": 0
    }
    
    print(f"URL: {url}")
    print(f"Params: {params}")
    print(f"Encoded keyword: {encoded_keyword}")
    
    async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=60)) as session:
        async with session.get(url, headers=headers, params=params) as resp:
            print(f"\n状态：{resp.status}")
            if resp.status == 200:
                result = await resp.json()
                print(f"响应：成功")
                if 'data' in result and 'data' in result['data']:
                    items = result['data']['data'].get('items', [])
                    print(f"笔记数：{len(items)}")
            else:
                error = await resp.json()
                print(f"错误：{error}")

asyncio.run(test())
