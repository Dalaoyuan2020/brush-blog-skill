---
name: brush-blog
description: 像刷抖音一样刷顶级博客。执行 python3 {baseDir}/src/main.py /brush [action] 推荐文章
user-invocable: true
metadata: {"openclaw": {"requires": {"bins": ["python3"]}, "emoji": "📰"}}
---

## 使用方式
执行 `python3 {baseDir}/src/main.py /brush [action]`
支持的 action: (空)=推荐, like, skip, read, save, refresh

## 输出协议
Skill 输出纯文本到 stdout，Agent 用 exec 工具获取输出后：
1. 解析卡片正文（去除 POOL_* 状态行）
2. 用 message 工具的 send 动作发送（含 buttons 参数）

## 状态行协议（stdout 最后几行）
- POOL_LOW: true/false -> Agent 决定是否 spawn 子代理刷新
- POOL_EMPTY: true/false -> Agent 决定是否同步刷新
- POOL_SIZE: N -> 当前池子文章数

## 按钮映射（Agent 集成层负责，Skill 不管按钮）
buttons: [[{"text":"👍","callback_data":"/brush like"},{"text":"👎","callback_data":"/brush skip"}],[{"text":"📖 深读","callback_data":"/brush read"},{"text":"💾 收藏","callback_data":"/brush save"}],[{"text":"🔄 换一批","callback_data":"/brush refresh"}]]
