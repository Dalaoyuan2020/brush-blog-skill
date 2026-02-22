# HANDOFF.md - 交接文档

## 项目信息
- **项目名称**: 刷博客 Skill
- **参与成员**: Opus (CloneLamb), Claude Code/Codex, 龍蝦 (小羊一号)

## 当前状态
- **阶段**: 🟢 M1 完成 → M2 预实现中（优先 RSS 源接入）
- **进度**: 100% — M1 已验收；已开始补充真实 RSS 取文链路
- **最后更新**: Codex / 2026-02-22 12:25

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
- [x] 所有模块文件创建完成（见 PLAN.md 文件结构）
- [x] config.yaml 配置完整
- [x] feeds.json 包含至少 15 个 RSS 源（每类 3 个）
- [x] main.py 能跑通 /brush 命令（即使返回假数据）
- [x] 更新 HANDOFF.md 进度

## 开发顺序
1. M1: 骨架搭建 → 2. M2: 内容采集 → 3. M3: 交互引擎 → 4. M4: 推荐引擎 → 5. M5: 行为收集 → 6. M6: 知识沉淀 → 7. M7: 冷启动 → 8. M8: 测试发布

## 开发日志（M1）
- 2026-02-22 11:55 / Codex：完成模块目录与文件骨架创建（`src/fetcher`、`src/interaction`、`src/recommend`、`src/tracker`、`src/sink`）。
- 2026-02-22 11:55 / Codex：完成 `config.yaml`，包含命令、数据路径、推荐参数、行为衰减、Notion 配置与里程碑开关。
- 2026-02-22 11:55 / Codex：完成 `data/feeds.json`，5 个分类共 15 个 RSS 源，并通过脚本校验每类 3 个。
- 2026-02-22 11:57 / Codex：完成 `src/main.py`，支持 `/brush` 命令并用假数据输出博客卡片；本地验证命令 `python3 src/main.py /brush` 通过。
- 2026-02-22 11:57 / Codex：补齐数据层骨架文件 `data/content.db` 与 `data/profiles/.gitkeep`，确保仓库结构与 `PLAN.md` 一致。
- 2026-02-22 12:00 / Codex：接入用户指定 RSS 信息源（`https://t.co/dwAiIjlXet` → Gist OPML），将其前 3 个 feed 写入 `data/feeds.json` 第一优先组 `priority_hn_popular_2025`。
- 2026-02-22 12:00 / Codex：增强 `src/fetcher/rss.py` 支持抓取 RSS/Atom 最新文章；`src/main.py` 改为 `/brush` 优先展示优先源真实文章，失败自动回退假数据。
- 2026-02-22 12:10 / Codex：新增 `docs/CLAW_MANAGER_TEST_MANUAL.md`，包含 claw 管家测试步骤、检查项、可复制指令、失败上报模板。
- 2026-02-22 12:10 / Codex：本地验证通过，`python3 src/main.py /brush` 已输出优先源真实文章（来源 `simonwillison.net`）及原文链接。
- 2026-02-22 12:25 / Codex：已提交并推送 M1 到 GitHub `main` 分支，提交 `7236976`，可在 VPS 直接 `git pull` 后运行测试。

## 问题区
- 非阻塞：本机无 `python` 命令（仅有 `python3`），校验脚本已改用 `python3` 执行。
- 非阻塞：`t.co` 为短链，已落地为可追溯来源 `https://gist.github.com/emschwartz/e6d2bf860ccc367fe37ff953ba6de66b`。
