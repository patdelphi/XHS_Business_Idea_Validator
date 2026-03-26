# TikHub API 测试总结

**测试时间**: 2026-03-26 13:30  
**测试人**: BigBoss 🦀

---

## ✅ **关键发现**

### 正确的 API 配置

| 配置项 | 值 |
|--------|-----|
| **域名** | `https://api.tikhub.io` (国际) |
| **端点** | `/api/v1/xiaohongshu/web/search_notes` |
| **参数** | `keyword`, `page`, `sort`, `note_type=0` |
| **User-Agent** | 需要完整的浏览器 UA |

### 首次成功测试
```
测试关键词：理财
状态：200
✅ 成功！笔记数：20
```

---

## ⚠️ **API 不稳定性**

| 测试时间 | 关键词 | 状态 | 说明 |
|----------|--------|------|------|
| 13:15 | 理财 | 200 ✅ | 返回 20 条笔记 |
| 13:29 | 理财 | 400 ❌ | Request failed |
| 13:30 | 保险理财 | 400 ❌ | Request failed |

**可能原因**:
1. **API 限流** - 请求频率过高
2. **服务器不稳定** - TikHub 服务器波动
3. **关键词敏感** - 某些关键词可能触发风控

---

## 📋 **正确的请求格式**

```python
import aiohttp

headers = {
    "Authorization": f"Bearer {YOUR_TOKEN}",
    "Accept": "application/json",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
}

params = {
    "keyword": "理财",  # 简单关键词成功率更高
    "page": 1,
    "sort": "general",
    "note_type": 0  # 整数 0，不是字符串
}

async with session.get(url, headers=headers, params=params) as resp:
    if resp.status == 200:
        result = await resp.json()
        notes = result['data']['data']['items']
```

---

## 💡 **建议**

### 立即可用
1. **等待 5-10 分钟** - 可能是临时限流
2. **使用简单关键词** - "理财" 比 "保险理财" 成功率高
3. **添加重试机制** - 指数退避重试

### 长期方案
1. **联系 TikHub 支持** - Discord: https://discord.gg/Pu2uKkFu6u
2. **检查账户余额** - 可能余额不足
3. **考虑备用方案** - 整合现有 `xiaohongshu-skills`

---

## 📁 项目状态

| 模块 | 状态 |
|------|------|
| 代码克隆 | ✅ |
| 依赖安装 | ✅ |
| LLM 分析 | ✅ |
| TikHub API | ⚠️ 不稳定 |
| 报告生成 | ✅ |

---

**下一步**: 等待几分钟后重试，或联系 TikHub 支持确认 API 状态 🦀
