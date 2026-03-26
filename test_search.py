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
    
    # 测试两个域名的搜索 API
    domains = [
        ("api.tikhub.io (国际)", "https://api.tikhub.io"),
        ("api.tikhub.dev (中国大陆)", "https://api.tikhub.dev"),
    ]
    
    keyword = "理财"
    params = {
        "keyword": keyword,
        "page": 1,
        "sort": "general",
        "note_type": 0,  # 尝试不同的参数名
    }
    
    async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=60)) as session:
        for name, base in domains:
            print(f"\n测试：{name}")
            url = f"{base}/api/v1/xiaohongshu/web/search_notes"
            
            # 尝试不同的参数名
            for param_variant in [
                {"noteType": ""},
                {"noteType": "0"},
                {"note_type": 0},
                {},  # 无 noteType 参数
            ]:
                test_params = {**params, **param_variant}
                # 清理空值
                test_params = {k: v for k, v in test_params.items() if v != "" and v is not None}
                
                param_str = " ".join([f"{k}={v}" for k, v in test_params.items()])
                print(f"  参数：{param_str}")
                
                async with session.get(url, headers=headers, params=test_params) as resp:
                    print(f"    状态：{resp.status}")
                    if resp.status == 200:
                        result = await resp.json()
                        if 'data' in result and 'data' in result['data']:
                            items = result['data']['data'].get('items', [])
                            print(f"    ✅ 成功！笔记数：{len(items)}")
                            return  # 成功就退出
                        else:
                            print(f"    响应结构：{list(result.keys())}")
                    elif resp.status == 400:
                        error = await resp.json()
                        msg = error.get('detail', {}).get('message', '')[:80]
                        print(f"    ❌ 400: {msg}")
                    elif resp.status == 504:
                        print(f"    ⏱️ 504 超时")
                    else:
                        text = await resp.text()
                        print(f"    响应：{text[:100]}")

asyncio.run(test())
