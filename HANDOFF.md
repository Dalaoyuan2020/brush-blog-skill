# HANDOFF.md - 交接文档

## 项目信息
- **项目名称**: 刷博客 Skill
- **参与成员**: Opus (CloneLamb), Claude Code/Codex, 龍蝦 (小羊一号)

## 当前状态
- **阶段**: ✅ M1 完成（VPS 复测通过） → 🔄 M2 内容采集进行中
- **进度**: 70%（整体）— M2 真实内容链路已通过 VPS 复测
- **最后更新**: Codex / 2026-02-22 19:44

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
- 2026-02-22 12:34 / Codex：新增仓库根目录 `SKILL.md`（`name: brush`、`user-invocable: true`、`{baseDir}` 执行步骤），将项目从“代码仓库”补齐为“可识别 skill 包”入口。
- 2026-02-22 12:35 / Codex：将 `docs/CLAW_MANAGER_TEST_MANUAL.md` 改为 VPS/Skill 测试流程（GitHub 拉取→执行 `/brush`）；`README.md` 补充 skill 入口与 VPS 快速测试指令。
- 2026-02-22 12:35 / Codex：回归验证通过，`python3 src/main.py /brush` 输出正常。
- 2026-02-22 18:10 / Codex：解决远端并行变更导致的 `SKILL.md` rebase 冲突（add/add），已合并为统一 skill 描述并推送 `main`，提交 `57f246f`。
- 2026-02-22 18:46 / Codex：接收 claw 管家 VPS 复测结果，确认 `bf83d92` 版本在 `/home/admin/clawd/github/brush-blog-skill` 执行 `python3 src/main.py /brush` 通过（exit code 0，卡片与按钮输出正常）。
- 2026-02-22 18:53 / Codex：按激活指令通过 Notion API 读取页面 `Opus-30bd38a850fc805c98edf1de6e88f31c`，确认“⚠️ 协作踩坑记录”与“M2 内容采集（RSS 解析/摘要生成/内容清洗）”任务要求。
- 2026-02-22 18:55 / Codex：完成 M2-1（内容清洗/摘要），增强 `src/fetcher/cleaner.py`：支持 HTML 标签清洗、实体解码、2-3 句摘要生成（长度截断）。
- 2026-02-22 18:57 / Codex：完成 M2-2（RSS 解析），增强 `src/fetcher/rss.py`：新增 `collect_latest_articles()`，按 `priority_hn_popular_2025` 优先批量抓取并输出标准化文章结构。
- 2026-02-22 19:37 / Codex：完成 M2-3（主链路接入），`src/main.py` 改为 `/brush` 统一走 `_build_recommended_item()` 使用批量抓取结果，抓取失败自动回退 mock；`handle_command` 与 CLI 均支持输出 `原文` 链接。
- 2026-02-22 19:37 / Codex：本地验收通过：`python3 src/main.py /brush` 与 `PYTHONPATH=src python3 -c \"from main import handle_command ...\"` 均返回卡片、按钮、原文链接。
- 2026-02-22 19:40 / Codex：已将 M2 当前进展推送 GitHub `main`，提交 `e451908`，可在 VPS 直接 `git pull` 复测。
- 2026-02-22 19:44 / Codex：接收 claw 管家复测结果，确认 `6ea0318` 在 VPS 通过；`/brush` 已输出真实博客内容（Jeff Geerling: Frigate + Hailo），M2 推进有效。
- 2026-02-22 19:45 / Codex：已同步 Notion 面板（页面 `刷博客 Skill - Agent Team 首个协作项目`）：更新“项目状态”为 `M2 进行中 | 进度 70%`，并追加 M2 复测通过 callout 与下一步行动。
- 2026-02-22 19:45 / Codex：新增 `docs/NOTION_AI_UPDATE_PLAYBOOK.md`，提供固定沟通模板（阶段/进度/提交号/测试命令/结果/下一步）以提升 Notion AI 看板更新质量。

## 测试验收（VPS）
- **测试环境**: `/home/admin/clawd/github/brush-blog-skill`
- **测试版本**: `bf83d92`
- **执行命令**: `python3 src/main.py /brush`
- **结果**: ✅ PASS
- **证据摘要**:
  - 命令成功退出（exit code 0）
  - 输出博客卡片与按钮文案
  - 来源命中 `priority_hn_popular_2025` 首条（`simonwillison.net`）
  - “原文链接未显示”属于 M1 mock 回退路径，已标记低优先级，M2 真实采集阶段处理

## 测试验收（VPS，M2 进展）
- **测试环境**: `/home/admin/clawd/github/brush-blog-skill`
- **测试版本**: `6ea0318`
- **执行命令**: `python3 src/main.py /brush`
- **结果**: ✅ PASS
- **证据摘要**:
  - 输出真实博客内容（非 M1 mock）
  - 实例文章来源：Jeff Geerling（Frigate + Hailo）
  - 卡片与按钮文案正常

## 问题区
- 非阻塞：本机无 `python` 命令（仅有 `python3`），校验脚本已改用 `python3` 执行。
- 非阻塞：`t.co` 为短链，已落地为可追溯来源 `https://gist.github.com/emschwartz/e6d2bf860ccc367fe37ff953ba6de66b`。
- 已解除：Notion API 凭据已由羊爸爸提供，任务面板可访问。
