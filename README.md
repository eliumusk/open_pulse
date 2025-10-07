# 🌟 Open Pulse

> 你的个性化 AI 新闻简报服务

Open Pulse 是一个基于 [Agno](https://github.com/agno-agi/agno) 框架构建的智能新闻简报应用。它通过对话学习你的兴趣，自动搜索和整理相关内容，并生成个性化的新闻摘要。

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![Agno](https://img.shields.io/badge/Built%20with-Agno-purple.svg)](https://github.com/agno-agi/agno)

---

## ✨ 功能特色

### 🤖 智能对话
- **对话式学习**：与 Newsletter Agent 聊天，自然地分享你的兴趣和偏好
- **持久记忆**：系统会记住你的偏好，并在不同会话间保持上下文
- **智能提取**：使用自定义 Memory Manager 提取高质量的用户偏好

### 📚 知识管理
- **多源导入**：支持上传文件、URL、纯文本内容
- **自定义 Reader**：内置 Jina Web Reader，完美解析网页内容
- **灵活分块**：支持 8 种 chunking 策略（Fixed Size, Semantic, Agentic 等）
- **向量检索**：使用 LanceDB 进行高效的语义搜索

### 🎯 个性化内容
- **自动生成**：Digest Agent 根据你的兴趣自动搜索和整理内容
- **定时推送**：可配置的定时任务，每日生成新闻摘要
- **多模态支持**：支持文本、图片、视频等多种内容类型


---

## 🏗️ 架构概览

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

## 🚀 快速开始

### 前置条件

- **Python 3.11+**
- **Node.js 18+** 和 npm/pnpm
- **API Keys**：
  - OpenAI API Key（推荐）或 OpenRouter
  - Jina API Key
  - GOOGLE_API_KEY
  - GOOGLE_CLIENT_ID=your_client_id_here
  - GOOGLE_CLIENT_SECRET=your_client_secret_here
  - GOOGLE_PROJECT_ID=your_project_id_here
  - GOOGLE_REDIRECT_URI=http://localhost  # Default value

### 后端部署

#### 1. 克隆仓库

```bash
git clone https://github.com/eliumusk/open_pulse.git
cd open-pulse
```

#### 2. 创建虚拟环境

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
```

#### 3. 安装依赖

使用 uv（推荐）：
```bash
uv sync
```

或使用 pip：
```bash
pip install -r requirements.txt
```

#### 4. 配置环境变量

```bash
cp .env.example .env
```

编辑 `.env` 文件，填入必需的 API Keys：

```bash
# 必需：至少配置一个 LLM API Key
OPENAI_API_KEY=sk-...

# 推荐：用于网页解析（免费）
JINA_API_KEY=jina_...  # 从 https://jina.ai/reader 获取


# 数据库配置
DATABASE_URL=sqlite:///./open_pulse.db

# AgentOS 配置
AGENTOS_PORT=7777
AGENTOS_HOST=0.0.0.0
```

#### 5. 启动 AgentOS

```bash
python agentos.py
```

你应该看到：
```
✅ Registered JinaWebReader to knowledge.readers and ReaderFactory
INFO:     Started server process
INFO:     Uvicorn running on http://0.0.0.0:7777
```

#### 6. 访问后端服务

- **API 文档**：http://localhost:7777/docs
- **健康检查**：http://localhost:7777/health

### 前端部署

#### 1. 进入前端目录

```bash
cd agent-ui
```

#### 2. 安装依赖

使用 npm：
```bash
npm install
```


#### 3. 启动开发服务器

```bash
npm run dev
```

#### 4. 访问前端应用

打开浏览器访问：http://localhost:3000

---

## 📖 使用指南

### 1. 与 Newsletter Agent 对话

首次使用时，Newsletter Agent 会与你对话，了解你的兴趣：

```
Agent: 你好！我是 Open Pulse 的 Newsletter Agent。我想了解一下你感兴趣的话题，
       这样我就能为你生成个性化的新闻摘要。你最近在关注什么领域呢？

User: 我是一个软件工程师，对分布式系统、数据库内核、AI 基础设施比较感兴趣。

Agent: 太好了！分布式系统和数据库内核都是很有深度的领域。你更喜欢技术深度文章，
       还是行业动态和新闻？

User: 我更喜欢技术深度文章，最好是有源码分析或者架构设计的那种。
```

**系统会自动记住**：
- ✅ 用户是软件工程师
- ✅ 对分布式系统、数据库内核、AI 基础设施感兴趣
- ✅ 偏好技术深度文章，喜欢源码分析和架构设计

### 2. 导入知识内容

Open Pulse 支持三种方式导入内容到知识库：

#### 方式 1：上传文件

支持的文件类型：
- 📄 PDF（`.pdf`）
- 📊 CSV（`.csv`）
- 📝 Markdown（`.md`）
- 📋 JSON（`.json`）
- 📃 纯文本（`.txt`）

**操作步骤**：
1. 点击左侧 "Knowledge" 面板
2. 点击 "Add" 按钮
3. 选择 "File" 标签
4. 拖拽或选择文件
5. （可选）展开 "Advanced Options" 选择 Reader 和 Chunking 策略
6. 点击 "Upload"

**高级选项**：
- **Reader Type**：选择特定的文件解析器（通常选 Auto-detect 即可）
- **Chunking Strategy**：
  - `Fixed Size`：固定大小分块（适合长文档）
  - `Semantic`：语义分块（保持语义完整性）
  - `Agentic`：AI 驱动的智能分块（最佳质量，但较慢）
  - `Markdown`：按 Markdown 结构分块
  - `Document`：文档切分专用

#### 方式 2：导入 URL

支持的 URL 类型：
- 🌐 网页文章
- 📺 YouTube 视频
- 📚 Wikipedia 页面
- 🔬 arXiv 论文
- 🔍 Web 搜索结果

**操作步骤**：
1. 点击 "Add" → "URL" 标签
2. 输入 URL（如 `https://example.com/article`）
3. 输入内容名称和描述
4. **重要**：展开 "Advanced Options"，选择 **"Jina Web Reader (Recommended for URLs)"**
5. 点击 "Upload"

**为什么选择 Jina Web Reader？**
- ✅ 完美解析复杂网页（包括微信公众号、Medium 等）
- ✅ 自动提取正文内容，过滤广告和导航
- ✅ 转换为 LLM 友好的 Markdown 格式



#### 方式 3：粘贴文本

直接粘贴文本内容：

**操作步骤**：
1. 点击 "Add" → "Text" 标签
2. 粘贴或输入文本内容
3. 输入内容名称和描述
4. 点击 "Upload"

**适用场景**：
- 📋 复制的文章片段
- 💬 聊天记录
- 📝 笔记和摘要
- 🔖 书签和引用

### 3. 查看处理状态

上传后，系统会自动处理内容：

- ⟳ **处理中**（黄色旋转图标）：正在解析和向量化
- ✓ **完成**（绿色对勾）：已成功添加到知识库
- ✗ **失败**（红色叉号）：处理失败，点击查看错误信息

**状态自动刷新**：前端每 2 秒自动轮询一次，无需手动刷新。

### 4. 使用知识库

导入的内容会自动用于：

1. **对话增强**：Agent 可以引用知识库中的内容回答问题
2. **内容生成**：Digest Agent 会基于知识库生成新闻摘要
3. **语义搜索**：通过向量检索找到相关内容

**示例对话**：
```
User: 我刚才上传的那篇关于 Raft 算法的文章，能总结一下核心思想吗？

Agent: [检索知识库] 根据你上传的文章，Raft 算法的核心思想包括：
       1. Leader Election：通过随机超时机制选举 Leader
       2. Log Replication：Leader 负责接收客户端请求并复制到 Followers
       3. Safety：确保已提交的日志不会丢失
       ...
```

### 5. 管理 Memory

系统会自动提取和存储你的偏好，你可以：

**查看 Memories**：
- 通过 API：`GET http://localhost:7777/memories?user_id=your_user_id`
- 通过数据库：查看 `open_pulse.db` 中的 `memories` 表

**Memory 提取规则**：
系统使用自定义的 Memory Manager，遵循以下规则：

✅ **会存储**：
- 用户兴趣和偏好
- 内容类型偏好
- 阅读习惯
- 专业背景
- 学习目标

❌ **不会存储**：
- 敏感个人信息（姓名、地址等）
- 临时性请求
- 系统指令
- 冗余信息

**自定义 Memory 配置**：
如果需要修改 Memory 提取规则，编辑 `config/memory_config.py`：

```python
# 添加自定义规则
additional_instructions = """
- 特别关注用户的技术栈偏好
- 记录用户对特定公司或产品的兴趣
- 追踪用户的学习进度
"""

memory_manager = create_memory_manager(
    db=db,
    additional_instructions=additional_instructions
)
```

### 6. 定时任务

Open Pulse 使用 `trigger_workflow.sh` 脚本配合 crontab 实现定时生成 Newsletter。

#### 配置步骤

**1. 编辑触发脚本**

修改 `trigger_workflow.sh` 中的用户配置：

```bash
USER_ID="your_email@example.com"  # 你的邮箱
INTERESTS="AI, quantum computing, space exploration"  # 你的兴趣
```

**2. 设置 crontab 定时任务**

```bash
# 编辑 crontab
crontab -e

# 添加定时任务（每天早上 8 点生成）
0 8 * * * trigger_workflow.sh

# 或者每2分钟生成一次（测试用）
*/2 * * * * trigger_workflow.sh
```

**3. 查看定时任务**

```bash
# 查看当前的 crontab 任务
crontab -l

# 查看执行日志
tail -f logs/trigger_workflow_$(date +%F).log
```

#### Crontab 时间格式说明

```
# ┌───────────── 分钟 (0 - 59)
# │ ┌───────────── 小时 (0 - 23)
# │ │ ┌───────────── 日期 (1 - 31)
# │ │ │ ┌───────────── 月份 (1 - 12)
# │ │ │ │ ┌───────────── 星期 (0 - 7，0 和 7 都代表周日)
# │ │ │ │ │
# * * * * * 要执行的命令

# 常用示例：
0 8 * * *     # 每天早上 8:00
0 */2 * * *   # 每 2 小时
30 9 * * 1-5  # 周一到周五 9:30
0 0 1 * *     # 每月 1 号 0:00
```

#### 前端通知

当 workflow 完成后，前端会自动弹出通知卡片：
- 打开浏览器访问 http://localhost:3000
- 右下角会显示通知卡片
- 点击 "View Full Newsletter" 查看完整内容
- 点击 "Dismiss" 关闭通知

#### 手动触发

也可以手动运行脚本立即生成：

```bash
./trigger_workflow.sh
```

---

## 📁 项目结构

```
open_pulse/
├── agents/                      # 智能体定义
│   ├── newsletter_agent.py      # 对话智能体（与用户交互）
│   ├── digest_agent.py          # 内容生成智能体（生成摘要）
│   └── __init__.py
│
├── readers/                     # 自定义 Reader 实现
│   ├── jina_reader.py           # Jina Web Reader（网页解析）
│   ├── registry.py              # Reader 注册系统
│   ├── README.md                # Reader 开发文档
│   └── __init__.py
│
├── config/                      # 配置文件
│   ├── settings.py              # 全局配置
│   ├── memory_config.py         # Memory 管理配置
│   └── __init__.py
│
│
├── workflows/                   # 工作流
│   ├── newsletter_generation.py # newsletter生成工作流
│   └── __init__.py
│
├── agent-ui/                    # 前端应用（Next.js）
│   ├── src/
│   │   ├── api/                 # API 调用层
│   │   ├── components/          # React 组件
│   │   │   ├── chat/            # 聊天界面
│   │   │   │   ├── ChatInterface.tsx
│   │   │   │   └── Sidebar/
│   │   │   │       ├── Knowledge/  # 知识管理
│   │   │   │       │   ├── Knowledge.tsx
│   │   │   │       │   ├── KnowledgeItem.tsx
│   │   │   │       │   └── UploadFileDialog.tsx
│   │   │   │       └── ...
│   │   │   └── ui/              # UI 组件库
│   │   ├── app/                 # Next.js 页面
│   │   └── types/               # TypeScript 类型定义
│   ├── package.json
│   └── ...
│
├── agentos.py                   # AgentOS 主服务入口
├── pyproject.toml               # Python 项目配置
├── uv.lock                      # 依赖锁定文件
├── .env.example                 # 环境变量模板
└── README.md                    # 本文件
```

---

## 🔧 开发指南

### 添加自定义 Reader

如果需要支持新的内容源（如特定网站、API 等），可以创建自定义 Reader：

#### 1. 创建 Reader 类

在 `readers/` 目录下创建新文件，例如 `custom_reader.py`：

```python
from agno.knowledge.reader.base import Reader
from agno.document import Document
from typing import List, Optional

class CustomReader(Reader):
    """自定义 Reader 示例"""

    def __init__(self, api_key: str = None, **kwargs):
        super().__init__(**kwargs)
        self.api_key = api_key

    def read(self, source: str, name: str = None) -> List[Document]:
        """同步读取内容"""
        # 实现你的读取逻辑
        content = self._fetch_content(source)

        return [Document(
            name=name or source,
            content=content,
            meta_data={"source": source}
        )]

    async def async_read(self, source: str, name: str = None) -> List[Document]:
        """异步读取内容"""
        import asyncio
        return await asyncio.to_thread(self.read, source, name)

    def _fetch_content(self, source: str) -> str:
        """获取内容的具体实现"""
        # 你的实现逻辑
        pass
```

#### 2. 注册 Reader

在 `readers/registry.py` 中添加注册函数：

```python
def _register_custom_reader(knowledge: Knowledge) -> str:
    """注册 CustomReader"""
    api_key = os.getenv("CUSTOM_API_KEY")
    if not api_key:
        return "skipped: CUSTOM_API_KEY not found"

    try:
        custom_reader = CustomReader(
            api_key=api_key,
            name="Custom Reader",
            description="Description of what this reader does"
        )

        # 添加到 knowledge.readers
        knowledge.readers["CustomReader"] = custom_reader

        # 注册到 ReaderFactory
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

# 在 register_all_readers 函数中调用
def register_all_readers(knowledge: Knowledge) -> dict:
    status = {}

    # 现有的 readers
    jina_status = _register_jina_reader(knowledge)
    status['JinaWebReader'] = jina_status

    # 添加你的 custom reader
    custom_status = _register_custom_reader(knowledge)
    status['CustomReader'] = custom_status

    return status
```

#### 3. 更新前端

在 `agent-ui/src/components/chat/Sidebar/Knowledge/UploadFileDialog.tsx` 中添加选项：

```typescript
<SelectItem value="CustomReader">Custom Reader</SelectItem>
```

详细文档请参考：[`readers/README.md`](readers/README.md)

### 自定义 Memory 提取规则

编辑 `config/memory_config.py` 来自定义 Memory 提取逻辑：

```python
# 修改全局规则
MEMORY_EXTRACTION_RULES = """
## 你的自定义规则

### What to Store:
- 你想存储的信息类型

### What NOT to Store:
- 你不想存储的信息类型
"""

# 或为特定 Agent 添加规则
def create_newsletter_memory_manager(db: SqliteDb) -> MemoryManager:
    additional_instructions = """
    ### 你的额外规则：
    - 规则 1
    - 规则 2
    """

    return create_memory_manager(
        db=db,
        additional_instructions=additional_instructions
    )
```

### 添加新的 Agent

1. 在 `agents/` 目录创建新文件
2. 定义 Agent 的 instructions 和 tools
3. 在 `agentos.py` 中注册 Agent

示例：

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

## 🤝 贡献指南

欢迎贡献！请遵循以下步骤：

1. Fork 本仓库
2. 创建特性分支：`git checkout -b feature/amazing-feature`
3. 提交更改：`git commit -m 'Add amazing feature'`
4. 推送到分支：`git push origin feature/amazing-feature`
5. 提交 Pull Request

### 代码规范

- **Python**：遵循 PEP 8，使用 `black` 格式化
- **TypeScript**：遵循 ESLint 规则，使用 `prettier` 格式化
- **提交信息**：使用清晰的提交信息，描述更改内容

---

## 📝 常见问题

### Q: 为什么上传 URL 时选择 Jina Web Reader？

A: Agno 内置的 `WebsiteReader` 和 `FirecrawlReader` 在解析某些网页时存在 bug。Jina Web Reader 是我们自定义的解决方案，使用 Jina AI 的免费 API，能够完美解析各种复杂网页。

### Q: 如何处理大量历史聊天记录？

A: 可以使用 `create_chat_history_memory_manager` 来批量处理聊天记录：

```python
from config.memory_config import create_chat_history_memory_manager

memory_manager = create_chat_history_memory_manager(db)
# 使用这个 memory_manager 处理聊天记录
```

### Q: 如何修改定时任务的时间？

A: 编辑 crontab 配置：

```bash
# 编辑定时任务
crontab -e

# 修改时间（例如改为每天下午 6 点）
0 18 * * * /data/muskliu/mt/open_pulse/trigger_workflow.sh

# 保存并退出（vim: 按 ESC，输入 :wq）
```

常用时间配置：
- `0 8 * * *` - 每天早上 8:00
- `0 12,18 * * *` - 每天 12:00 和 18:00
- `0 */6 * * *` - 每 6 小时一次
- `0 9 * * 1-5` - 周一到周五 9:00

### Q: 支持哪些 LLM？

A: 支持所有 Agno 兼容的 LLM：
- OpenAI（GPT-4o, GPT-4o-mini 等）
- Anthropic（Claude 3.5 Sonnet 等）
- OpenRouter（访问多种模型）
- 本地模型（通过 Ollama 等）

### Q: 如何备份数据？

A: 备份以下文件/目录：
- `open_pulse.db`（SQLite 数据库）
- `my_knowledge.db`（Knowledge 内容数据库）
- `tmp/lancedb/`（向量数据库）

---

## 📄 许可证

本项目采用 MIT 许可证。详见 [LICENSE](LICENSE) 文件。

---

## 🙏 致谢

- [Agno](https://github.com/agno-agi/agno) - 强大的 AI Agent 框架

---

## 📧 联系方式

如有问题或建议，请：
- 提交 [Issue](https://github.com/eliumusk/open_pulse/issues)
- 加入我们的 [Discord 社区](https://discord.gg/your-invite)

---

<div align="center">
  <p>用 ❤️ 和 Agno 构建</p>
  <p>⭐ 如果这个项目对你有帮助，请给我们一个 Star！</p>
</div>
