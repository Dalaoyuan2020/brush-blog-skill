---
name: brush
description: 像刷抖音一样学顶级博客，一站式知识沉淀。Use this skill for /brush blog discovery.
user-invocable: true
metadata: {"clawdbot":{"emoji":"🦞"},"openclaw":{"emoji":"📰","homepage":"https://github.com/Dalaoyuan2020/brush-blog-skill","requires":{"anyBins":["python3"]},"supports":{"inlineButtons":true}}}
---

# 🦞 刷博客 Skill

像刷抖音一样学顶级博客，一站式知识沉淀。

## 命令

- `/brush` - 开始刷博客
- `/brush like` - 标记感兴趣并推荐下一条
- `/brush skip` - 划走并推荐下一条
- `/brush read` - 展开当前文章深度阅读
- `/brush save` - 收藏并沉淀到知识库（本地 JSONL，可选 Notion）
- `/brush refresh` - 换一批推荐
- `/brush choose <tech|ai|biz|design|science|popular>` - 冷启动阶段直接选择兴趣分类
- `/brush start` - 冷启动选满 2 类后进入智能推荐

新用户首次执行 `/brush` 会自动进入冷启动：可点击分类按钮选择 2-3 个兴趣领域，也可继续对当前领域点 `👍`。选满 2 类后可点 `✅ 开始推荐`，系统将进入 20 次快速学习期。

## 执行流程（当前已实现）

1. 执行命令：
   `python3 {baseDir}/src/main.py /brush`
2. 若 `python3` 不可用，回退：
   `python {baseDir}/src/main.py /brush`
3. 将命令输出直接回传给用户。

## 输出预期

- 以 `📰 博客卡片` 开头
- 包含按钮提示：
  `[👍 感兴趣] [👎 划走] [📖 深度阅读] [💾 收藏] [🔄 换一批]`
- RSS 抓取成功时包含 `原文：<url>`
- `/brush save` 成功后包含沉淀结果（本地或 Notion）

## 数据优先级

优先读取 `priority_hn_popular_2025`：
`{baseDir}/data/feeds.json`

## 失败处理

- RSS/网络失败：回退假数据卡片，命令不崩溃。
- 命令执行失败：返回错误摘要并提示重试。
