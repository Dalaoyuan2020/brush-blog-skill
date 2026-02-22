# HANDOFF.md - 交接文档

## 项目信息
- **项目名称**: 刷博客 Skill
- **参与成员**: Opus (CloneLamb), Claude Code/Codex, 龍蝦 (小羊一号)

## 当前状态
- **阶段**: 🟢 规划完成 → 开发中
- **进度**: 20% — 产品需求 + 技术路线已完成，待编码实现
- **最后更新**: 龍蝦 / 2026-02-22 11:45

## Context（上下文）
- 产品需求通过 TRQA 十轮问答法完成，详见 PRODUCT.md
- 技术路线由 Opus 规划完成，详见 PLAN.md
- 核心功能：冷启动 → 信息流 → 交互反馈 → 知识沉淀 → 智能推荐
- 技术栈：Moltbot Skill + Telegram + Python + RSS + SQLite + Notion API
- 推荐算法公式：Interest×0.4 + Knowledge×0.3 + Diversity×0.2 + Popularity×0.1

## 下阶段目标
- **任务**: 编码实现（M1-M8 里程碑）
- **由谁来做**: Codex / Claude Code
- **预期产出**: 可运行的 Skill 代码
- **预期时间**: 约 11 天（可并行）
- **起点**: 从 M1 骨架搭建开始

## 验收标准（M1 骨架搭建）
- [ ] 所有模块文件创建完成（见 PLAN.md 文件结构）
- [ ] config.yaml 配置完整
- [ ] feeds.json 包含至少 15 个 RSS 源（每类 3 个）
- [ ] main.py 能跑通 /brush 命令（即使返回假数据）
- [ ] 更新 HANDOFF.md 进度

## 开发顺序
1. M1: 骨架搭建 → 2. M2: 内容采集 → 3. M3: 交互引擎 → 4. M4: 推荐引擎 → 5. M5: 行为收集 → 6. M6: 知识沉淀 → 7. M7: 冷启动 → 8. M8: 测试发布
