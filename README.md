# 🦞 刷博客 Skill

**像刷抖音一样学顶级博客，一站式知识沉淀**

## 项目信息

- **平台**: Moltbot (Skill 形式)
- **数据源**: RSS（可扩展到 Twitter、YouTube）
- **推荐算法**: 规则+权重，先简单后优化
- **状态**: 🟡 开发中

## Agent Team 协作项目

这是 Agent Team 的首个协作项目，参与成员：

| Agent | 平台 | 职责 |
|-------|------|------|
| Opus (CloneLamb) | Notion AI | 技术路线规划 |
| Claude Code | 线下 | 代码编写、迭代 |
| 龍蝦 (小羊一号) | VPS / Moltbot | 测试、部署、发布 |

## 项目结构

```
brush-blog-skill/
├── README.md              ← 项目说明
├── HANDOFF.md             ← 交接文档（Agent 间接力棒）
├── PLAN.md                ← Opus 产出的技术路线
├── PRODUCT.md             ← TRQA 产出的产品文档
├── AGENT_WORKFLOW.md      ← Agent Team 工作流说明
├── src/                   ← 代码
└── tests/                 ← 测试
```

## 通信机制

- **本地**: 同设备 Agent 直接读写 .md 文件
- **跨端**: GitHub repo 同步
- **展板**: Notion 看板（人类可视）
