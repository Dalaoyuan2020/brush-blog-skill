# AGENT_INSTRUCTIONS.md

## 目标
定义 Agent 在收到 `/brush` 请求后的标准调度流程，确保：
- Skill 本体只做本地读取和 stdout 输出
- 按钮由 Agent 的 `message` 工具发送
- 内容池刷新由 Agent 决策（同步或异步）

## 处理流程（/brush 或 /brush [action]）
1. Agent 用 `exec` 工具执行：
`python3 {skillDir}/src/main.py /brush [action]`
2. 解析 `exec` 的 stdout：
- 卡片正文（用于展示）
- 状态行：`POOL_SIZE` / `POOL_LOW` / `POOL_EMPTY`
3. Agent 用 `message` 工具 `send` 动作发消息（附带 buttons 参数）。
4. 根据状态行决策补货：
- 若 `POOL_EMPTY: true`：同步执行刷新（阻塞当前请求，刷新后可再推荐）
- 若 `POOL_LOW: true` 且 `POOL_EMPTY: false`：异步 `sessions_spawn` 子代理刷新

## 状态行解析建议
- `POOL_SIZE: N`：解析 `N` 为整数
- `POOL_LOW: true|false`：布尔值
- `POOL_EMPTY: true|false`：布尔值

## 同步刷新（POOL_EMPTY=true）
当池子为空，主 Agent 直接执行：
`python3 {skillDir}/src/pool_manager.py refresh`

## 异步刷新（POOL_LOW=true）
当池子偏低但非空，主 Agent 启动子代理异步刷新。

### sessions_spawn 参数示例（JSON）
```json
{
  "label": "brush-pool-refresh",
  "task": "执行 python3 {skillDir}/src/pool_manager.py refresh，完成后回报池子大小与去重结果。",
  "runTimeoutSeconds": 180,
  "cleanup": "delete"
}
```

## 关键限制（必须遵守）
- 子代理不能再 spawn 子代理（官方限制，禁止嵌套 spawn）。
- `{baseDir}` / `{skillDir}` 是 OpenClaw 运行时占位符，不要写死成本地路径。
- Skill 不负责按钮渲染，按钮必须由 Agent `message send` 发送。

## 按钮映射（Agent 侧发送）
```json
[
  [
    {"text": "👍", "callback_data": "/brush like"},
    {"text": "👎", "callback_data": "/brush skip"}
  ],
  [
    {"text": "📖 深读", "callback_data": "/brush read"},
    {"text": "💾 收藏", "callback_data": "/brush save"}
  ],
  [
    {"text": "🔄 换一批", "callback_data": "/brush refresh"}
  ]
]
```

## 参考文档
- Skills: https://docs.openclaw.ai/tools/skills
- Sub-Agents: https://docs.openclaw.ai/tools/subagents
- Tools: https://docs.openclaw.ai/tools
