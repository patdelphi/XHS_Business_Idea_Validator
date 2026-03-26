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
        "Accept": "application/json"
    }
    
    # 尝试不同的端点
    endpoints = [
        "https://api.tikhub.io/api/v1/user/info",
        "https://api.tikhub.io/api/v1/account/info",
        "https://api.tikhub.io/api/v1/tiktok/user_info",  # TikTok 端点测试 token
    ]
    
    async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=30)) as session:
        for url in endpoints:
            print(f"\n测试：{url}")
            async with session.get(url, headers=headers) as resp:
                print(f"  状态：{resp.status}")
                try:
                    result = await resp.json()
                    print(f"  响应：{str(result)[:200]}")
                except:
                    text = await resp.text()
                    print(f"  响应：{text[:200]}")

asyncio.run(test())
