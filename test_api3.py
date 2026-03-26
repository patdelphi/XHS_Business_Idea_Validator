import asyncio
import os
from dotenv import load_dotenv
from pathlib import Path
import aiohttp

load_dotenv(Path(__file__).parent / '.env')

async def test():
    tikhub_token = os.getenv('TIKHUB_TOKEN')
    base_url = "https://api.tikhub.io/api/v1/xiaohongshu/web"
    
    headers = {
        "Authorization": f"Bearer {tikhub_token}",
        "Accept": "application/json",
        "User-Agent": "Mozilla/5.0"
    }
    
    # 尝试不同的 API 端点和参数
    tests = [
        {
            "name": "search_notes (无 noteType)",
            "url": f"{base_url}/search_notes",
            "params": {"keyword": "理财", "page": 1, "sort": "general"}
        },
        {
            "name": "search_notes (noteType=0)",
            "url": f"{base_url}/search_notes",
            "params": {"keyword": "理财", "page": 1, "sort": "general", "noteType": "0"}
        },
        {
            "name": "search_notes (noteType 为空)",
            "url": f"{base_url}/search_notes",
            "params": {"keyword": "理财", "page": 1, "sort": "general", "noteType": ""}
        },
    ]
    
    async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=60)) as session:
        for test in tests:
            print(f"\n测试：{test['name']}")
            async with session.get(test['url'], headers=headers, params=test['params']) as resp:
                print(f"  状态：{resp.status}")
                if resp.status == 200:
                    result = await resp.json()
                    if 'data' in result and 'data' in result['data']:
                        items = result['data']['data'].get('items', [])
                        print(f"  ✅ 笔记数：{len(items)}")
                    else:
                        print(f"  响应结构：{list(result.keys())}")
                else:
                    error = await resp.json()
                    print(f"  ❌ {error.get('detail', {}).get('message', '')[:100]}")

asyncio.run(test())
