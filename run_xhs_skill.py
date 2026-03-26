"""
使用 xiaohongshu-skills 运行业务创意验证
用法：python run_xhs_skill.py "业务创意"
"""
import asyncio
import sys
import os
import json
import subprocess
from pathlib import Path
from datetime import datetime
from dotenv import load_dotenv

load_dotenv(Path(__file__).parent / '.env')

from openai import AsyncOpenAI

# xiaohongshu-skills 路径
XHS_SKILLS_PATH = Path.home() / ".openclaw" / "skills" / "xiaohongshu-skills"
XHS_CLI = XHS_SKILLS_PATH / "scripts" / "cli.py"

def search_xhs(keyword: str, max_results: int = 10) -> list:
    """使用 xiaohongshu-skills 搜索笔记"""
    print(f"   搜索关键词：{keyword}...")
    
    try:
        # 调用 xiaohongshu-skills CLI
        cmd = [
            "uv", "run", "python", str(XHS_CLI),
            "search-feeds",
            "--keyword", keyword
        ]
        
        result = subprocess.run(
            cmd,
            cwd=str(XHS_SKILLS_PATH),
            capture_output=True,
            text=True,
            timeout=60
        )
        
        # 解析 JSON 输出
        output = result.stdout.strip()
        # 找到最后一个 JSON 对象
        json_start = output.rfind('{')
        if json_start >= 0:
            output = output[json_start:]
        
        data = json.loads(output)
        
        if data.get('success') and 'feeds' in data:
            feeds = data['feeds'][:max_results]
            print(f"   ✅ 获取 {len(feeds)} 条笔记")
            return feeds
        else:
            error = data.get('error', '未知错误')
            print(f"   ❌ 错误：{error}")
            return []
            
    except subprocess.TimeoutExpired:
        print("   ❌ 超时（60 秒）")
        return []
    except json.JSONDecodeError as e:
        print(f"   ❌ JSON 解析错误：{e}")
        print(f"   输出：{output[:200]}")
        return []
    except Exception as e:
        print(f"   ❌ 错误：{e}")
        return []

async def validate_business_idea(business_idea: str, fast_mode: bool = True):
    """验证业务创意"""
    print("╔══════════════════════════════════════════════════════════════╗")
    print("║         业务创意验证系统 v0.2.0 (xiaohongshu-skills)            ║")
    print("╚══════════════════════════════════════════════════════════════╝\n")
    
    print(f"🎯 业务创意：{business_idea}\n")
    
    # 初始化 LLM 客户端
    llm_client = AsyncOpenAI(
        api_key=os.getenv('OPENAI_API_KEY'),
        base_url=os.getenv('OPENAI_BASE_URL')
    )
    
    # 设置参数
    max_posts = 10 if fast_mode else 20
    print(f"⚡ 快速模式：最多 {max_posts} 条笔记\n")
    
    # 步骤 1: 搜索小红书笔记
    print("📊 步骤 1: 搜索小红书笔记...")
    feeds = search_xhs(business_idea, max_results=max_posts)
    
    if not feeds:
        print("\n❌ 未找到相关笔记")
        await llm_client.close()
        return False
    
    print(f"\n   ✅ 共获取 {len(feeds)} 条笔记\n")
    
    # 步骤 2: 分析笔记内容
    print("📊 步骤 2: AI 分析笔记内容...")
    
    notes_text = "\n\n".join([
        f"标题：{feed.get('note_card', {}).get('title', 'N/A')}\n"
        f"内容：{feed.get('note_card', {}).get('desc', 'N/A')}\n"
        f"点赞：{feed.get('note_card', {}).get('interact_info', {}).get('liked_count', 0)}\n"
        f"收藏：{feed.get('note_card', {}).get('interact_info', {}).get('collected_count', 0)}\n"
        f"评论：{feed.get('note_card', {}).get('interact_info', {}).get('comment_count', 0)}"
        for feed in feeds
    ])
    
    analysis_prompt = f"""
你是一个市场分析师。请分析以下小红书笔记，提取市场洞察：

业务创意：{business_idea}

笔记样本：
{notes_text[:4000]}

请输出以下分析（每点 2-3 句话）：
1. 目标用户画像
2. 用户核心痛点/需求
3. 热门话题/关键词
4. 竞争程度评估（1-10 分）
5. 市场机会评分（1-10 分）及理由
"""
    
    response = await llm_client.chat.completions.create(
        model="MiniMax-M2.5",
        messages=[{"role": "user", "content": analysis_prompt}],
        max_tokens=1500
    )
    
    analysis = response.choices[0].message.content
    print("✅ 分析完成:\n")
    print(analysis)
    
    # 步骤 3: 生成报告
    print("\n\n📊 步骤 3: 生成报告...")
    report_dir = Path(__file__).parent / "reports"
    report_dir.mkdir(exist_ok=True)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    safe_name = business_idea.replace("/", "_").replace(" ", "_")
    report_file = report_dir / f"{safe_name}_{timestamp}_xhs.md"
    
    # 计算互动数据
    total_engagement = sum(
        feed.get('note_card', {}).get('interact_info', {}).get('liked_count', 0) + 
        feed.get('note_card', {}).get('interact_info', {}).get('collected_count', 0) * 2 + 
        feed.get('note_card', {}).get('interact_info', {}).get('comment_count', 0)
        for feed in feeds
    )
    avg_engagement = total_engagement / len(feeds) if feeds else 0
    
    report_content = f"""# 业务创意验证报告 (xiaohongshu-skills)

**业务创意**: {business_idea}  
**生成时间**: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}  
**数据源**: xiaohongshu-skills (CDP)

---

## 📊 数据概览

- **分析笔记数**: {len(feeds)}
- **总互动数**: {total_engagement}
- **平均互动数**: {avg_engagement:.1f}

---

## 🤖 AI 分析结果

{analysis}

---

## 📈 热门笔记 TOP 5

"""
    
    sorted_feeds = sorted(
        feeds,
        key=lambda x: x.get('note_card', {}).get('interact_info', {}).get('liked_count', 0),
        reverse=True
    )[:5]
    
    for i, feed in enumerate(sorted_feeds, 1):
        note_card = feed.get('note_card', {})
        interact_info = note_card.get('interact_info', {})
        user_info = note_card.get('user', {})
        
        report_content += f"""
### TOP {i}
- **标题**: {note_card.get('title', note_card.get('desc', 'N/A')[:50])}
- **互动**: 点赞{interact_info.get('liked_count', 0)} | 收藏{interact_info.get('collected_count', 0)} | 评论{interact_info.get('comment_count', 0)}
- **作者**: {user_info.get('nickname', 'N/A')}
"""
    
    with open(report_file, 'w', encoding='utf-8') as f:
        f.write(report_content)
    
    print(f"✅ 报告已保存：{report_file}")
    print(f"\n📄 报告预览:\n{report_content[:2000]}")
    
    await llm_client.close()
    return True

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("用法：python run_xhs_skill.py \"业务创意\"")
        sys.exit(1)
    
    business_idea = " ".join(sys.argv[1:])
    success = asyncio.run(validate_business_idea(business_idea, fast_mode=True))
    sys.exit(0 if success else 1)
