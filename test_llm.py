"""
简化测试 - 仅测试 LLM 连接
"""
import asyncio
import sys
import os
from pathlib import Path

# 加载 .env
from dotenv import load_dotenv
load_dotenv(Path(__file__).parent / '.env')

async def test_llm():
    """测试 LLM 连接"""
    print("🧪 测试 LLM 连接...\n")
    
    api_key = os.getenv('OPENAI_API_KEY')
    base_url = os.getenv('OPENAI_BASE_URL')
    model = "MiniMax-M2.5"
    
    print(f"📡 配置:")
    print(f"   Model: {model}")
    print(f"   Base URL: {base_url}")
    print(f"   API Key: {api_key[:10]}...{api_key[-5:]}")
    
    from openai import AsyncOpenAI
    
    client = AsyncOpenAI(
        api_key=api_key,
        base_url=base_url
    )
    
    try:
        print("\n📤 发送测试请求...")
        response = await client.chat.completions.create(
            model=model,
            messages=[
                {"role": "user", "content": "你好，请用一句话介绍你自己"}
            ],
            max_tokens=100
        )
        
        result = response.choices[0].message.content
        print(f"\n✅ 成功!")
        print(f"📝 响应: {result}")
        return True
        
    except Exception as e:
        print(f"\n❌ 失败: {e}")
        return False
    finally:
        await client.close()

if __name__ == "__main__":
    success = asyncio.run(test_llm())
    sys.exit(0 if success else 1)
