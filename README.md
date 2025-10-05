🌟 Open Pulse

你的个性化 AI 新闻简报服务

Open Pulse 是一个智能化的新闻简报应用，它通过与用户对话学习兴趣，并自动生成个性化内容。

⸻

✨ 功能特色
	•	对话式学习：与新闻简报智能体聊天，分享你的兴趣
	•	持久记忆：系统会在不同会话间记住你的偏好
	•	自主内容生成：后台智能体搜索并综合信息
	•	MCP 集成：所有工具通过 Model Context Protocol 解耦
	•	基于 Agno 构建：使用 Agno 强大的智能体框架和 AgentOS

⸻

🏗️ 架构概览

┌──────────────────────────────┐
│         AgentOS (FastAPI)    │
│  • 会话管理                   │
│  • 记忆管理                   │
│  • API 接口                   │
└──────────────────────────────┘
                  ↓
┌──────────────────────────────┐
│            智能体             │
│  • 新闻简报智能体（对话）      │
│  • 摘要智能体（内容生成）      │
│  • 研究智能体（信息收集）      │
└──────────────────────────────┘
                  ↓
┌──────────────────────────────┐
│         MCP 工具              │
│  • Brave 搜索                 │
│  • Arxiv                      │
└──────────────────────────────┘


⸻

🚀 快速开始

前置条件
•Python 3.11+
•Node.js
•API Key：
•OpenRouter
•Brave Search（可选，但推荐）

安装步骤
1.克隆仓库

git clone https://github.com/yourusername/open-pulse.git
cd open-pulse

2.创建虚拟环境

python -m venv venv
source venv/bin/activate  # Windows 使用: venv\Scripts\activate

3.安装依赖

uv sync

4.配置环境变量

cp .env.example .env
# 编辑 .env 文件，填入你的 API Key

5.启动 AgentOS

python agentos.py

6.访问应用

•API: http://localhost:7777
•文档: http://localhost:7777/docs
•MCP 服务器: http://localhost:7777/mcp


⸻

📁 项目结构

open_pulse/
├── agents/                 # 智能体定义
│   ├── newsletter_agent.py # 对话智能体
│   ├── digest_agent.py     # 内容生成智能体
│   └── __init__.py
├── tools/                  # MCP 工具配置
│   ├── mcp_tools.py
│   └── __init__.py
├── workflows/              # 后台工作流
├── config/                 # 配置文件
│   ├── settings.py
│   └── __init__.py
├── agentos.py              # AgentOS 主服务
├── requirements.txt        # Python 依赖
├── .env.example            # 环境变量模板
└── README.md               # 本文件

