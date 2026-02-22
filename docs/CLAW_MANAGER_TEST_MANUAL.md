# claw 管家功能测试手册（刷博客 Skill / VPS 版）

## 1. 测试目标
验证 `/brush` 命令在当前版本可用，并且优先采用用户指定 RSS 来源（`https://t.co/dwAiIjlXet` 对应 Gist OPML）中的文章。

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

## 3. Skill 模式最小测试步骤（必须执行）
1. 执行：
   ```bash
   python3 src/main.py /brush
   ```
2. 预期输出包含：
   - `📰 博客卡片`
   - `按钮：[👍 感兴趣] ...`
3. 优先源验证：
   - 正常网络下，输出应带 `原文：` 链接（真实文章）
   - `来源` 优先来自 `priority_hn_popular_2025`（首条默认是 `simonwillison.net`）
4. 回退验证（可选）：
   - 断网或故意改错首条 RSS URL 后重跑
   - 预期仍能输出卡片（假数据回退），命令不崩溃

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
4) 来源是否来自 priority_hn_popular_2025 首条源
5) 若失败，请给出失败步骤、报错原文、定位建议

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
