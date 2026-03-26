import asyncio
import os
from dotenv import load_dotenv
from pathlib import Path
from urllib.parse import quote_plus
import aiohttp

load_dotenv(Path(__file__).parent / '.env')

async def test():
    tikhub_token = os.getenv('TIKHUB_TOKEN')
    url = "https://api.tikhub.io/api/v1/xiaohongshu/web/search_notes"
    
    headers = {
        "Authorization": f"Bearer {tikhub_token}",
        "Accept": "application/json",
        "User-Agent": "Mozilla/5.0"
    }
    
    # 尝试不同关键词
    keywords = ["保险", "理财", "存钱"]
    
    async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=60)) as session:
        for kw in keywords:
            params = {
                "keyword": kw,
                "page": 1,
                "sort": "general",
                "noteType": "_0"
            }
            
            print(f"\n测试关键词：{kw}")
            async with session.get(url, headers=headers, params=params) as resp:
                print(f"  状态：{resp.status}")
                if resp.status == 200:
                    result = await resp.json()
                    if 'data' in result and 'data' in result['data']:
                        items = result['data']['data'].get('items', [])
                        print(f"  笔记数：{len(items)}")
                    else:
                        print(f"  响应：{result}")
                elif resp.status == 400:
                    error = await resp.json()
                    print(f"  错误：{error}")
                else:
                    text = await resp.text()
                    print(f"  响应：{text[:200]}")

asyncio.run(test())
