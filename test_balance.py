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
    
    async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=30)) as session:
        # 检查账户信息
        print("检查账户信息...")
        url = "https://api.tikhub.io/api/v1/user/me"
        async with session.get(url, headers=headers) as resp:
            print(f"状态：{resp.status}")
            result = await resp.json()
            print(f"响应：{result}")
        
        # 检查余额
        print("\n检查余额...")
        url = "https://api.tikhub.io/api/v1/user/credits"
        async with session.get(url, headers=headers) as resp:
            print(f"状态：{resp.status}")
            result = await resp.json()
            print(f"响应：{result}")

asyncio.run(test())
