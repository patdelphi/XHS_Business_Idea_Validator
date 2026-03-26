"""
测试运行脚本 - 非交互模式
"""
import asyncio
import sys
from pathlib import Path

project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from agents.orchestrator import OrchestratorAgent
from agents.config import ConfigManager
from agents.context_store import ContextStore

async def test_run():
    """测试运行"""
    print("🧪 开始测试 AI 连接...")
    
    config = ConfigManager()
    context_store = ContextStore()
    orchestrator = OrchestratorAgent(config, context_store)
    
    # 简单测试 LLM 连接
    llm_config = config.get_llm_config()
    print(f"📡 LLM 配置:")
    print(f"   Model: {llm_config.model_name}")
    print(f"   Base URL: {llm_config.base_url}")
    print(f"   API Key: {llm_config.api_key[:10]}...")
    
    # 测试 LLM 调用
    from mcp_servers.llm_server import LLMClient
    
    client = LLMClient(
        api_key=llm_config.api_key,
        base_url=llm_config.base_url,
        model_name=llm_config.model_name
    )
    
    await client.start()
    
    try:
        result = await client.generate_text("你好，请用一句话介绍你自己")
        print(f"\n✅ LLM 响应成功:")
        print(f"   {result[:200]}...")
        return True
    except Exception as e:
        print(f"\n❌ LLM 调用失败: {e}")
        return False
    finally:
        await client.close()

if __name__ == "__main__":
    success = asyncio.run(test_run())
    sys.exit(0 if success else 1)
