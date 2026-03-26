"""
调试 LLM 响应
"""
import asyncio
import os
from dotenv import load_dotenv
from pathlib import Path

load_dotenv(Path(__file__).parent / '.env')

from openai import AsyncOpenAI

async def debug():
    api_key = os.getenv('OPENAI_API_KEY')
    base_url = os.getenv('OPENAI_BASE_URL')
    
    print(f"API Key: {api_key[:10]}...{api_key[-5:]}")
    print(f"Base URL: {base_url}\n")
    
    client = AsyncOpenAI(api_key=api_key, base_url=base_url)
    
    prompt = "你好，请用一句话介绍你自己"
    
    print(f"发送：{prompt}")
    print(f"Model: MiniMax-M2.5\n")
    
    response = await client.chat.completions.create(
        model="MiniMax-M2.5",
        messages=[{"role": "user", "content": prompt}],
        max_tokens=100
    )
    
    print(f"完整响应:")
    print(f"  choices: {len(response.choices)}")
    if response.choices:
        msg = response.choices[0].message
        print(f"  message role: {msg.role}")
        print(f"  content: '{msg.content}'")
        print(f"  content type: {type(msg.content)}")
        print(f"  content bool: {bool(msg.content)}")
    
    await client.close()

asyncio.run(debug())
