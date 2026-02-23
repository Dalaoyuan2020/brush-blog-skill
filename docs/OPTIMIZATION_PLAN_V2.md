# Brush Skill V2.0 - 性能优化方案

## 📊 问题描述

### P0 故障：响应慢 + 推荐重复

**现象：**
- 用户点击 `/brush` 后等待 5-15 秒
- 反复推荐同一篇文章（Frigate with Hailo 刷了 10+ 次）
- 用户体验极差，功能基本不可用

**根因：**
- 串行架构：每次请求都重新刷新 38 个 RSS 源
- 无缓存：内容池不持久化
- 无去重：没有已读历史过滤

---

## 🏗️ 架构设计

### 前后端分离

```
┌───────────────── 后端（内容池 Agent）──────────────────┐
│                                                        │
│  后台任务：定时刷新 RSS → 解析 → 去重 → 存入内容池     │
│  触发条件：内容池 <30% 或 推荐率变化                   │
│  输出：content_pool.json（10-20 篇去重后的文章）        │
│                                                        │
└────────────────────────────────────────────────────────┘
                          ↓ (文件共享)
┌───────────────── 前端（用户交互 Agent）────────────────┐
│                                                        │
│  用户点击 /brush                                       │
│  ↓                                                     │
│  直接读 content_pool.json（0.1 秒）                     │
│  ↓                                                     │
│  推荐算法选 1 篇（0.1 秒）                              │
│  ↓                                                     │
│  返回结果 + inline buttons（<1 秒）                     │
│                                                        │
└────────────────────────────────────────────────────────┘
```

### 核心模块

| 模块 | 职责 | 优先级 |
|------|------|--------|
| **内容池管理** | RSS 刷新、去重、缓存 | P0 |
| **用户交互** | 推荐算法、按钮回调 | P0 |
| **已读历史** | 24 小时内不重复推荐 | P0 |
| **后台任务** | 定时刷新、清理过期数据 | P1 |

---

## ✅ MVP 功能清单（V2.0 第一版）

### 必须有
1. ✅ 内容池 Agent（后台运行，保持 10-20 篇文章）
2. ✅ 用户交互 Agent（直接从内容池推荐，<2 秒响应）
3. ✅ 基础查重（URL 去重，不重复进池子）
4. ✅ 自动补货（内容池<30% 时刷新）

### 第一版不做（后续迭代）
- ❌ 推荐率动态调整
- ❌ 固定区/可释放区
- ❌ 标题相似度检测
- ❌ 用户偏好个性化

---

## 📏 验收标准

| 指标 | 目标 | 当前 |
|------|------|------|
| 响应时间 | <3 秒（目标 2 秒） | 5-15 秒 |
| 内容池大小 | 10-20 篇 | 不稳定 |
| 重复率 | 24 小时内不重复 | 高频重复 |
| 稳定性 | 连续刷 10 次不卡死 | 经常卡死 |

---

## 🛠️ 技术实现

### 共享数据结构

**目录：** `/home/admin/clawd/skills/brush/shared/`

**文件：**
- `content_pool.json` - 内容池（10-20 篇去重文章）
- `user_prefs.json` - 用户偏好（已选领域）
- `read_history.json` - 已读历史（24 小时内）
- `tasks.jsonl` - 任务队列（后台任务）

### 内容池 Schema

```json
{
  "articles": [
    {
      "id": "unique_id",
      "title": "文章标题",
      "summary": "摘要",
      "url": "原文链接",
      "source": "来源站点",
      "tags": ["#tag1", "#tag2"],
      "fetched_at": "2026-02-23T13:00:00+08:00",
      "recommended_count": 0
    }
  ],
  "last_refresh": "2026-02-23T13:00:00+08:00",
  "pool_size": 15,
  "min_threshold": 5
}
```

### 去重逻辑

```python
def should_add_to_pool(new_article, existing_pool, read_history):
    # 1. URL 去重（池子内不重复）
    if new_article.url in [a.url for a in existing_pool]:
        return False
    
    # 2. 已读历史过滤（24 小时内不重复）
    if new_article.url in read_history:
        return False
    
    # 3. 标题相似度（可选，第一版可不做）
    # ...
    
    return True
```

### 自动补货逻辑

```python
def check_and_refresh(content_pool):
    pool_size = len(content_pool.articles)
    min_threshold = 5  # 30% of 15
    
    if pool_size < min_threshold:
        # 触发刷新
        refresh_rss_feeds()
        return True
    
    return False
```

---

## 📋 任务拆解（给 Opus 规划）

### Phase 1: 内容池管理（P0）
- [ ] 设计 content_pool.json schema
- [ ] 实现 RSS 刷新模块
- [ ] 实现 URL 去重逻辑
- [ ] 实现自动补货触发

### Phase 2: 用户交互（P0）
- [ ] 修改 `/brush` 命令从内容池推荐
- [ ] 实现已读历史过滤
- [ ] 优化响应时间（<2 秒）

### Phase 3: 后台任务（P1）
- [ ] 定时刷新任务
- [ ] 清理过期已读历史
- [ ] 日志记录

### Phase 4: 测试验收
- [ ] 性能测试（连续刷 10 次）
- [ ] 重复率测试（24 小时内）
- [ ] 稳定性测试

---

## 📂 文件位置

- **方案文档：** `docs/OPTIMIZATION_PLAN_V2.md`
- **用户反馈：** `docs/USER_FEEDBACK_2026-02-23.md`
- **M11 经验：** `docs/M11_BUTTON_FIX_EXPERIENCE.md`
- **Notion 项目：** https://www.notion.so/Skill-Agent-Team-30fd38a850fc813da8fdf68cbab7f3e3

---

## 🎯 下一步

1. 羊爸爸确认本方案
2. Opus 阅读方案 → 拆解任务 → 输出详细实现计划
3. Codex 按计划实现
4. 测试验收

---

*创建时间：2026-02-23 13:17 (Asia/Shanghai)*
*版本：V2.0 MVP*
