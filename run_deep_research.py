"""
深度调研脚本 - 分析 30+ 条笔记，生成详细报告
用法：python run_deep_research.py "业务创意"
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

XHS_SKILLS_PATH = Path.home() / ".openclaw" / "skills" / "xiaohongshu-skills"
XHS_CLI = XHS_SKILLS_PATH / "scripts" / "cli.py"

def search_xhs(keyword: str, max_results: int = 30) -> list:
    """使用 xiaohongshu-skills 搜索笔记"""
    print(f"   搜索关键词：{keyword}...")
    
    try:
        cmd = ["uv", "run", "python", str(XHS_CLI), "search-feeds", "--keyword", keyword]
        
        result = subprocess.run(cmd, cwd=str(XHS_SKILLS_PATH), capture_output=True, text=True, timeout=90)
        output = result.stdout.strip()
        
        try:
            data = json.loads(output)
        except json.JSONDecodeError:
            json_start = output.rfind('{')
            json_end = output.rfind('}')
            if json_start >= 0 and json_end > json_start:
                output = output[json_start:json_end+1]
                data = json.loads(output)
            else:
                raise
        
        if isinstance(data, dict):
            feeds = data.get('feeds', [])[:max_results]
        elif isinstance(data, list):
            feeds = data[:max_results]
        else:
            return []
        
        print(f"   ✅ 获取 {len(feeds)} 条笔记")
        return feeds
            
    except Exception as e:
        print(f"   ❌ 错误：{e}")
        return []

async def deep_research(business_idea: str):
    """深度调研"""
    print("╔══════════════════════════════════════════════════════════════╗")
    print("║         业务创意深度调研系统 v1.0                               ║")
    print("╚══════════════════════════════════════════════════════════════╝\n")
    
    print(f"🎯 调研主题：{business_idea}\n")
    
    llm_client = AsyncOpenAI(
        api_key=os.getenv('OPENAI_API_KEY'),
        base_url=os.getenv('OPENAI_BASE_URL')
    )
    
    # 步骤 1: 搜索笔记（最多 30 条）
    print("📊 步骤 1: 搜索小红书笔记...")
    feeds = search_xhs(business_idea, max_results=30)
    
    if not feeds:
        print("\n❌ 未找到相关笔记")
        await llm_client.close()
        return False
    
    print(f"\n   ✅ 共获取 {len(feeds)} 条笔记\n")
    
    # 步骤 2: 数据整理
    print("📊 步骤 2: 整理笔记数据...")
    
    def get_count(feed, key):
        interact = feed.get('interactInfo', {}) or feed.get('note_card', {}).get('interact_info', {})
        val = interact.get(key, interact.get(key.lower(), 0))
        try:
            return int(val or 0)
        except:
            return 0
    
    # 计算统计数据
    total_likes = sum(get_count(f, 'likedCount') for f in feeds)
    total_collects = sum(get_count(f, 'collectedCount') for f in feeds)
    total_comments = sum(get_count(f, 'commentCount') for f in feeds)
    avg_engagement = (total_likes + total_collects * 2 + total_comments) / len(feeds) if feeds else 0
    
    # 按互动排序
    sorted_feeds = sorted(feeds, key=lambda x: get_count(x, 'likedCount'), reverse=True)
    
    # 提取 TOP 10 笔记详情
    top_10_details = []
    for i, feed in enumerate(sorted_feeds[:10], 1):
        detail = {
            "rank": i,
            "title": feed.get('displayTitle', feed.get('note_card', {}).get('title', 'N/A'))[:100],
            "author": feed.get('user', {}).get('nickname', feed.get('note_card', {}).get('user', {}).get('nickname', 'N/A')),
            "likes": get_count(feed, 'likedCount'),
            "collects": get_count(feed, 'collectedCount'),
            "comments": get_count(feed, 'commentCount'),
            "type": feed.get('type', 'normal'),
        }
        top_10_details.append(detail)
    
    print(f"   ✅ 数据整理完成\n")
    
    # 步骤 3: AI 深度分析
    print("📊 步骤 3: AI 深度分析...")
    
    notes_text = "\n\n".join([
        f"【{i+1}】标题：{feed.get('displayTitle', feed.get('note_card', {}).get('title', 'N/A'))}\n"
        f"作者：{feed.get('user', {}).get('nickname', 'N/A')}\n"
        f"互动：点赞{get_count(feed, 'likedCount')} | 收藏{get_count(feed, 'collectedCount')} | 评论{get_count(feed, 'commentCount')}\n"
        f"类型：{feed.get('type', 'normal')}"
        for i, feed in enumerate(feeds[:20])
    ])
    
    analysis_prompt = f"""
你是一位资深市场研究分析师。请对以下小红书笔记进行深度市场分析：

**调研主题**: {business_idea}
**样本数量**: {len(feeds)} 条笔记
**数据范围**: 小红书平台

**笔记样本**:
{notes_text[:6000]}

请输出以下深度分析（每部分至少 150 字）：

## 一、市场概况
1. 内容热度评估（总互动、平均互动、头部效应）
2. 内容供给分析（笔记数量、更新频率、创作者类型）

## 二、用户画像深度分析
1. 核心用户群体（年龄、性别、地域、收入水平）
2. 用户需求分层（显性需求、隐性需求、潜在需求）
3. 用户决策路径（关注点、顾虑点、触发点）

## 三、内容生态分析
1. 热门内容类型（图文/视频、测评/种草/干货）
2. 爆款内容特征（标题、封面、内容结构）
3. 内容缺口机会（未被满足的信息需求）

## 四、竞争格局
1. 主要参与者（个人创作者、机构账号、品牌方）
2. 竞争程度评估（1-10 分，附详细理由）
3. 头部账号分析（粉丝量、内容策略、变现方式）

## 五、市场机会评估
1. 市场机会评分（1-10 分，附详细理由）
2. 推荐切入点（3 个具体方向）
3. 风险提示（政策、竞争、用户接受度）

## 六、行动建议
1. 内容策略（做什么类型的内容）
2. 差异化定位（如何与现有内容区分）
3. 变现路径（可能的商业模式）
"""
    
    response = await llm_client.chat.completions.create(
        model="MiniMax-M2.5",
        messages=[{"role": "user", "content": analysis_prompt}],
        max_tokens=4000
    )
    
    analysis = response.choices[0].message.content
    print("✅ 深度分析完成\n")
    
    # 步骤 4: 生成完整报告
    print("📊 步骤 4: 生成完整报告...")
    report_dir = Path(__file__).parent / "reports"
    report_dir.mkdir(exist_ok=True)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    safe_name = business_idea.replace("/", "_").replace(" ", "_")
    report_file = report_dir / f"{safe_name}_{timestamp}_deep_research.md"
    
    # 构建完整报告
    report_content = f"""# 🔍 {business_idea} - 深度市场调研报告

**生成时间**: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}  
**数据源**: xiaohongshu-skills (CDP)  
**样本数量**: {len(feeds)} 条笔记  
**调研平台**: 小红书

---

## 📊 核心数据概览

| 指标 | 数值 |
|------|------|
| 分析笔记数 | {len(feeds)} |
| 总点赞数 | {total_likes:,} |
| 总收藏数 | {total_collects:,} |
| 总评论数 | {total_comments:,} |
| 平均互动数 | {avg_engagement:,.1f} |
| 头部笔记点赞 | {get_count(sorted_feeds[0], 'likedCount'):,} |

---

## 📈 TOP 10 热门笔记

| 排名 | 标题 | 作者 | 点赞 | 收藏 | 评论 | 类型 |
|------|------|------|------|------|------|------|
"""
    
    for item in top_10_details:
        report_content += f"| {item['rank']} | {item['title'][:30]}... | {item['author']} | {item['likes']:,} | {item['collects']:,} | {item['comments']:,} | {item['type']} |\n"
    
    report_content += f"""
---

## 🤖 AI 深度分析

{analysis}

---

## 📋 原始数据附录

### 全部笔记列表

"""
    
    for i, feed in enumerate(sorted_feeds, 1):
        report_content += f"""
#### {i}. {feed.get('displayTitle', feed.get('note_card', {}).get('title', 'N/A'))}
- **作者**: {feed.get('user', {}).get('nickname', 'N/A')}
- **互动**: 点赞{get_count(feed, 'likedCount')} | 收藏{get_count(feed, 'collectedCount')} | 评论{get_count(feed, 'commentCount')}
- **类型**: {feed.get('type', 'normal')}

"""
    
    with open(report_file, 'w', encoding='utf-8') as f:
        f.write(report_content)
    
    print(f"✅ 报告已保存：{report_file}")
    print(f"\n📄 报告字数：{len(report_content):,} 字")
    
    await llm_client.close()
    return str(report_file)

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("用法：python run_deep_research.py \"业务创意\"")
        sys.exit(1)
    
    business_idea = " ".join(sys.argv[1:])
    report_path = asyncio.run(deep_research(business_idea))
    
    if report_path:
        print(f"\n✅ 深度调研完成！报告路径：{report_path}")
    sys.exit(0 if report_path else 1)
