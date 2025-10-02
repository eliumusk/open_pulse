🌟 Open Pulse

你的个性化 AI 新闻简报服务

Open Pulse 是一个智能化的新闻简报应用，它通过与您的对话学习兴趣，并自动为您生成个性化内容。

✨ 功能特色
•对话式学习：与新闻简报智能体聊天，分享你的兴趣
•持久记忆：系统会在不同会话间记住你的偏好
•自主内容生成：后台智能体搜索并综合信息
•MCP 集成：所有工具通过 Model Context Protocol 解耦
•基于 Agno 构建：使用 Agno 强大的智能体框架和 AgentOS

🏗️ 架构

┌─────────────────────────────────────────┐
│         AgentOS (FastAPI)               │
│  • 会话管理                             │
│  • 记忆管理                             │
│  • API 接口                             │
└─────────────────────────────────────────┘
                  ↓
┌─────────────────────────────────────────┐
│            智能体                       │
│  • 新闻简报智能体（对话）               │
│  • 摘要智能体（内容生成）               │
│  • 研究智能体（信息收集）               │
└─────────────────────────────────────────┘
                  ↓
┌─────────────────────────────────────────┐
│         MCP 工具                        │
│  • Brave 搜索                           │
│  • Arxiv                                │
└─────────────────────────────────────────┘

🚀 快速开始

前置条件
	•	Python 3.9+
	•	Node.js（用于 MCP 服务器）
	•	API Key：
	•	OpenAI API Key（或 Anthropic/OpenRouter）
	•	Brave Search API Key（可选但推荐）

安装步骤
	1.	克隆仓库

cd open_pulse


	2.	创建虚拟环境

python -m venv venv
source venv/bin/activate  # Windows 使用: venv\Scripts\activate


	3.	安装依赖

pip install -r requirements.txt


	4.	配置环境变量

cp .env.example .env
# 编辑 .env 文件并填入 API Key


	5.	启动 AgentOS

python agentos.py


	6.	访问应用
	•	API: http://localhost:7777
	•	文档: http://localhost:7777/docs
	•	MCP 服务器: http://localhost:7777/mcp

📖 使用方法

使用 Agno UI

与 Open Pulse 交互最简单的方式是使用 Agno 内置的 UI：
	1.	启动 AgentOS（见快速开始）
	2.	服务运行在 http://localhost:7777
	3.	通过 /docs 下的 API 接口与智能体交互

API 接口示例

与新闻简报智能体对话

curl -X POST "http://localhost:7777/agents/newsletter-agent/runs" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "message=我对人工智能和量子计算感兴趣" \
  -d "user_id=user123" \
  -d "stream=false"

生成新闻简报（摘要智能体）

curl -X POST "http://localhost:7777/agents/digest-agent/runs" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "message=根据我的兴趣生成一份新闻简报" \
  -d "user_id=user123" \
  -d "stream=false"

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

🔧 配置

编辑 .env 文件可配置：
	•	LLM 提供商：OpenRouter
	•	数据库：SQLite 路径（默认 ./open_pulse.db）
	•	服务器：主机与端口设置
	•	MCP 工具：搜索服务的 API Key

🎯 路线图
	•	项目初始化
	•	核心智能体（新闻简报、摘要、研究）
	•	MCP 工具集成
	•	AgentOS 搭建
	•	后台工作流系统
	•	定时新闻简报生成
	•	邮件投递集成
	•	Web 前端

🤝 贡献

欢迎贡献！请随时提交 Pull Request。

📄 许可证

MIT License

🙏 致谢
	•	基于 Agno 构建 —— 最快的智能体开发框架
	•	使用 Model Context Protocol (MCP) 进行工具集成

