# 🌟 Open Pulse

> Your personalized AI newsletter service

Open Pulse is an intelligent newsletter application built on the [Agno](https://github.com/agno-agi/agno) framework. It learns your interests through conversation, automatically searches and curates relevant content, and generates personalized news summaries.

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![Agno](https://img.shields.io/badge/Built%20with-Agno-purple.svg)](https://github.com/agno-agi/agno)

---

## ✨ Features

### 🤖 Conversational Intelligence
- Conversational learning: Chat with the Newsletter Agent to naturally share your interests and preferences
- Persistent memory: The system remembers your preferences and maintains context across sessions
- Intelligent extraction: Extracts high-quality user preferences using a custom Memory Manager

### 📚 Knowledge Management
- Multi-source import: Supports uploading files, URLs, and plain text
- Custom Reader: Built-in Jina Web Reader for perfect web content parsing
- Flexible chunking: 8 chunking strategies (Fixed Size, Semantic, Agentic, etc.)
- Vector search: Efficient semantic search powered by LanceDB

### 🎯 Personalized Content
- Auto-generation: Digest Agent automatically searches and curates content based on your interests
- Scheduled delivery: Configurable cron jobs to generate daily digests
- Multimodal support: Supports text, images, videos, and more

---

## 🏗️ Architecture Overview

```
┌─────────────────────────────────────────────────────────────┐
│                    Frontend (Next.js)                       │
│  • Chat Interface  • Knowledge Management  • Settings       │
└─────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│                    AgentOS (FastAPI)                        │
│  • Session Management  • Memory Management  • API Endpoints │
└─────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│                         Agents                              │
│  • Newsletter Agent (Conversational)                        │
│  • Digest Agent (Content Generation)                        │
│  • Research Agent (Information Gathering)                   |
│  • Social Agent (Wechat History)                            │
└─────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│                    Knowledge & Tools                        │
│  • LanceDB (Vector Store)  • Custom Readers                 │
│  • MCP Tools (Brave Search, Gmail, Arxiv)                   │
└─────────────────────────────────────────────────────────────┘
```

---

## 🚀 Quick Start

### Prerequisites

- Python 3.11+
- Node.js 18+ and npm/pnpm
- API Keys:
  - OpenAI API Key (recommended) or OpenRouter
  - Jina API Key
  - GOOGLE_API_KEY
  - GOOGLE_CLIENT_ID=your_client_id_here
  - GOOGLE_CLIENT_SECRET=your_client_secret_here
  - GOOGLE_PROJECT_ID=your_project_id_here
  - GOOGLE_REDIRECT_URI=http://localhost  # Default value

### Backend Deployment

#### 1. Clone the repository

```bash
git clone https://github.com/eliumusk/open_pulse.git
cd open-pulse
```

#### 2. Create a virtual environment

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
```

#### 3. Install dependencies

Using uv (recommended):
```bash
uv sync
```

Or using pip:
```bash
pip install -r requirements.txt
```

#### 4. Configure environment variables

```bash
cp .env.example .env
```

Edit the `.env` file and fill in the required API Keys:

```bash
# Required: configure at least one LLM API key
OPENAI_API_KEY=sk-...

# Recommended: for web parsing (free)
JINA_API_KEY=jina_...  # Get from https://jina.ai/reader


# Database configuration
DATABASE_URL=sqlite:///./open_pulse.db

# AgentOS configuration
AGENTOS_PORT=7777
AGENTOS_HOST=0.0.0.0
```

#### 5. Start AgentOS

```bash
python agentos.py
```

You should see:
```
✅ Registered JinaWebReader to knowledge.readers and ReaderFactory
INFO:     Started server process
INFO:     Uvicorn running on http://0.0.0.0:7777
```

#### 6. Access backend services

- API Docs: http://localhost:7777/docs
- Health Check: http://localhost:7777/health

### Frontend Deployment

#### 1. Go to the frontend directory

```bash
cd agent-ui
```

#### 2. Install dependencies

Using npm:
```bash
npm install
```


#### 3. Start the development server

```bash
npm run dev
```

#### 4. Visit the frontend app

Open your browser and go to: http://localhost:3000

---

## 📖 Usage Guide

### 1. Chat with the Newsletter Agent

On first use, the Newsletter Agent will chat with you to learn your interests:

```
Agent: Hi! I'm the Newsletter Agent of Open Pulse. I'd like to learn about the topics
       you're interested in so I can generate personalized digests for you.
       What areas have you been following recently?

User: I'm a software engineer, interested in distributed systems, database internals,
      and AI infrastructure.

Agent: Awesome! Distributed systems and database internals are deep areas.
       Do you prefer deep technical articles, or industry news and updates?

User: I prefer deep technical articles, ideally with source code analysis or
      architecture design.
```

The system will automatically remember:
- ✅ The user is a software engineer
- ✅ Interested in distributed systems, database internals, and AI infrastructure
- ✅ Prefers deep technical articles, likes source code analysis and architecture design

### 2. Import knowledge content

Open Pulse supports three ways to import content into the knowledge base:

#### Method 1: Upload files

Supported file types:
- 📄 PDF (.pdf)
- 📊 CSV (.csv)
- 📝 Markdown (.md)
- 📋 JSON (.json)
- 📃 Plain text (.txt)

Steps:
1. Click the "Knowledge" panel on the left
2. Click the "Add" button
3. Select the "File" tab
4. Drag-and-drop or select files
5. (Optional) Expand "Advanced Options" to choose Reader and Chunking strategy
6. Click "Upload"

Advanced options:
- Reader Type: Select a specific file parser (Auto-detect is usually fine)
- Chunking Strategy:
  - Fixed Size: Fixed-size chunks (suitable for long documents)
  - Semantic: Semantic chunking (preserves semantic coherence)
  - Agentic: AI-driven intelligent chunking (best quality, slower)
  - Markdown: Chunk by Markdown structure
  - Document: Document-specific chunking

#### Method 2: Import URL

Supported URL types:
- 🌐 Web articles
- 📺 YouTube videos
- 📚 Wikipedia pages
- 🔬 arXiv papers
- 🔍 Web search results

Steps:
1. Click "Add" → "URL" tab
2. Enter the URL (e.g., https://example.com/article)
3. Enter a content name and description
4. Important: Expand "Advanced Options" and select "Jina Web Reader (Recommended for URLs)"
5. Click "Upload"

Why choose Jina Web Reader?
- ✅ Perfectly parses complex pages (including WeChat Official Accounts, Medium, etc.)
- ✅ Automatically extracts main content and filters ads/navigation
- ✅ Converts to LLM-friendly Markdown

#### Method 3: Paste text

Paste text directly:

Steps:
1. Click "Add" → "Text" tab
2. Paste or enter text
3. Enter a content name and description
4. Click "Upload"

Use cases:
- 📋 Copied article excerpts
- 💬 Chat logs
- 📝 Notes and summaries
- 🔖 Bookmarks and citations

### 3. View processing status

After upload, the system will automatically process the content:

- ⟳ Processing (yellow spinning icon): Parsing and vectorizing
- ✓ Completed (green check): Successfully added to the knowledge base
- ✗ Failed (red cross): Processing failed; click to view error details

Auto-refresh: The frontend polls every 2 seconds; no manual refresh needed.

### 4. Use the knowledge base

Imported content is automatically used for:

1. Conversation augmentation: Agents can cite knowledge base content to answer questions
2. Content generation: Digest Agent generates newsletters using the knowledge base
3. Semantic search: Find relevant content via vector search

Example conversation:
```
User: The article about the Raft algorithm I just uploaded — could you summarize the core ideas?

Agent: [Retrieve from knowledge base] Based on the article you uploaded, the core ideas of Raft include:
       1. Leader Election: Elect a leader using randomized timeouts
       2. Log Replication: The leader receives client requests and replicates them to followers
       3. Safety: Ensures committed logs are never lost
       ...
```

### 5. Manage Memory

The system automatically extracts and stores your preferences. You can:

View Memories:
- Via API: GET http://localhost:7777/memories?user_id=your_user_id
- Via database: View the memories table in open_pulse.db

Memory extraction rules:
The system uses a custom Memory Manager with the following rules:

✅ Will store:
- User interests and preferences
- Content type preferences
- Reading habits
- Professional background
- Learning goals

❌ Will NOT store:
- Sensitive personal information (name, address, etc.)
- Temporary requests
- System instructions
- Redundant information

Custom Memory configuration:
If you need to modify memory extraction rules, edit config/memory_config.py:

```python
# Add custom rules
additional_instructions = """
- Pay special attention to the user's tech stack preferences
- Record user interest in specific companies or products
- Track the user's learning progress
"""

memory_manager = create_memory_manager(
    db=db,
    additional_instructions=additional_instructions
)
```

### 6. Scheduled tasks

Open Pulse uses the trigger_workflow.sh script with crontab to schedule newsletter generation.

Configuration steps

1. Edit the trigger script

Modify user configuration in trigger_workflow.sh:

```bash
USER_ID="your_email@example.com"  # Your email
INTERESTS="AI, quantum computing, space exploration"  # Your interests
```

2. Set up the crontab job

```bash
# Edit crontab
crontab -e

# Add a scheduled task (generate every day at 8 AM)
0 8 * * *  /bin/bash trigger_workflow.sh

# Or every 2 minutes (for testing)
*/2 * * * * /bin/bash trigger_workflow.sh
```

3. View scheduled tasks

```bash
# View current crontab jobs
crontab -l

# View execution logs
tail -f logs/trigger_workflow_$(date +%F).log
```

Crontab time format explanation

```
# ┌───────────── Minute (0 - 59)
# │ ┌───────────── Hour (0 - 23)
# │ │ ┌───────────── Day of month (1 - 31)
# │ │ │ ┌───────────── Month (1 - 12)
# │ │ │ │ ┌───────────── Day of week (0 - 7, both 0 and 7 mean Sunday)
# │ │ │ │ │
# * * * * * Command to execute

# Common examples:
0 8 * * *     # Every day at 8:00 AM
0 */2 * * *   # Every 2 hours
30 9 * * 1-5  # Monday to Friday at 9:30 AM
0 0 1 * *     # At 12:00 AM on the 1st of every month
```

Frontend notifications

After the workflow completes, the frontend will display a notification card:
- Open the browser and go to http://localhost:3000
- A notification card will appear in the bottom-right corner
- Click "View Full Newsletter" to see the full content
- Click "Dismiss" to close the notification

#### 手动触发

也可以手动运行脚本立即生成：

```bash
./trigger_workflow.sh
```

### 7. 邮件通知配置

Newsletter 生成后会自动发送邮件给订阅者，邮件中包含封面图片和内容。

#### 配置步骤

**1. 编辑 `.env` 文件**

```bash
# SMTP 服务器设置
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587

# 发件人邮箱（需要应用专用密码）
SENDER_EMAIL=your_email@gmail.com
SENDER_PASSWORD=your_app_password
```

**注意**：收件人邮箱由 `trigger_workflow.sh` 中的 `USER_ID` 指定。

**2. 配置收件人**

编辑 `trigger_workflow.sh`：

```bash
USER_ID="your_email@example.com"  # 这个邮箱将收到 Newsletter
```

**3. 获取 Gmail 应用专用密码**

1. 访问 https://myaccount.google.com/apppasswords
2. 选择 "Mail" 和 "Other (Custom name)"
3. 生成密码并复制到 `SENDER_PASSWORD`

**4. 测试邮件发送**

```bash
python -c "from services.email_service import send_newsletter_email; \
send_newsletter_email('Test Content', None, ['your_email@example.com'])"
```

**5. 邮件特性**

- ✅ 精美的 HTML 邮件模板
- ✅ 封面图片直接嵌入邮件正文（非附件）
- ✅ 响应式设计，支持移动端
- ✅ 自动发送给所有订阅者

**详细配置说明**：参考 [docs/EMAIL_SETUP.md](docs/EMAIL_SETUP.md)

---

## 📁 Project Structure

```
open_pulse/
├── agents/                      # Agent definitions
│   ├── newsletter_agent.py      # Conversational agent (user interaction)
│   ├── digest_agent.py          # Content generation agent (summarization)
│   └── __init__.py
│
├── readers/                     # Custom Reader implementations
│   ├── jina_reader.py           # Jina Web Reader (web parsing)
│   ├── registry.py              # Reader registration system
│   ├── README.md                # Reader development docs
│   └── __init__.py
│
├── config/                      # Configuration files
│   ├── settings.py              # Global settings
│   ├── memory_config.py         # Memory management configuration
│   └── __init__.py
│
│
├── workflows/                   # Workflows
│   ├── newsletter_generation.py # Newsletter generation workflow
│   └── __init__.py
│
├── agent-ui/                    # Frontend app (Next.js)
│   ├── src/
│   │   ├── api/                 # API layer
│   │   ├── components/          # React components
│   │   │   ├── chat/            # Chat interface
│   │   │   │   ├── ChatInterface.tsx
│   │   │   │   └── Sidebar/
│   │   │   │       ├── Knowledge/  # Knowledge management
│   │   │   │       │   ├── Knowledge.tsx
│   │   │   │       │   ├── KnowledgeItem.tsx
│   │   │   │       │   └── UploadFileDialog.tsx
│   │   │   │       └── ...
│   │   │   └── ui/              # UI component library
│   │   ├── app/                 # Next.js pages
│   │   └── types/               # TypeScript type definitions
│   ├── package.json
│   └── ...
│
├── agentos.py                   # AgentOS main service entrypoint
├── pyproject.toml               # Python project configuration
├── uv.lock                      # Dependency lockfile
├── .env.example                 # Environment variable template
└── README.md                    # This file
```

---

## 🔧 Development Guide

### Add a custom Reader

If you need to support new content sources (e.g., specific websites or APIs), you can create a custom Reader:

#### 1. Create the Reader class

Create a new file under readers/, e.g., custom_reader.py:

```python
from agno.knowledge.reader.base import Reader
from agno.document import Document
from typing import List, Optional

class CustomReader(Reader):
    """Custom Reader example"""

    def __init__(self, api_key: str = None, **kwargs):
        super().__init__(**kwargs)
        self.api_key = api_key

    def read(self, source: str, name: str = None) -> List[Document]:
        """Synchronous read"""
        # Implement your reading logic
        content = self._fetch_content(source)

        return [Document(
            name=name or source,
            content=content,
            meta_data={"source": source}
        )]

    async def async_read(self, source: str, name: str = None) -> List[Document]:
        """Asynchronous read"""
        import asyncio
        return await asyncio.to_thread(self.read, source, name)

    def _fetch_content(self, source: str) -> str:
        """Concrete implementation to fetch content"""
        # Your implementation
        pass
```

#### 2. Register the Reader

Add the registration function in readers/registry.py:

```python
def _register_custom_reader(knowledge: Knowledge) -> str:
    """Register CustomReader"""
    api_key = os.getenv("CUSTOM_API_KEY")
    if not api_key:
        return "skipped: CUSTOM_API_KEY not found"

    try:
        custom_reader = CustomReader(
            api_key=api_key,
            name="Custom Reader",
            description="Description of what this reader does"
        )

        # Add to knowledge.readers
        knowledge.readers["CustomReader"] = custom_reader

        # Register to ReaderFactory
        def create_custom_reader(**kwargs):
            return CustomReader(api_key=api_key, **kwargs)

        ReaderFactory.register_reader(
            key="CustomReader",
            reader_method=create_custom_reader,
            name="Custom Reader",
            description="Description of what this reader does",
            extensions=None
        )

        return "registered"
    except Exception as e:
        return f"failed: {str(e)}"

# Call it inside register_all_readers
def register_all_readers(knowledge: Knowledge) -> dict:
    status = {}

    # Existing readers
    jina_status = _register_jina_reader(knowledge)
    status['JinaWebReader'] = jina_status

    # Add your custom reader
    custom_status = _register_custom_reader(knowledge)
    status['CustomReader'] = custom_status

    return status
```

#### 3. Update the frontend

Add the option in agent-ui/src/components/chat/Sidebar/Knowledge/UploadFileDialog.tsx:

```typescript
<SelectItem value="CustomReader">Custom Reader</SelectItem>
```

For detailed docs, see: readers/README.md

### Customize Memory extraction rules

Edit config/memory_config.py to customize memory extraction logic:

```python
# Modify global rules
MEMORY_EXTRACTION_RULES = """
## Your custom rules

### What to Store:
- Types of information you want to store

### What NOT to Store:
- Types of information you don't want to store
"""

# Or add rules for a specific agent
def create_newsletter_memory_manager(db: SqliteDb) -> MemoryManager:
    additional_instructions = """
    ### Your extra rules:
    - Rule 1
    - Rule 2
    """

    return create_memory_manager(
        db=db,
        additional_instructions=additional_instructions
    )
```

### Add a new Agent

1. Create a new file in the agents/ directory
2. Define the agent's instructions and tools
3. Register the agent in agentos.py

Example:

```python
# agents/research_agent.py
from agno.agent import Agent
from agno.models.openai import OpenAIChat

def create_research_agent(db, knowledge):
    return Agent(
        name="Research Agent",
        model=OpenAIChat(id="gpt-4o"),
        instructions="You are a research assistant...",
        db=db,
        knowledge=knowledge,
        tools=[...]
    )
```

---

## 🤝 Contributing

Contributions are welcome! Please follow these steps:

1. Fork this repository
2. Create a feature branch: git checkout -b feature/amazing-feature
3. Commit changes: git commit -m 'Add amazing feature'
4. Push to the branch: git push origin feature/amazing-feature
5. Open a Pull Request

### Code style

- Python: Follow PEP 8; use black for formatting
- TypeScript: Follow ESLint rules; use prettier for formatting
- Commit messages: Use clear messages describing the changes

---

## 📝 FAQ

### Q: Why choose Jina Web Reader when uploading URLs?

A: Agno's built-in WebsiteReader and FirecrawlReader have bugs parsing certain pages. Jina Web Reader is our custom solution that uses Jina AI's free API and can perfectly parse various complex web pages.

### Q: How to handle a large amount of chat history?

A: Use create_chat_history_memory_manager to process chat logs in bulk:

```python
from config.memory_config import create_chat_history_memory_manager

memory_manager = create_chat_history_memory_manager(db)
# Use this memory_manager to process chat logs
```

### Q: How to modify the schedule time?

A: Edit your crontab configuration:

```bash
# Edit crontab
crontab -e

# Change time (e.g., to 6 PM daily)
0 18 * * * /data/muskliu/mt/open_pulse/trigger_workflow.sh

# Save and exit (vim: press ESC, type :wq)
```

Common schedules:
- 0 8 * * * - Every day at 8:00 AM
- 0 12,18 * * * - At 12:00 PM and 6:00 PM every day
- 0 */6 * * * - Every 6 hours
- 0 9 * * 1-5 - Weekdays at 9:00 AM

### Q: Which LLMs are supported?

A: All LLMs compatible with Agno:
- OpenAI (GPT-4o, GPT-4o-mini, etc.)
- Anthropic (Claude 3.5 Sonnet, etc.)
- OpenRouter (access to many models)
- Local models (via Ollama, etc.)

### Q: How to back up data?

A: Back up the following files/directories:
- open_pulse.db (SQLite database)
- my_knowledge.db (Knowledge content database)
- tmp/lancedb/ (vector database)

---

## 📄 License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

---

## 🙏 Acknowledgments

- [Agno](https://github.com/agno-agi/agno) - A powerful AI Agent framework

---

## 📧 Contact

For issues or suggestions:
- Open an [Issue](https://github.com/eliumusk/open_pulse/issues)
- Join our [Discord community](https://discord.gg/your-invite)

---

<div align="center">
  <p>Built with ❤️ and Agno</p>
  <p>⭐ If you find this project helpful, please give us a Star!</p>
</div>