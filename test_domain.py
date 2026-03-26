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
    
    # 测试两个域名
    domains = [
        ("api.tikhub.io (国际)", "https://api.tikhub.io"),
        ("api.tikhub.dev (中国大陆)", "https://api.tikhub.dev"),
    ]
    
    # 测试用户信息端点
    async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=30)) as session:
        for name, base in domains:
            print(f"\n测试：{name}")
            url = f"{base}/api/v1/user/info"
            async with session.get(url, headers=headers) as resp:
                print(f"  状态：{resp.status}")
                try:
                    result = await resp.json()
                    print(f"  响应：{str(result)[:200]}")
                except:
                    text = await resp.text()
                    print(f"  响应：{text[:200]}")

asyncio.run(test())
