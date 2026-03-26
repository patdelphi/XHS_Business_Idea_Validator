import asyncio
import os
from pathlib import Path
from dotenv import load_dotenv
import aiohttp

load_dotenv(Path(__file__).parent / '.env')

async def test():
    tikhub_token = os.getenv('TIKHUB_TOKEN')
    
    headers = {
        "Authorization": f"Bearer {tikhub_token}",
        "Accept": "application/json",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    }
    
    # 完全复制之前成功的测试
    params = {
        "keyword": "理财",  # 简单关键词
        "page": 1,
        "sort": "general",
        "note_type": 0,
    }
    
    url = "https://api.tikhub.io/api/v1/xiaohongshu/web/search_notes"
    
    async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=60)) as session:
        async with session.get(url, headers=headers, params=params) as resp:
            print(f"状态：{resp.status}")
            if resp.status == 200:
                result = await resp.json()
                if 'data' in result and 'data' in result['data']:
                    items = result['data']['data'].get('items', [])
                    print(f"✅ 成功！笔记数：{len(items)}")
            else:
                error = await resp.json()
                print(f"❌ 错误：{error.get('detail', {}).get('message', '')[:100]}")

asyncio.run(test())
