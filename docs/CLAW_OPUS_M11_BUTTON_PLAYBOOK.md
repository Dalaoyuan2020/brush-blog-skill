# M11 按钮可点击 - claw /opus 执行手册

## 背景

当前 `handle_command()` 已返回 `buttons + callback_data`，但在线体验里按钮仍不可点击。  
该问题更可能出在 **宿主运行时集成层**（Claw/Moltbot 对 skill 输出的接入方式），不是纯离线代码逻辑问题。

结论：M11 采用 **在线闭环**。
- 由 claw 管家切换 `/opus` 模型在 VPS 环境直接调试
- 修复后把可复用方法沉淀到本仓库文档

---

## 目标

让以下按钮在实际对话中可点击并触发回调：
- `👍 感兴趣`
- `👎 划走`
- `📖 深度阅读`
- `💾 收藏`
- `🔄 换一批`

---

## 执行步骤（给 claw 管家）

### 第 1 步：确认宿主能力

让 `/opus` 先确认三件事：
1. Skill 命令返回结构化数据时，宿主是否会解析 `buttons`
2. 宿主要求的按钮字段名（例如 `buttons` / `inline_keyboard` / `actions`）
3. callback 事件回到 skill 时的命令格式（例如 `/brush like`）

建议提示词：

```text
请在当前 claw/moltbot 运行环境中确认：skill 的按钮可点击能力到底要求什么响应结构。
重点输出：
1) 可点击按钮需要的字段 schema
2) callback 回传命令格式
3) 最小可运行示例（message + button）
```

### 第 2 步：最小化打通

先做一个最小按钮回调闭环，不要一次改大：
1. `/brush` 返回 1 个按钮（例如 `👍 感兴趣`）
2. 点击后能触发 `/brush like`
3. 返回确认消息（例如 `✅ callback ok`）

建议提示词：

```text
请先实现最小闭环：
- /brush 只返回一个可点击按钮
- 点击按钮后触发 /brush like
- 返回 callback 成功消息
先证明“可点击 + 可回调”成立，再扩展完整按钮组。
```

### 第 3 步：恢复完整按钮组

最小闭环通过后，恢复 5 个按钮与现有命令映射：
- `/brush like`
- `/brush skip`
- `/brush read`
- `/brush save`
- `/brush refresh`

### 第 4 步：验收

验收通过标准：
1. `/brush` 可见可点击按钮（不是文本方括号）
2. 每个按钮点击后都能触发对应命令
3. `behavior_events.jsonl` 有对应事件记录
4. `scripts/m8_smoke_test.py` 仍为 PASS

---

## 经验沉淀模板（修复完成后填写）

请把以下内容补到 `docs/USER_FEEDBACK_2026-02-23.md` 的 M11 小节，或新增 `docs/M11_BUTTON_FIX_EXPERIENCE.md`：

```markdown
## M11 按钮可点击修复经验（YYYY-MM-DD）

### 根因
- 例如：skill 被按 CLI 文本模式执行，宿主未解析按钮结构
- 例如：字段名不匹配（buttons vs inline_keyboard）

### 最终方案
- 关键改动文件：
  - path/to/file1
  - path/to/file2
- 关键字段/协议：
  - ...

### 验收结果
- /brush 按钮点击：PASS
- like/skip/read/save/refresh 回调：PASS
- m8_smoke_test：PASS

### 可复用规则
1. 新 skill 默认先做最小按钮闭环验证
2. 先确认宿主 schema，再写业务逻辑
3. 文本按钮仅作 fallback，不作为最终交互
```

---

## 交付要求

修复完成后，请 claw 管家回传：
1. 通过的提交号（commit）
2. 关键输出证据（按钮可点击 + callback 生效）
3. 经验文档路径
4. 是否可将 `m11_inline_buttons` 置为 `true`
