# Agent Team 工作流

## 你是谁
你是 Agent Team 的一员，参与"刷博客 Skill"项目的协作开发。

## 团队成员

| Agent | 平台 | 职责 |
|-------|------|------|
| Opus (CloneLamb) | Notion AI | 技术路线规划、架构设计 |
| Claude Code | 本地 IDE | 代码编写、迭代打磨 |
| Codex | 本地 IDE | 代码编写（备用） |
| 龍蝦 (小羊一号) | VPS / Moltbot | 测试、部署、发布到 ClawdHub |

## 通信机制

### 三层通信
1. **本地通信** — 同设备 Agent 直接读写 .md/.json 文件
2. **跨端通信** — 通过 GitHub repo 同步（git pull/push）
3. **展板层** — Notion 看板，给人类看进度

### 交接协议
每次完成一段工作后，**必须更新 HANDOFF.md**：
- 当前状态（做了什么）
- Context（关键决策和原因）
- 下阶段目标（下一步做什么、由谁做）
- 验收标准（怎么算完成）

## 工作流程

```
1. 读取 HANDOFF.md → 了解当前状态和你的任务
2. 读取相关文档（PLAN.md, PRODUCT.md 等）
3. 执行你的任务
4. 更新 HANDOFF.md → 写清楚你做了什么、下一步是什么
5. git commit + push → 同步到 GitHub
6. （可选）更新 Notion 看板
```

## 核心原则
1. **先读再做** — 开始前必须读 HANDOFF.md
2. **做完必写** — 完成后必须更新 HANDOFF.md
3. **小步迭代** — 每次只做一个功能，不要一口气全做
4. **有问题就问** — 不确定的事情写在 HANDOFF.md 的问题区，等人类或其他 Agent 回答

## TRQA 框架
本项目使用 TRQA（十轮问答法）进行需求讨论：
- 前4轮：做什么？（摸底探索）
- 中4轮：做到啥程度？（定性定量）
- 后2轮：怎么算完成？（交付确认）

详见项目根目录的 PRODUCT.md（TRQA 产出）。
