"""
非交互式运行脚本
用法：python run_non_interactive.py "业务创意"
"""
import asyncio
import sys
import os
import json
from pathlib import Path
from datetime import datetime
from dotenv import load_dotenv
from urllib.parse import quote_plus

load_dotenv(Path(__file__).parent / '.env')

from openai import AsyncOpenAI
import aiohttp

async def validate_business_idea(business_idea: str, fast_mode: bool = True):
    """验证业务创意"""
    print("╔══════════════════════════════════════════════════════════════╗")
    print("║         业务创意验证系统 v0.1.0                                 ║")
    print("╚══════════════════════════════════════════════════════════════╝\n")
    
    print(f"🎯 业务创意：{business_idea}\n")
    
    # 初始化 LLM 客户端
    llm_client = AsyncOpenAI(
        api_key=os.getenv('OPENAI_API_KEY'),
        base_url=os.getenv('OPENAI_BASE_URL')
    )
    
    # TikHub 配置 - 使用国际域名 + 正确的参数
    tikhub_token = os.getenv('TIKHUB_TOKEN')
    tikhub_base = "https://api.tikhub.io/api/v1/xiaohongshu/web"
    headers = {
        "Authorization": f"Bearer {tikhub_token}",
        "Accept": "application/json",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    }
    
    # 设置参数
    if fast_mode:
        pages = 1
        max_posts = 10
        print("⚡ 快速模式：1 页 × 10 笔记\n")
    else:
        pages = 2
        max_posts = 20
        print("📊 完整模式：2 页 × 20 笔记\n")
    
    # 增加超时时间到 60 秒
    async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=60, connect=30)) as session:
        try:
            # 步骤 1: 搜索小红书笔记
            print("📊 步骤 1: 搜索小红书笔记...")
            
            all_notes = []
            for page in range(1, pages + 1):
                encoded_keyword = quote_plus(business_idea)
                url = f"{tikhub_base}/search_notes"
                # 正确的参数：note_type=0 (不是 noteType)
                params = {
                    "keyword": encoded_keyword,
                    "page": page,
                    "sort": "general",
                    "note_type": 0
                }
                
                print(f"   请求第{page}页...", end=" ", flush=True)
                
                async with session.get(url, headers=headers, params=params) as resp:
                    if resp.status == 200:
                        result = await resp.json()
                        # TikHub 响应结构：result['data']['data']['items']
                        if 'data' in result and 'data' in result['data'] and 'items' in result['data']['data']:
                            items = result['data']['data']['items']
                            # 提取 note 对象
                            notes = [item['note'] for item in items if 'note' in item]
                            all_notes.extend(notes)
                            print(f"✅ 获取 {len(notes)} 条笔记")
                        else:
                            print(f"⚠️ 响应结构异常")
                    elif resp.status == 400:
                        error = await resp.json()
                        print(f"❌ 400 错误：{error.get('detail', {}).get('message', '')[:100]}")
                    elif resp.status == 401:
                        print(f"❌ 401 未授权 - Token 无效")
                        return False
                    elif resp.status == 402:
                        print(f"❌ 402 余额不足")
                        return False
                    elif resp.status == 504:
                        print(f"⏱️ 504 超时")
                    else:
                        print(f"❌ 失败：{resp.status}")
            
            print(f"\n   ✅ 共获取 {len(all_notes)} 条笔记\n")
            
            if not all_notes:
                print("❌ 未找到相关笔记")
                return False
            
            # 步骤 2: 分析笔记内容
            print("📊 步骤 2: AI 分析笔记内容...")
            
            sample_notes = all_notes[:max_posts]
            notes_text = "\n\n".join([
                f"标题：{note.get('title', 'N/A')}\n内容：{note.get('desc', 'N/A')}\n点赞：{note.get('liked_count', 0)}\n收藏：{note.get('collected_count', 0)}\n评论：{note.get('comments_count', 0)}"
                for note in sample_notes
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
            report_file = report_dir / f"{safe_name}_{timestamp}.md"
            
            # 计算互动数据
            total_engagement = sum(
                note.get('liked_count', 0) + 
                note.get('collected_count', 0) * 2 + 
                note.get('shared_count', 0) * 3 + 
                note.get('comments_count', 0)
                for note in sample_notes
            )
            avg_engagement = total_engagement / len(sample_notes) if sample_notes else 0
            
            report_content = f"""# 业务创意验证报告

**业务创意**: {business_idea}  
**生成时间**: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}  
**模式**: {"快速" if fast_mode else "完整"}

---

## 📊 数据概览

- **分析笔记数**: {len(sample_notes)}
- **总互动数**: {total_engagement}
- **平均互动数**: {avg_engagement:.1f}

---

## 🤖 AI 分析结果

{analysis}

---

## 📈 热门笔记 TOP 5

"""
            
            sorted_notes = sorted(
                sample_notes,
                key=lambda x: x.get('liked_count', 0) + x.get('collected_count', 0) * 2,
                reverse=True
            )[:5]
            
            for i, note in enumerate(sorted_notes, 1):
                report_content += f"""
### TOP {i}
- **标题**: {note.get('title', note.get('desc', 'N/A')[:50])}
- **互动**: 点赞{note.get('liked_count', 0)} | 收藏{note.get('collected_count', 0)} | 评论{note.get('comments_count', 0)}
- **作者**: {note.get('user', {}).get('nickname', 'N/A')}
"""
            
            with open(report_file, 'w', encoding='utf-8') as f:
                f.write(report_content)
            
            print(f"✅ 报告已保存：{report_file}")
            print(f"\n📄 报告预览:\n{report_content[:2000]}")
            
            return True
            
        except asyncio.TimeoutError:
            print("\n❌ 错误：请求超时（60 秒）")
            return False
        except Exception as e:
            print(f"\n❌ 错误：{e}")
            import traceback
            traceback.print_exc()
            return False
        finally:
            await llm_client.close()

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("用法：python run_non_interactive.py \"业务创意\"")
        sys.exit(1)
    
    business_idea = " ".join(sys.argv[1:])
    success = asyncio.run(validate_business_idea(business_idea, fast_mode=True))
    sys.exit(0 if success else 1)
