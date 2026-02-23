# M11 按钮可点击修复经验（2026-02-23）

## 根因

- Skill 以 CLI 文本模式执行（`python3 src/main.py /brush`），输出纯文本
- 按钮以文字形式输出：`按钮：[👍 感兴趣] [👎 划走] | ...`
- 宿主（Agent）直接将文本转发给用户，Telegram 无法识别为 inline keyboard
- **核心问题在集成层，不在 skill 代码**

## 最终方案

### 关键改动

**不需要修改 skill 代码**，修复在 Agent 集成层：

1. Agent 运行 skill 命令获取文本输出
2. 解析输出：提取消息正文（去掉 DEBUG 行和 `按钮：` 行）
3. 使用 Moltbot `message` 工具发送，附带 `buttons` 参数（Telegram inline keyboard）

### 关键字段/协议

Moltbot `message` 工具的 `buttons` 参数格式：

```json
{
  "action": "send",
  "message": "📰 博客卡片\n标题：...\n...",
  "buttons": [
    [
      {"text": "👍 感兴趣", "callback_data": "/brush like"},
      {"text": "👎 划走", "callback_data": "/brush skip"}
    ],
    [
      {"text": "📖 深度阅读", "callback_data": "/brush read"},
      {"text": "💾 收藏", "callback_data": "/brush save"}
    ],
    [
      {"text": "🔄 换一批", "callback_data": "/brush refresh"}
    ]
  ]
}
```

### 按钮映射表

| 按钮文字 | callback_data | 触发命令 |
|----------|---------------|----------|
| 👍 感兴趣 / 👍 这个领域感兴趣 | `/brush like` | `python3 src/main.py /brush like` |
| 👎 划走 / 👎 下一个领域 | `/brush skip` | `python3 src/main.py /brush skip` |
| 📖 深度阅读 / 📖 先读这篇 | `/brush read` | `python3 src/main.py /brush read` |
| 💾 收藏 | `/brush save` | `python3 src/main.py /brush save` |
| 🔄 换一批 / 🔄 换个领域 | `/brush refresh` | `python3 src/main.py /brush refresh` |

### 冷启动阶段按钮

冷启动时按钮不同：
```json
[
  [
    {"text": "👍 这个领域感兴趣", "callback_data": "/brush like"},
    {"text": "👎 下一个领域", "callback_data": "/brush skip"}
  ],
  [
    {"text": "📖 先读这篇", "callback_data": "/brush read"},
    {"text": "🔄 换个领域", "callback_data": "/brush refresh"}
  ]
]
```

## 验收结果

- /brush 按钮点击：**PASS** ✅
- like callback 回调：**PASS** ✅
- 完整 5 按钮组发送：**PASS** ✅
- m8_smoke_test：**PASS** ✅

## 可复用规则

1. **新 skill 默认先做最小按钮闭环验证** — 发一个按钮，确认 callback 能回来
2. **先确认宿主 schema，再写业务逻辑** — Moltbot 用 `message` 工具的 `buttons` 参数
3. **文本按钮仅作 fallback，不作为最终交互** — 正式交互必须用 inline keyboard
4. **按钮修复在集成层，不在 skill 代码层** — skill 输出文本，Agent 负责解析并发送 inline buttons
5. **callback_data 格式统一为 `/brush <command>`** — 与 skill CLI 命令一致
