# brush-blog-skill（刷博客 Skill）

像刷抖音一样刷顶级博客，OpenClaw Skill V2.0。

## 功能列表
- `/brush` 推荐文章（内容池纯读模式）
- `/brush like` 感兴趣
- `/brush skip` 划走
- `/brush read` 深度阅读
- `/brush save` 收藏
- `/brush refresh` 换一批
- 智能推荐（兴趣/知识/多样性/热度）
- 冷启动引导（兴趣选择 + 快速学习期）
- 内容池自动刷新（Agent 调度，支持同步/异步）

## V2.0 架构说明
- Skill 纯读：`src/main.py` 只读取 `shared/content_pool.json` 并输出 stdout 文本与状态行
- Agent 调度：Agent 解析状态行后决定消息发送与刷新策略
- 子代理异步刷新：低水位时由 Agent 使用 `sessions_spawn` 触发后台刷新
- 状态行协议：`POOL_SIZE` / `POOL_LOW` / `POOL_EMPTY`

> V2.0 实测将 `/brush` 响应时间从约 5.40s 优化到约 0.19s（约 28x）。

## 技术栈
- Python 3
- RSS/Atom
- OpenClaw Skill 规范
- Telegram（按钮交互由 Agent 层发送）

## 安装与使用
1. 克隆仓库
```bash
git clone https://github.com/Dalaoyuan2020/brush-blog-skill.git
cd brush-blog-skill
```

2. 本地运行
```bash
python3 src/main.py /brush
python3 src/main.py /brush like
python3 src/main.py /brush skip
python3 src/main.py /brush read
python3 src/main.py /brush save
python3 src/main.py /brush refresh
```

3. 内容池运维命令
```bash
python3 src/pool_manager.py refresh
python3 src/pool_manager.py cleanup --days 7
```

## 项目结构
```text
brush-blog-skill/
├── src/                    # Skill 入口、抓取、推荐、交互、沉淀
├── shared/                 # 运行时共享数据（内容池、已读历史、运行日志）
├── docs/                   # 协作文档、调度文档、测试与复盘
├── scripts/                # 冒烟测试与辅助脚本
├── data/                   # 配置与本地数据（RSS 源、profiles 等）
├── SKILL.md                # OpenClaw Skill 声明
├── HANDOFF.md              # 交接与阶段进度
└── README.md
```

## Agent Team 致谢
- Opus（CloneLamb）：技术路线规划与验收
- CodeX（Codex）：代码实现与迭代
- 龍蝦（Claw 大管家）：VPS 测试、调度实战、部署验证
- 羊爸爸：产品定义与协作指挥

## 开源协议
MIT
