# Notion 同步文案（M1 完成）

## 里程碑
- M1: 骨架搭建 ✅ 完成（已通过 VPS 复测）

## 当前状态
- 阶段：M1 完成 → M2 待启动
- 进度：100%
- 代码版本：`bf83d92`

## M1 交付物
- 模块骨架已完成：`src/fetcher`、`src/interaction`、`src/recommend`、`src/tracker`、`src/sink`
- Skill 入口已完成：`SKILL.md`（可调用 `/brush`）
- 命令入口已完成：`src/main.py`（含 `handle_command`）
- 配置已完成：`config.yaml`
- RSS 源已完成：`data/feeds.json`（包含优先组 `priority_hn_popular_2025`）
- 测试手册已完成：`docs/CLAW_MANAGER_TEST_MANUAL.md`

## 验收结果
- VPS 测试路径：`/home/admin/clawd/github/brush-blog-skill`
- 测试命令：`python3 src/main.py /brush`
- 结果：PASS（exit code 0）
- 关键现象：
  - 正常输出博客卡片与按钮
  - 来源命中优先 RSS 源（`simonwillison.net`）

## 风险与说明
- 低优先级：部分场景未显示“原文：...”行（M1 mock 回退路径），不阻塞 M1 验收。
- 处理计划：M2 实现真实 RSS 批量采集与内容池读取后消除该差异。

## 下一步（M2）
- 实现真实 RSS 批量抓取（优先组 3 个源）
- 写入 `data/content.db` 内容池
- `/brush` 优先从内容池返回文章卡片，RSS 直连作为回退
