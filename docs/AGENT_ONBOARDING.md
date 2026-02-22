# 🦞 Agent Team 新成员入职指南

**欢迎加入 Agent Team！**

这是你的第一个协作项目。请先读完这个文档，了解如何在团队中工作。

---

## 📚 核心文档

开始工作前，必须阅读：

1. **PRODUCT.md** - 产品需求（TRQA 十轮问答产出）
2. **PLAN.md** - 技术路线（Opus 规划）
3. **HANDOFF.md** - 交接文档（**每次工作前后都要读/写**）
4. **SKILL_TEMPLATE.md** - Moltbot Skill 开发模板

---

## 🔄 工作流程

### 开始工作前

1. **读取 HANDOFF.md**
   - 了解当前阶段（M1/M2/M3...）
   - 找到分配给你的任务
   - 看清楚验收标准

2. **读取相关文档**
   - PRODUCT.md（产品需求）
   - PLAN.md（技术设计）
   - 已有代码（了解现状）

3. **确认理解**
   - 如果有疑问，写在 HANDOFF.md 的"问题区"
   - 等人类或其他 Agent 回答后再开始

### 工作中

1. **小步迭代**
   - 每次只做一个小功能
   - 不要一口气全做

2. **及时提交**
   - 完成一个小功能就 git commit + push
   - 提交信息写清楚做了什么

3. **遇到问题**
   - 先尝试自己解决
   - 解决不了 → 写在 HANDOFF.md 问题区

### 完成工作后

**这是最重要的环节！**

1. **更新 HANDOFF.md**
   ```markdown
   ## 开发日志
   - 日期 / Agent：做了什么
   - 日期 / Agent：完成了什么
   ```

2. **更新进度**
   ```markdown
   ## 当前状态
   - 阶段：M1 完成 → M2 进行中
   - 进度：30%
   ```

3. **写下阶段总结**
   - 完成了什么
   - 遇到什么问题
   - 下一步建议

4. **同步到 Notion**（如果配置了）
   - 更新项目看板
   - 通知下一个 Agent

---

## 📝 代码规范

### Python 版本
- **目标版本**: Python 3.6+（兼容 VPS 环境）
- **不要用**: `from __future__ import annotations`
- **不要用**: `str | None`（用 `Optional[str]`）
- **不要用**: `dict[str, Any]`（用 `Dict[str, Any]`）

### 提交信息格式
```
🦞 M1 完成：添加 SKILL.md + handle_command 函数
🧠 add: Opus 完成 PLAN.md 技术路线规划
📚 add: Moltbot Skill 开发指南
```

### 文件结构
```
brush-blog-skill/
├── SKILL.md          ← Skill 定义（必需）
├── src/main.py       ← 入口（必需）
├── config.yaml       ← 配置
├── data/             ← 数据
└── docs/             ← 文档
```

---

## 🧪 测试规范

### 本地测试
```bash
cd /path/to/brush-blog-skill
python3 src/main.py /brush
```

### 测试检查项
- [ ] 命令是否成功退出（exit code 0）
- [ ] 是否输出博客卡片
- [ ] 是否输出按钮文案
- [ ] 来源是否来自 priority_hn_popular_2025

### 测试报告模板
```
📋 测试结果：PASS/FAIL

✅ 检查项：
1) 命令退出码：PASS
2) 卡片输出：PASS
3) 按钮文案：PASS
4) RSS 源：PASS

📝 问题：
- 无 / 问题描述

💡 建议：
- 建议内容
```

---

## 🤝 协作规范

### 和人类协作
- 人类是产品经理，你是开发者
- 需求不清楚就问，不要猜
- 完成一个功能就汇报，不要等全部做完

### 和其他 Agent 协作
- **Opus（Notion AI）**：技术规划师，它说怎么做就怎么做
- **Codex / Claude Code**：开发者，可以互相 review 代码
- **龍蝦（小羊一号）**：测试 + 部署，它负责验证和发布

### 交接给下一个 Agent
1. 确保 HANDOFF.md 更新完整
2. 确保代码能跑（至少不报错）
3. 在 Notion 上通知下一个 Agent

---

## 🎯 里程碑计划

| 里程碑 | 任务 | 负责 | 状态 |
|--------|------|------|------|
| M1 | 骨架搭建 | Codex | ✅ 完成 |
| M2 | 内容采集 | Codex | ⏳ 待开始 |
| M3 | 交互引擎 | Codex | ⏳ 待开始 |
| M4 | 推荐引擎 | Codex | ⏳ 待开始 |
| M5 | 行为收集 | Codex | ⏳ 待开始 |
| M6 | 知识沉淀 | Codex | ⏳ 待开始 |
| M7 | 冷启动 | Codex | ⏳ 待开始 |
| M8 | 测试发布 | 龍蝦 | ⏳ 待开始 |

---

## 📞 求助渠道

1. **HANDOFF.md 问题区** - 写问题，等回答
2. **Notion 项目页面** - 查看进度和决策
3. **GitHub Issues** - 提 issue（如果需要）

---

## 🎓 学习资源

- [Moltbot Skill 开发指南](../SKILL_TEMPLATE.md)
- [刷博客 Skill 产品文档](../PRODUCT.md)
- [技术路线](../PLAN.md)
- [OpenClaw 官方 Skills](https://github.com/openclaw/skills)

---

**记住：流程比进度重要！**

每次交接都走完整流程，即使是很小的任务。这样团队才能高效协作。

🦞 欢迎加入！
