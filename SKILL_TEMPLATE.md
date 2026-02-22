# Moltbot Skill 开发指南

## Skill 结构

```
your-skill/
├── SKILL.md          ← Skill 定义文件（必需）
├── src/
│   └── main.py       ← Skill 入口（必需）
├── config.yaml       ← 配置文件（可选）
└── data/             ← 数据文件（可选）
```

---

## SKILL.md 格式

```markdown
---
name: brush-blog
description: 像刷抖音一样学顶级博客
metadata: {"clawdbot":{"emoji":"🦞"}}
---

# 刷博客 Skill

这里是 Skill 的说明文档，用户可以看到。

## 命令
- `/brush` - 开始刷博客
- `/brush status` - 查看进度
```

**要点：**
- 顶部 YAML frontmatter 定义名称、描述、emoji
- 下面是 Markdown 说明文档

---

## src/main.py 格式

```python
"""
刷博客 Skill - Moltbot Skill 入口
"""

def handle_command(command, args, user_id, context):
    """
    处理用户命令
    
    Args:
        command: 命令字符串（如 "/brush"）
        args: 命令参数列表
        user_id: 用户 ID
        context: 上下文（包含用户配置、数据等）
    
    Returns:
        dict: {
            "message": str,           # 回复消息
            "buttons": [[{"text": str, "callback_data": str}]],  # 按钮（可选）
            "media": str              # 媒体文件路径（可选）
        }
    """
    if command == "/brush":
        # 1. 读取用户画像
        # 2. 推荐一条内容
        # 3. 返回卡片 + 按钮
        return {
            "message": "📰 博客卡片内容...",
            "buttons": [
                [
                    {"text": "👍 感兴趣", "callback_data": "/brush like"},
                    {"text": "👎 划走", "callback_data": "/brush skip"}
                ],
                [
                    {"text": "📖 深度阅读", "callback_data": "/brush read"},
                    {"text": "💾 收藏", "callback_data": "/brush save"}
                ]
            ]
        }
    
    elif command == "/brush status":
        return {
            "message": "📊 你的阅读进度：..."
        }
    
    else:
        return {
            "message": "未知命令，试试 /brush"
        }
```

**要点：**
- 必须定义 `handle_command` 函数
- 参数：`command, args, user_id, context`
- 返回 dict：`message`（必需）, `buttons`（可选）, `media`（可选）
- 按钮格式：二维数组 `[[row1], [row2]]`

---

## 按钮回调处理

用户点击按钮后，callback_data 会作为新命令发送：

```python
def handle_command(command, args, user_id, context):
    if command == "/brush":
        # 主命令：推荐内容
        ...
    
    elif command == "/brush like":
        # 用户点了"👍 感兴趣"
        # 记录正反馈，更新用户画像
        ...
        return {"message": "已记录，推荐相似内容"}
    
    elif command == "/brush skip":
        # 用户点了"👎 划走"
        # 记录负反馈，跳过这条
        ...
        return {"message": "已跳过"}
```

---

## 读取配置文件

```python
import yaml
import json

# 读取 config.yaml
with open('config.yaml', 'r') as f:
    config = yaml.safe_load(f)

# 读取 feeds.json
with open('data/feeds.json', 'r') as f:
    feeds = json.load(f)

# 读取用户画像
profile_path = f'data/profiles/{user_id}.json'
try:
    with open(profile_path, 'r') as f:
        profile = json.load(f)
except FileNotFoundError:
    profile = None  # 新用户
```

---

## 完整示例：/brush 命令

```python
"""
SKILL.md 内容：
---
name: brush-blog
description: 像刷抖音一样学顶级博客
metadata: {"clawdbot":{"emoji":"🦞"}}
---
"""

import json
import random

def handle_command(command, args, user_id, context):
    if command == "/brush":
        # 1. 读取 RSS 源
        with open('data/feeds.json', 'r') as f:
            feeds = json.load(f)
        
        # 2. 随机选一条（简化版，实际应该用推荐算法）
        all_posts = []
        for category, sources in feeds.items():
            for source in sources:
                all_posts.append({
                    "title": f"示例文章 from {source}",
                    "summary": "这是文章摘要...",
                    "tags": ["#AI", "#Python"],
                    "source": source,
                    "url": f"https://{source}/article"
                })
        
        post = random.choice(all_posts)
        
        # 3. 构建卡片消息
        message = f"""📰 {post['title']}

{post['summary']}

标签：{' '.join(post['tags'])}
来源：{post['source']}
"""
        
        # 4. 返回按钮
        return {
            "message": message,
            "buttons": [
                [
                    {"text": "👍 感兴趣", "callback_data": "/brush like"},
                    {"text": "👎 划走", "callback_data": "/brush skip"}
                ],
                [
                    {"text": "📖 深度阅读", "callback_data": "/brush read"},
                    {"text": "💾 收藏", "callback_data": "/brush save"}
                ]
            ]
        }
```

---

## 开发流程

1. **创建 SKILL.md** - 定义 Skill 名称、描述
2. **创建 src/main.py** - 实现 handle_command 函数
3. **本地测试** - `python3 src/main.py /brush`（如果支持 CLI 测试）
4. **部署到 Moltbot** - 发布到 ClawdHub 或本地加载
5. **Telegram 测试** - 发送 `/brush` 验证

---

## 常见错误

❌ **忘记 SKILL.md 的 YAML frontmatter**
```markdown
# 错误：没有 ---
name: brush-blog
```

✅ **正确：**
```markdown
---
name: brush-blog
description: ...
---
```

❌ **handle_command 参数不对**
```python
# 错误：缺少 context
def handle_command(command, args, user_id):
```

✅ **正确：**
```python
def handle_command(command, args, user_id, context):
```

❌ **按钮格式错误**
```python
# 错误：一维数组
"buttons": [{"text": "👍", "callback_data": "/like"}]
```

✅ **正确：**
```python
"buttons": [
    [{"text": "👍", "callback_data": "/like"}]
]
```

---

## 参考项目

- OpenClaw 官方 Skills: https://github.com/openclaw/skills
- 刷博客 Skill: https://github.com/Dalaoyuan2020/brush-blog-skill
