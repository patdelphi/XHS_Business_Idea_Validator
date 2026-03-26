"""
备用测试脚本 - 使用不同的 API 端点
"""
import asyncio
import os
from pathlib import Path
from dotenv import load_dotenv
import aiohttp
import json
from datetime import datetime

load_dotenv(Path(__file__).parent / '.env')

async def test_feed():
    """测试推荐流 API"""
    tikhub_token = os.getenv('TIKHUB_TOKEN')
    
    headers = {
        "Authorization": f"Bearer {tikhub_token}",
        "Accept": "application/json",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    }
    
    # 尝试不同的端点
    endpoints = [
        "https://api.tikhub.io/api/v1/xiaohongshu/web/feed",
        "https://api.tikhub.io/api/v1/xiaohongshu/web/note_detail",
    ]
    
    async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=30)) as session:
        for url in endpoints:
            print(f"\n测试：{url}")
            params = {"noteId": "69a9ba86000000003201a79a"}  # 示例 ID
            async with session.get(url, headers=headers, params=params) as resp:
                print(f"  状态：{resp.status}")
                if resp.status == 200:
                    result = await resp.json()
                    print(f"  ✅ 成功")
                    return True
                else:
                    try:
                        error = await resp.json()
                        print(f"  错误：{str(error)[:100]}")
                    except:
                        text = await resp.text()
                        print(f"  响应：{text[:100]}")
    
    return False

# 检查账户信息
async def check_account():
    """检查账户余额"""
    tikhub_token = os.getenv('TIKHUB_TOKEN')
    
    headers = {
        "Authorization": f"Bearer {tikhub_token}",
        "Accept": "application/json"
    }
    
    url = "https://api.tikhub.io/api/v1/user/credit"
    
    async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=30)) as session:
        print("\n检查账户余额...")
        async with session.get(url, headers=headers) as resp:
            print(f"  状态：{resp.status}")
            if resp.status == 200:
                result = await resp.json()
                print(f"  响应：{json.dumps(result, indent=2)[:500]}")
            else:
                text = await resp.text()
                print(f"  响应：{text[:200]}")

async def main():
    await check_account()
    await test_feed()

asyncio.run(main())
