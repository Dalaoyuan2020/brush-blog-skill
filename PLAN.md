# PLAN.md - 刷博客 Skill 技术路线

**创建者**: Opus (CloneLamb)  
**日期**: 2026-02-22  
**状态**: ✅ 规划完成，待开发

---

## 1️⃣ 架构总览

```
graph TB
    subgraph 用户层
        A["Telegram 用户"]
    end
    subgraph Moltbot Skill
        B["交互引擎 (按钮/滑动模拟)"]
        C["推荐引擎"]
        D["行为收集器"]
        E["知识沉淀器"]
    end
    subgraph 数据层
        F["内容池 (RSS + 爬虫)"]
        G["用户画像库"]
        H["知识库 (Notion/NotebookLM)"]
    end
    A -->|操作指令| B
    B -->|推送请求| C
    C -->|取内容| F
    C -->|读画像| G
    B -->|行为事件| D
    D -->|更新| G
    B -->|存储指令| E
    E -->|写入| H
```

---

## 2️⃣ 模块划分

### 模块 A：内容采集模块

**职责**: RSS 源管理、内容抓取、清洗

**初始 RSS 源分类**:
- 🖥️ 技术/编程（Hacker News、阮一峰、CSS-Tricks）
- 🧠 AI/ML（Lil'Log、Distill、Jay Alammar）
- 💰 商业/创业（Paul Graham、a16z）
- 🎨 设计/产品（Nielsen Norman、Intercom）
- 🌍 科学/通识（Wait But Why、Quanta Magazine）

### 模块 B：交互引擎

**职责**: Telegram 按钮交互、内容展示、用户操作处理

**核心交互流程**:
```
┌─────────────────────────┐
│  📰 博客卡片            │
│  标题：xxx              │
│  摘要：2-3 句话           │
│  标签：#AI #Python      │
│  来源：blog.example.com │
├─────────────────────────┤
│ [👍 感兴趣] [👎 划走]   │
│ [📖 深度阅读] [💾 收藏] │
│ [🔄 换一批]             │
└─────────────────────────┘
```

**按钮映射**:
- 👍 感兴趣 → 记录正反馈，推送相似内容
- 👎 划走 → 记录负反馈，推送下一条
- 📖 深度阅读 → 展开全文摘要 + 原文链接
- 💾 收藏 → 存入知识库
- 🔄 换一批 → 刷新推荐池

### 模块 C：推荐引擎

**职责**: 内容评分、排序、推荐

**推荐公式**:
```
Score = Interest(u, i) × 0.4
      + Knowledge(u, i) × 0.3
      + Diversity(i)     × 0.2
      + Popularity(i)    × 0.1
```

**各分量计算方案**:

**Embedding 方案**:
- 第一阶段：TF-IDF + 标签匹配（零成本，快速上线）
- 第二阶段：sentence-transformers
- 第三阶段：可选接入 SiliconFlow embedding API

### 模块 D：行为收集器

**职责**: 用户行为采集、画像更新、兴趣衰减

**采集的行为事件**:
- 点击（👍/👎/📖/💾）
- 停留时间
- 滚动深度
- 是否追问

**用户画像结构**:
```python
UserProfile {
  user_id: string
  interest_tags: { tag: string, score: float }[]   # 衰减加权
  read_history: string[]                            # 最近 100 条
  favorite_sources: string[]                        # 偏好来源
  knowledge_topics: string[]                        # 知识库主题
  created_at: timestamp
  last_active: timestamp
}
```

**兴趣衰减**:
- 每次交互后，旧兴趣分数 × 0.95
- 新交互的标签 +2/+3/+5（根据操作类型）

### 模块 E：知识沉淀器

**职责**: 结构化笔记生成、Notion/NotebookLM 存储

**存储流程**:
1. 用户点击 💾 收藏
2. LLM 生成结构化笔记：标题 + 3 句摘要 + 关键概念 + 原文链接
3. 写入 Notion Database（通过 Notion API）
4. 可选：同步到 NotebookLM

**Notion Database Schema**:
- Title (标题)
- Source (来源链接)
- Summary (摘要)
- Tags (标签)
- Saved At (保存时间)
- Rating (评分)

---

## 3️⃣ 数据流设计

### 主数据流（Happy Path）

```
sequenceDiagram
    participant U as 用户
    participant T as Telegram Bot
    participant R as 推荐引擎
    participant C as 内容池
    participant P as 用户画像
    participant K as 知识库

    U->>T: /brush (开始刷博客)
    T->>R: 请求推荐 1 条
    R->>P: 读取用户画像
    R->>C: 按分数排序取 Top1
    R-->>T: 返回博客卡片
    T-->>U: 展示卡片 + 按钮
    
    alt 👍 感兴趣
        U->>T: 点击 👍
        T->>P: 更新兴趣 (+2)
        T->>R: 请求下一条（偏相似）
    else 📖 深度阅读
        U->>T: 点击 📖
        T-->>U: 展开摘要 + 原文链接
        T->>P: 更新兴趣 (+3)
    else 💾 收藏
        U->>T: 点击 💾
        T->>K: 结构化存储
        T->>P: 更新兴趣 (+5)
    else 👎 划走
        U->>T: 点击 👎
        T->>P: 更新兴趣 (-1)
        T->>R: 请求下一条（偏不同）
    end
```

---

## 4️⃣ 冷启动流程设计

### 阶段一：首次使用引导

```
用户发送 /brush
    ↓
检测：用户画像是否存在？
    ↓ 不存在（新用户）
展示欢迎语:
  "👋 欢迎来到刷博客！
   我先推几篇不同领域的文章，
   你告诉我哪些感兴趣 👇"
    ↓
推送 6 条种子内容（每个领域 1 条）:
  🖥️ 技术  🧠 AI  💰 商业
  🎨 设计  🌍 科学  📚 人文
    ↓
用户选择 ≥2 个感兴趣的领域
    ↓
初始化用户画像
    ↓
进入正常推荐流
```

### 阶段二：快速学习期（第 1-20 次交互）
- 推荐公式临时调整：Diversity 权重提升到 0.4
- 每 5 次交互后重新计算兴趣向量
- 显示 "还在了解你的口味..." 提示

### 阶段三：稳定推荐期（第 20+ 次交互）
- 恢复正常权重配比
- 引入兴趣衰减
- 每周生成一次 "本周阅读报告"

---

## 5️⃣ 技术栈确认

| 模块 | 技术选型 | 说明 |
|------|----------|------|
| 交互引擎 | Moltbot Skill + Telegram Bot API | 按钮交互 |
| 内容采集 | Python + feedparser | RSS 解析 |
| 推荐引擎 | Python + scikit-learn | TF-IDF + 余弦相似度 |
| 数据存储 | SQLite + JSON | 轻量级，易部署 |
| 知识沉淀 | Notion API | 结构化存储 |
| 用户画像 | JSON 文件 | 易读写，易备份 |

---

## 6️⃣ 文件结构（给 CodeX）

```
brush-blog-skill/
├── PLAN.md              ← 你在这里
├── PRODUCT.md           ← 产品需求文档
├── HANDOFF.md           ← Agent 交接文档
├── src/
│   ├── main.py          ← Moltbot Skill 入口
│   ├── fetcher/         ← 模块 A: 内容采集
│   │   ├── rss.py
│   │   └── cleaner.py
│   ├── interaction/     ← 模块 B: 交互引擎
│   │   └── telegram.py
│   ├── recommend/       ← 模块 C: 推荐引擎
│   │   ├── scorer.py
│   │   └── embedder.py
│   ├── tracker/         ← 模块 D: 行为收集
│   │   └── behavior.py
│   └── sink/            ← 模块 E: 知识沉淀
│       └── notion.py
├── data/
│   ├── feeds.json       ← RSS 源配置
│   ├── content.db       ← 内容池 (SQLite)
│   └── profiles/        ← 用户画像
└── config.yaml          ← 全局配置
```

---

## 7️⃣ 里程碑计划

| 里程碑 | 交付物 | 预计时间 |
|--------|--------|----------|
| M1: 骨架搭建 | 文件结构 + 配置文件 | 1 天 |
| M2: 内容采集 | RSS 读取 + 清洗 | 1 天 |
| M3: 交互引擎 | Telegram 按钮 + 卡片展示 | 2 天 |
| M4: 推荐引擎 | TF-IDF + 简单排序 | 2 天 |
| M5: 行为收集 | 用户画像 + 兴趣更新 | 1 天 |
| M6: 知识沉淀 | Notion 存储 | 1 天 |
| M7: 冷启动 | 新用户引导流程 | 1 天 |
| M8: 测试发布 | VPS 测试 + ClawdHub 发布 | 2 天 |

**总计**: 约 11 天（可并行）

---

## 8️⃣ 下一步

**交给 Codex**: 按照文件结构开始编码，从 M1 骨架搭建开始。

**验收标准**:
- [ ] 所有模块文件创建完成
- [ ] config.yaml 配置完整
- [ ] feeds.json 包含至少 15 个 RSS 源（每类 3 个）
- [ ] main.py 能跑通 /brush 命令（即使返回假数据）
