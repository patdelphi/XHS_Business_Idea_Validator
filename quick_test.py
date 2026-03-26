"""
快速测试 - 完整流程（简化版）
"""
import asyncio
import sys
import os
from pathlib import Path

from dotenv import load_dotenv
load_dotenv(Path(__file__).parent / '.env')

async def quick_test():
    """快速测试完整流程"""
    print("╔══════════════════════════════════════════════════════════════╗")
    print("║         业务创意验证系统 - 快速测试                            ║")
    print("╚══════════════════════════════════════════════════════════════╝\n")
    
    business_idea = "在深圳卖陈皮"
    print(f"🎯 业务创意：{business_idea}\n")
    
    # 1. 测试 LLM 分析能力
    print("📊 步骤 1: 测试 AI 分析能力...")
    from openai import AsyncOpenAI
    
    client = AsyncOpenAI(
        api_key=os.getenv('OPENAI_API_KEY'),
        base_url=os.getenv('OPENAI_BASE_URL')
    )
    
    test_prompt = """
    请分析以下业务创意的市场需求：
    业务：在深圳卖陈皮
    
    请从以下角度分析（每点 1 句话）：
    1. 目标用户是谁？
    2. 主要痛点是什么？
    3. 竞争格局如何？
    """
    
    try:
        response = await client.chat.completions.create(
            model="MiniMax-M2.5",
            messages=[{"role": "user", "content": test_prompt}],
            max_tokens=500
        )
        
        analysis = response.choices[0].message.content
        print("✅ AI 分析完成:\n")
        print(analysis)
        print()
        
        # 2. 测试 TikHub 连接
        print("\n📊 步骤 2: 测试 TikHub 小红书 API 连接...")
        tikhub_token = os.getenv('TIKHUB_TOKEN')
        
        import httpx
        async with httpx.AsyncClient() as http_client:
            test_url = "https://api.tikhub.io/v1/xhs/search/search"
            headers = {
                "Authorization": f"Bearer {tikhub_token}",
                "Content-Type": "application/json"
            }
            data = {
                "keyword": "陈皮",
                "page": 1,
                "page_size": 1
            }
            
            resp = await http_client.post(test_url, headers=headers, json=data, timeout=30)
            
            if resp.status_code == 200:
                result = resp.json()
                print(f"✅ TikHub API 连接成功!")
                print(f"   状态码：{resp.status_code}")
                if 'data' in result and 'items' in result['data']:
                    print(f"   搜索结果数：{len(result['data']['items'])}")
            else:
                print(f"⚠️ TikHub API 响应：{resp.status_code}")
                print(f"   {resp.text[:200]}")
        
        await client.close()
        
        print("\n" + "="*60)
        print("✅ 测试完成！系统可用")
        print("="*60)
        return True
        
    except Exception as e:
        print(f"\n❌ 测试失败：{e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = asyncio.run(quick_test())
    sys.exit(0 if success else 1)
