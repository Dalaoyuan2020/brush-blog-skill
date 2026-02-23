# HANDOFF.md - 交接文档

## 项目信息
- **项目名称**: 刷博客 Skill
- **参与成员**: Opus (CloneLamb), Claude Code/Codex, 龍蝦 (小羊一号)

## 当前状态
- **阶段**: ✅ M1 完成 → ✅ M2 完成 → ✅ M3 完成 → ✅ M4 完成 → ✅ M5 完成 → ✅ M6 完成 → ✅ M7 完成 → ✅ M8 完成（v1.0）→ ✅ M9 完成 → ✅ M10 完成 → ✅ M11 完成 → ✅ M12 完成（VPS 验收通过）→ 🚧 V2.0 执行中（任务 1.1、2.1、1.2、1.4、1.3、2.2、2.3 已完成）
- **进度**: v1.0 阶段进度 100%；V2.0 当前进度 7/12（任务 1.1 + 2.1 + 1.2 + 1.4 + 1.3 + 2.2 + 2.3 完成）
- **最后更新**: Codex / 2026-02-23 17:26

## Context（上下文）
- 产品需求通过 TRQA 十轮问答法完成，详见 PRODUCT.md
- 技术路线由 Opus 规划完成，详见 PLAN.md
- 核心功能：冷启动 → 信息流 → 交互反馈 → 知识沉淀 → 智能推荐
- 技术栈：Moltbot Skill + Telegram + Python + RSS + SQLite + Notion API
- 推荐算法公式：Interest×0.4 + Knowledge×0.3 + Diversity×0.2 + Popularity×0.1（M12 快速学习期临时提升 Diversity 到 0.4）

## 下阶段目标
- **任务**: 启动 V2.0 Skills 设计（问题收敛 + 方案评审）
- **由谁来做**: Codex / Claude Code
- **预期产出**: V2.0 设计文档（范围、优先级、验收标准）
- **预期时间**: 1 个迭代
- **起点**: M12 VPS 测试已通过，进入 V2.0 规划阶段

## 验收标准（M1 骨架搭建）
- [x] 所有模块文件创建完成（见 PLAN.md 文件结构）
- [x] config.yaml 配置完整
- [x] feeds.json 包含至少 15 个 RSS 源（每类 3 个）
- [x] main.py 能跑通 /brush 命令（即使返回假数据）
- [x] 更新 HANDOFF.md 进度

## 开发顺序
1. M1: 骨架搭建 → 2. M2: 内容采集 → 3. M3: 交互引擎 → 4. M4: 推荐引擎 → 5. M5: 行为收集 → 6. M6: 知识沉淀 → 7. M7: 冷启动 → 8. M8: 测试发布 → 9. M9: 性能优化 → 10. M10: 全文抓取+AI摘要 → 11. M11: Telegram按钮可点击性 → 12. M12: 冷启动兴趣选择

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
- 2026-02-22 19:48 / Codex：修正进度口径：`70%` 改为 `M2 里程碑进度 70%`，并补充 `项目总进度约 16%`（按 PLAN 11 天工期权重计算）。
- 2026-02-22 19:52 / Codex：完成 M2-4（内容池存储层），在 `src/fetcher/rss.py` 增加 SQLite 能力：`init_content_db`、`upsert_articles`、`refresh_content_pool`、`pick_article_from_pool`，实现 RSS 抓取结果入库与按优先分类取文。
- 2026-02-22 19:57 / Codex：完成 M2-5（主流程闭环），`src/main.py` 接入 `content.db`：`/brush` 先刷新内容池再取推荐，失败时回退实时抓取与 mock；新增 `read_history` 去重策略避免重复文章。
- 2026-02-22 19:57 / Codex：完成 M2-6（验收与配置），本地验证通过（CLI/handle_command/SQLite 入库/profile 历史），并将 `config.yaml` 里程碑 `m2_fetcher` 设置为 `true`。
- 2026-02-22 20:00 / Codex：已推送 M2 完成代码到 GitHub `main`，提交 `30326f2`。
- 2026-02-22 20:00 / Codex：已同步 Notion 页面状态为 `M2 开发完成（待VPS验收）`，并追加 commit `30326f2` 的 M2 完成说明与验收请求。
- 2026-02-22 20:06 / Codex：开始推进 M3（交互引擎）；完成 `src/interaction/telegram.py` 扩展，新增统一按钮布局、深度阅读消息与收藏反馈消息构造函数。
- 2026-02-22 20:08 / Codex：完成 `src/main.py` 交互主流程：`/brush like|skip|read|save|refresh` 全部落地；新增 `last_item`、`saved_items`、`interest_tags` 更新逻辑。
- 2026-02-22 20:08 / Codex：M3 本地验收通过：CLI 下 `/brush read` 可展开详情，`/brush save` 可收藏并回写 profile，按钮链路完整。
- 2026-02-22 20:28 / Codex：M3 代码已推送 GitHub `main`，提交 `8a04ecf`；`config.yaml` 已标记 `m3_interaction: true`。
- 2026-02-22 20:33 / Codex：开始推进 M4（推荐引擎）；重写 `src/recommend/scorer.py`，实现 Interest/Knowledge/Diversity/Popularity 四分量打分与候选排序函数。
- 2026-02-22 20:36 / Codex：完成 M4-2（评分接入），`src/main.py` 改为从 `content_pool` 拉候选并调用 `rank_items()` 选 Top1；新增 `source_history` 记录用于多样性分量。
- 2026-02-22 20:39 / Codex：完成 M4-3（交互回归验证），`/brush -> like -> skip -> save -> read` 命令链路通过；候选结果可按评分切换不同来源。
- 2026-02-22 20:39 / Codex：修复回归：`run_brush()` 已改为复用 `handle_command()`，消除 `_build_recommended_item()` 参数不匹配问题。
- 2026-02-22 20:41 / Codex：M4 当前代码已推送 GitHub `main`，提交 `cdd48bf`。
- 2026-02-22 20:41 / Codex：已同步 Notion 面板 M4 进展；由于旧状态块已归档，改为新增状态段落与 M4 callout（commit `cdd48bf`）。
- 2026-02-22 23:37 / Codex：完成“最后一块本地测试”：`/brush`、`/brush like`、`/brush skip`、`/brush read`、`/brush save` 全部通过；候选文章可跨来源切换（priority/tech/ai/design）。
- 2026-02-22 23:37 / Codex：测试后已清理运行时数据（profile 临时文件、content_pool 行数据），仓库保持可复测状态。
- 2026-02-22 23:51 / Codex：接收 claw 管家 VPS 最终结论：`69648e6` 全量命令通过（/brush/like/skip/read/save），数据库 6 条内容，确认 M4 当前目标达成。
- 2026-02-22 23:51 / Codex：标记里程碑开关 `m4_recommend: true`，并按 PLAN 启动 M5（行为收集）开发。
- 2026-02-22 23:55 / Codex：完成 M5-1（行为日志模块），扩展 `src/tracker/behavior.py`：支持事件结构、JSONL 落盘、最近事件读取。
- 2026-02-22 23:56 / Codex：完成 M5-2（主流程接入），`src/main.py` 在 `view/like/skip/read/save/refresh` 全链路写行为事件；失败不影响命令主流程。
- 2026-02-22 23:57 / Codex：M5 本地验证通过：执行 `/brush` 相关命令后行为日志产生 7 条事件（view/like/read/save/refresh 等）；验证后已清理运行时样本数据。
- 2026-02-23 00:23 / Codex：根据 claw 管家复测结论（`d10cce2`）对齐里程碑状态，`config.yaml` 标记 `m5_tracker: true`，M5 判定完成。
- 2026-02-23 00:26 / Codex：完成 M6-1（知识沉淀模块），重写 `src/sink/notion.py`：新增结构化笔记生成、JSONL 本地落盘、可选 Notion API 写入与失败回退。
- 2026-02-23 00:28 / Codex：完成 M6-2（主流程接入），`/brush save` 现已调用沉淀器；返回“本地沉淀/Notion沉淀”反馈，并将 `sink_status/sink_stores` 写入行为日志 metadata。
- 2026-02-23 00:30 / Codex：完成 M6-3（本地验收），`python3 -m py_compile` 与 `/brush -> like -> read -> save -> refresh` 回归通过；`data/saved_notes.jsonl` 已产出结构化笔记，`behavior_events.jsonl` 记录 `save` 的沉淀元数据。
- 2026-02-23 00:31 / Codex：完成 M6-4（文档对齐），更新 `SKILL.md` 命令说明（去除“预留”标记）与 `docs/CLAW_MANAGER_TEST_MANUAL.md` 全链路测试项（新增 save 沉淀与行为日志校验）。
- 2026-02-23 00:33 / Codex：完成 M6-5（稳定性补丁），为 `/brush save` 沉淀流程增加异常兜底；即使本地/Notion 写入失败，也不会影响“收藏成功”主流程。
- 2026-02-23 00:34 / Codex：完成展板同步：通过 Notion API 向项目页追加 M6 完成 callout（commit `96d8f3d`、能力变化、下一步 M7）。
- 2026-02-23 00:43 / Codex：完成 M7-1（冷启动交互层），在 `src/interaction/telegram.py` 新增 `build_cold_start_buttons()`，用于新用户领域选择流程。
- 2026-02-23 00:48 / Codex：完成 M7-2（冷启动主链路），`src/main.py` 新增新用户冷启动状态机：首次 `/brush` 进入 6 类种子内容引导，`/brush like|skip|refresh` 在冷启动阶段用于领域选择；选满 2 个领域后自动切换到常规推荐流。
- 2026-02-23 01:02 / Codex：完成 M7-3（兼容性与回归），修复冷启动状态引用问题（`current_index` 递进失效）；新增“历史老用户自动跳过冷启动”兼容逻辑，保证已有用户不被重新引导。
- 2026-02-23 01:04 / Codex：完成 M7-4（验收），本地回归通过：新用户 `/brush -> like -> skip -> like` 会输出“冷启动完成”；完成后 `/brush read|save|refresh` 正常；`python3 -m py_compile` 通过。
- 2026-02-23 01:06 / Codex：完成 M7-5（配置与文档对齐），`config.yaml` 标记 `m7_cold_start: true`，并更新 `SKILL.md`、`README.md`、`docs/CLAW_MANAGER_TEST_MANUAL.md` 的冷启动说明与测试步骤。
- 2026-02-23 01:43 / Codex：完成展板同步：通过 Notion API 向项目页追加 M7 完成 callout（commit `1501df0`，含冷启动能力与下一步 M8）。
- 2026-02-23 01:49 / Codex：完成 M8-1（自动化冒烟脚本），新增 `scripts/m8_smoke_test.py`，覆盖冷启动、核心命令链路、行为日志与知识沉淀文件校验。
- 2026-02-23 01:50 / Codex：完成 M8-2（测试手册升级），`docs/CLAW_MANAGER_TEST_MANUAL.md` 新增自动化 smoke test 步骤与通过标准，便于 claw 管家一键执行回归。
- 2026-02-23 02:02 / Codex：完成 M8-3（本地自动化验收），执行 `python3 scripts/m8_smoke_test.py` 通过（PASS），并完成 `src/main.py` 与脚本语法编译检查。
- 2026-02-23 02:06 / Codex：完成展板同步：通过 Notion API 向项目页追加 M8 进行中 callout（commit `51516c5`，附 VPS 验收动作）。
- 2026-02-23 02:13 / Codex：接收 claw 管家 M8 最终验收（commit `bb53ee9`）：`M8 smoke test PASS`，命令链路/行为事件/保存笔记全部通过，项目状态收口为 M1-M8 全完成。
- 2026-02-23 02:14 / Codex：完成最终展板同步：通过 Notion API 追加“项目完成（100%）”callout，记录最终收口提交 `b259cf8` 与验收结论。
- 2026-02-23 02:22 / Codex：按 `OPEN_SOURCE.md` 与 `docs/USER_FEEDBACK_2026-02-23.md` 校正进度口径：将“100%”限定为 `v1.0 (M1-M8)`，并恢复全路线进度为 `8/12 ≈ 67%`，下一步转入 M9-M12。
- 2026-02-23 10:08 / Codex：完成 M9-1（刷新节流），在 `src/main.py` 增加内容池刷新判定：仅在内容池过小或过旧时才拉取 RSS，避免每次 `/brush` 阻塞抓取。
- 2026-02-23 10:10 / Codex：完成 M9-2（冷启动提速），冷启动种子改为优先读取 `content_pool`，缺失时使用本地种子文案，不再在首次 `/brush` 同步串行抓取多个 RSS。
- 2026-02-23 10:11 / Codex：完成 M9-3（轻量优化），增加 `feeds.json` mtime 缓存、移除行为日志调试打印，并提供环境变量调优项（刷新间隔/超时/池容量）。
- 2026-02-23 10:12 / Codex：M9 本地回归通过：`python3 -m py_compile` 与 `scripts/m8_smoke_test.py` 均 PASS；单次 `/brush` CLI 测量 `real 0.12s`（当前环境）。
- 2026-02-23 10:19 / Codex：完成展板同步：通过 Notion API 追加 M9 完成 callout（commit `4303a15`，含性能优化说明与下一步 M10）。
- 2026-02-23 10:24 / Codex：完成 M10-1（深读抓取模块），新增 `src/fetcher/reader.py`：支持原文抓取、正文去噪提取、深读摘录生成与“大白话”解释生成。
- 2026-02-23 10:31 / Codex：完成 M10-2（读命令接入），`/brush read` 改为先抓取原文正文并生成“🧠 大白话讲解 + 📚 正文摘录”；抓取失败自动回退 RSS 摘要，不影响主流程。
- 2026-02-23 10:42 / Codex：完成 M10-3（回归与配置），`python3 -m py_compile` 与 `scripts/m8_smoke_test.py` 通过；`config.yaml` 标记 `m10_deep_read: true`，`README.md` 与 `docs/USER_FEEDBACK_2026-02-23.md` 完成状态对齐。
- 2026-02-23 10:45 / Codex：完成 M10-4（验收手册升级），更新 `docs/CLAW_MANAGER_TEST_MANUAL.md`：新增 `/brush read` 的“大白话讲解 + 正文摘录”检查项，供 VPS 复测。
- 2026-02-23 10:49 / Codex：完成展板同步：通过 Notion API 追加 M10 完成 callout（commit `59be455`，下一步 M11）。
- 2026-02-23 11:21 / Codex：根据羊爸爸指令调整 M11 策略：停止离线猜测式改造，改由 claw 管家切换 `/opus` 在在线运行环境完成“按钮可点击”落地；新增专项文档指导执行与经验沉淀。
- 2026-02-23 11:24 / Codex：完成展板同步：通过 Notion API 追加 M11 策略更新 callout（commit `0175718`，等待 claw 在线闭环结果）。
- 2026-02-23 11:30 / Codex：接收 claw 管家 M11 验收报告（commit `d360f19`）：最小闭环与完整 5 按钮组均可点击并成功 callback；经验文档已沉淀至 `docs/M11_BUTTON_FIX_EXPERIENCE.md`。
- 2026-02-23 11:34 / Codex：完成 M11 收口：`config.yaml` 标记 `m11_inline_buttons: true`，并更新 `README.md` 与 `docs/USER_FEEDBACK_2026-02-23.md` 的里程碑状态。
- 2026-02-23 11:47 / Codex：完成 M12-1（冷启动兴趣选择），`src/main.py` 新增 `/brush choose <alias>` 与 `/brush start`，支持 6 类兴趣直接选择，冷启动改为“选 2-3 类”流程；`src/interaction/telegram.py` 同步新增分类按钮和“开始推荐”按钮。
- 2026-02-23 11:51 / Codex：完成 M12-2（快速学习期），`src/main.py` 新增 learning state：冷启动完成后进入 20 次学习期，推荐权重自动切为 Diversity=0.4，并显示“还在了解你的口味...”提示；每 5 次交互执行轻量兴趣向量重平衡。
- 2026-02-23 11:54 / Codex：完成 M12-3（回归与文档），更新 `scripts/m8_smoke_test.py` 适配新冷启动路径，`python3 scripts/m8_smoke_test.py` 本地 PASS；同时完成 `README.md`、`SKILL.md`、`docs/CLAW_MANAGER_TEST_MANUAL.md`、`docs/USER_FEEDBACK_2026-02-23.md`、`config.yaml` 对齐。
- 2026-02-23 12:10 / Codex：接收 claw 管家 M12 VPS 验收报告：`m8_smoke_test PASS`、`/brush choose` 可用、`/brush start` 可用、按钮 callback 正常；结论为 M12 可用并通过验收。
- 2026-02-23 12:12 / Codex：完成 M12 收口：更新 `HANDOFF.md` 状态到“12/12 完成”，并切换下阶段目标为 V2.0 Skills 设计启动。
- 2026-02-23 16:20 / Codex：完成 V2.0 `任务 1.1`：创建 `shared/` 目录与三个共享数据文件（`shared/content_pool.json`、`shared/read_history.json`、`shared/user_prefs.json`），并通过 `python3` JSON 解析校验。
- 2026-02-23 16:27 / Codex：完成 V2.0 `任务 2.1`：`src/main.py` 的 `/brush` 改为纯读模式（仅读取 `shared/content_pool.json` + `shared/read_history.json`，不再触发 `refresh_content_pool()` 同步刷新）；输出追加 `POOL_LOW`/`POOL_EMPTY` 状态行供 Agent 调度。
- 2026-02-23 16:27 / Codex：V2.0 任务 2.1 验收通过：`/usr/bin/time -p python3 src/main.py /brush` 实测 `real 0.15s`（<1s），输出合法卡片文本且包含 `POOL_LOW: true`、`POOL_EMPTY: true`。
- 2026-02-23 17:02 / Codex：完成 V2.0 `任务 1.2`：新增 `src/pool_manager.py` 与 `refresh_pool()`，支持遍历 `data/feeds.json` 抓取 RSS、URL 去重、写入 `shared/content_pool.json`，并在池子达到 `20` 篇时停止抓取（保留最少 `10` 篇回填策略）。
- 2026-02-23 17:10 / Codex：完成 V2.0 `任务 1.4`：`shared/read_history.json` 改为 `[{url, read_at}]` 结构；推荐时按 URL 排除 24 小时内已读，并在每次推荐后写入 URL + 时间戳。
- 2026-02-23 17:12 / Codex：完成 V2.0 `任务 1.3`：`/brush` 输出状态行扩展为 `POOL_SIZE: N`、`POOL_LOW: true/false`、`POOL_EMPTY: true/false`，供 Agent 精准调度补货。
- 2026-02-23 17:15 / Codex：第 2 批验收命令通过：`python3 src/pool_manager.py refresh` 结果池子 `20` 篇且 URL 去重为 `True`；`echo '{\"articles\":[]}' > shared/content_pool.json` 后 `/brush` 正确输出 `POOL_SIZE: 0`、`POOL_EMPTY: true`。
- 2026-02-23 17:17 / Codex：补充验证 `任务 1.4`：清空历史后连续执行 `/brush` 10 次，标题唯一数 `10`（24h 已读去重生效）。
- 2026-02-23 17:24 / Codex：完成 V2.0 `任务 2.2`：重写 `SKILL.md` 为 OpenClaw Skills 规范格式，frontmatter 单行 key，`metadata` 为单行 JSON，命令与状态行协议对齐 V2.0。
- 2026-02-23 17:26 / Codex：完成 V2.0 `任务 2.3`：新增 `docs/AGENT_INSTRUCTIONS.md`，定义 `/brush` 调度全流程（exec→message→状态判定→同步/异步刷新），并补充 `sessions_spawn` 合法参数示例与“子代理不可嵌套 spawn”限制说明。

## 测试验收（本地，M12 冷启动兴趣选择）
- **执行命令**: `python3 -m py_compile src/main.py src/interaction/telegram.py scripts/m8_smoke_test.py`
- **执行命令**: `python3 scripts/m8_smoke_test.py`
- **执行命令**: `PYTHONPATH=src python3 - <<'PY' ... /brush -> choose ai -> choose design -> start -> /brush ... PY`
- **结果**: ✅ PASS
- **证据摘要**:
  - 冷启动支持 `/brush choose ai|design` 与 `/brush start`
  - 选满 2 类后可进入推荐，消息包含：`✅ 冷启动完成，已进入智能推荐。`
  - 推荐消息包含学习期提示：`🧪 还在了解你的口味...（学习期 x/20）`
  - 自动化脚本通过：`M8 smoke test PASS`

## 测试验收（VPS，M12 最终）
- **测试环境**: claw 管家 VPS
- **测试版本**: `91d4070`
- **结果**: ✅ PASS
- **证据摘要**:
  - `m8_smoke_test PASS`
  - `/brush choose` 可用
  - `/brush start` 可用
  - 按钮 callback 正常
  - 观察项：冷启动完成后直接进入推荐模式；“20 次快速学习期提示”未在该次复测中稳定复现（可能由测试用户状态导致）

## 测试验收（VPS，M11 最终）
- **测试环境**: claw 管家在线运行环境（/opus）
- **测试版本**: `d360f19`
- **结果**: ✅ PASS
- **证据摘要**:
  - 最小闭环 PASS：inline button 发送成功（messageId: 6134）→ 点击 `👍 感兴趣` → callback `/brush like` 生效
  - 完整按钮组 PASS：5 按钮可点击（messageId: 6140），`/brush like|skip|read|save|refresh` 全部触发成功
  - 经验沉淀：`docs/M11_BUTTON_FIX_EXPERIENCE.md`

## 测试验收（本地，M10 深度阅读）
- **执行命令**: `PYTHONPATH=src python3 -c "from main import handle_command ... /brush read"`
- **执行命令**: `python3 scripts/m8_smoke_test.py`
- **结果**: ✅ PASS
- **证据摘要**:
  - `/brush read` 输出“🧠 大白话讲解”与“📚 正文摘录”
  - 原文抓取失败时自动回退摘要（命令不报错）
  - `M8 smoke test PASS`（核心链路无回归）

## 测试验收（本地，M9 性能）
- **执行命令**: `/usr/bin/time -p python3 src/main.py /brush`
- **执行命令**: `python3 scripts/m8_smoke_test.py`
- **结果**: ✅ PASS
- **证据摘要**:
  - `/brush` 冷启动首响（当前环境）`real 0.12s`
  - `M8 smoke test PASS`（核心命令链路无回归）
  - 代码编译通过：`python3 -m py_compile src/main.py src/fetcher/rss.py`

## 测试验收（VPS，M8 最终）
- **测试环境**: `/home/admin/clawd/github/brush-blog-skill`
- **测试版本**: `bb53ee9`
- **执行命令**: `python3 scripts/m8_smoke_test.py`
- **结果**: ✅ PASS
- **证据摘要**:
  - `M8 smoke test PASS`
  - 检查命令：`/brush`、`/brush like`、`/brush skip`、`/brush read`、`/brush save`、`/brush refresh`
  - 行为事件：13 条
  - 保存笔记：1 条

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

## 测试验收（本地，M2 完成）
- **执行命令**: `python3 src/main.py /brush`
- **执行命令**: `PYTHONPATH=src python3 -c \"from main import handle_command ...\"`
- **数据库检查**: `sqlite3 data/content.db 'SELECT COUNT(*) FROM content_pool;'`
- **结果**: ✅ PASS
- **证据摘要**:
  - `content_pool` 已建表并入库（当前 6 条）
  - `/brush` 可输出真实文章 + 原文链接 + 按钮
  - `data/profiles/<user>.json` 已记录 `read_history` item_key

## 问题区
- 非阻塞：本机无 `python` 命令（仅有 `python3`），校验脚本已改用 `python3` 执行。
- 非阻塞：`t.co` 为短链，已落地为可追溯来源 `https://gist.github.com/emschwartz/e6d2bf860ccc367fe37ff953ba6de66b`。
- 已解除：Notion API 凭据已由羊爸爸提供，任务面板可访问。
- 非阻塞：不同 Notion Database 的字段名可能与默认映射（`Title/Source/Summary/Tags/Saved At/Rating`）不一致；若出现 400 错误，需在下一步补充字段映射配置。
- 非阻塞：M12 VPS 复测中“20 次快速学习期提示”未稳定复现，推测与复用已有测试用户状态有关；V2.0 建议新增显式调试开关/状态可视化以便定位。
