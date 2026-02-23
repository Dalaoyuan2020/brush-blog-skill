# claw 管家功能测试手册（刷博客 Skill / VPS 版）

## 1. 测试目标
验证刷博客 Skill 的核心链路可用：
- `/brush` 拉取推荐卡片
- `like/skip/read/save/refresh` 交互命令正常
- `save` 触发知识沉淀（本地 JSONL，Notion 可选）
- 行为事件落盘（`behavior_events.jsonl`）

## 2. 测试前准备
1. 在 VPS 获取最新版代码：
   ```bash
   git clone https://github.com/Dalaoyuan2020/brush-blog-skill.git
   cd brush-blog-skill
   git checkout main
   git pull origin main
   ```
2. 确认 `python3` 可用：
   ```bash
   python3 --version
   ```
3. 网络可访问外网 RSS 站点。

## 3. Skill 模式测试步骤（必须执行）
1. 执行：
   ```bash
   python3 src/main.py /brush
   python3 src/main.py /brush like
   python3 src/main.py /brush read
   python3 src/main.py /brush save
   python3 src/main.py /brush refresh
   ```
2. 预期输出包含：
   - `📰 博客卡片`
   - `按钮：[👍 感兴趣] ...`
   - `/brush read` 返回 `🧠 大白话讲解` 与 `📚 正文摘录`
   - `/brush save` 返回 `✅ 已收藏` 且包含 `已沉淀到...`
3. 优先源验证：
   - 正常网络下，输出应带 `原文：` 链接（真实文章）
   - `来源` 优先来自 `priority_hn_popular_2025`（首条默认是 `simonwillison.net`）
4. 行为/沉淀文件验证：
   ```bash
   tail -n 5 data/behavior_events.jsonl
   tail -n 3 data/saved_notes.jsonl
   ```
   - `behavior_events.jsonl` 包含 `view/like/read/save/refresh` 等事件
   - `saved_notes.jsonl` 至少新增 1 条结构化笔记（title/summary/tags/source_url）
5. 回退验证（可选）：
   - 断网或故意改错首条 RSS URL 后重跑
   - 预期仍能输出卡片（假数据回退），命令不崩溃

## 3.1 冷启动测试（M7，建议执行）
1. 使用全新用户（或删除对应 profile 文件）后执行：
   ```bash
   python3 src/main.py /brush
   python3 src/main.py /brush like
   python3 src/main.py /brush skip
   python3 src/main.py /brush like
   ```
2. 预期：
   - 首次 `/brush` 出现“欢迎 + 冷启动进度”文案
   - 冷启动阶段按钮为“这个领域感兴趣/下一个领域”
   - 选择满 2 个领域后输出：`✅ 冷启动完成，已进入智能推荐。`

## 3.2 M8 自动化 smoke test（推荐）
```bash
python3 scripts/m8_smoke_test.py
```

预期输出：
- `M8 smoke test PASS`
- 输出 checked commands / behavior events / saved notes 统计

## 4. claw 管家执行指令（可直接复制）

```text
请按“刷博客 Skill 功能测试手册（VPS版）”执行一轮功能测试，目标是验证 /brush 可用且优先使用指定 RSS 源。

仓库：https://github.com/Dalaoyuan2020/brush-blog-skill
分支：main

步骤：
1) git clone https://github.com/Dalaoyuan2020/brush-blog-skill.git
2) cd brush-blog-skill
3) git checkout main && git pull origin main
4) python3 src/main.py /brush

请你按以下检查项输出测试报告：
1) 命令是否成功退出（exit code）
2) 是否打印博客卡片与按钮文案
3) 是否打印原文链接（原文：...）
4) `/brush save` 是否输出收藏+沉淀文案
5) `/brush read` 是否包含“大白话讲解 + 正文摘录”
6) `behavior_events.jsonl` 是否记录 save 事件
7) `saved_notes.jsonl` 是否新增结构化笔记
8) 若失败，请给出失败步骤、报错原文、定位建议

报告格式：
- 结果：PASS/FAIL
- 证据：关键输出片段
- 问题列表：按严重级别排序
- 建议修复：每个问题 1 条可执行建议
```

## 5. 失败上报模板（给开发者）

```text
[FAIL] /brush 功能测试
时间：YYYY-MM-DD HH:MM
环境：本机 / python3 --version
步骤：
1. git clone ... && cd brush-blog-skill
2. git checkout main && git pull origin main
3. python3 src/main.py /brush

实际结果：
- ...

期望结果：
- 输出博客卡片、按钮文案，且优先源文章可见原文链接

错误日志：
- ...

初步判断：
- ...
```

## 6. 说明（Skill 结构）

- 本仓库已包含标准 skill 入口：`SKILL.md`
- `/brush` 对应 skill 名 `brush`（`user-invocable: true`）
- 运行逻辑通过 `python3 {baseDir}/src/main.py /brush` 执行
