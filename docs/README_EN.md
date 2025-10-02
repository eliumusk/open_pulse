# Open Pulse 🌊

An intelligent, agentic newsletter application powered by Agno framework.

> **Status**: ✅ MVP Complete - Workflow and Scheduler fully functional!

## 🎯 What is Open Pulse?

Open Pulse is an **autonomous newsletter system** that:

1. 💬 **Learns** - Chats with users to understand their interests
2. 🔍 **Researches** - Autonomously searches for relevant content after conversations
3. ✍️ **Generates** - Creates personalized newsletters at scheduled times
4. 📬 **Delivers** - Provides curated content based on user preferences

### The Magic ✨

Unlike traditional newsletters, Open Pulse **continues working after you stop chatting**. It digests your conversation, researches your interests, and generates fresh content automatically!

## 🚀 Quick Start

### Prerequisites

- Python 3.12+
- OpenRouter API key
- Brave Search API key

### Installation & Setup

```bash
# 1. Clone and setup
git clone <repository-url>
cd open_pulse
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt

# 2. Configure (copy .env.example to .env and fill in API keys)
cp .env.example .env

# 3. Run AgentOS
python agentos.py

# 4. Test workflow
python quick_test.py

# 5. Start scheduler
python scheduler.py
```

Visit **http://localhost:7777** to chat with Newsletter Agent!

## 📚 Documentation

| Document | Description |
|----------|-------------|
| [SCHEDULER_GUIDE.md](SCHEDULER_GUIDE.md) | Complete scheduler usage guide |
| [WORKFLOW_SUMMARY.md](WORKFLOW_SUMMARY.md) | Implementation details |
| [README.md](README.md) | Chinese version |

## 🎯 MVP Status

### ✅ Completed

- [x] Project setup & configuration
- [x] Core agents (Newsletter, Digest, Research)
- [x] MCP integration (Brave Search, Arxiv)
- [x] Newsletter generation workflow (4 steps)
- [x] Parallel research phase
- [x] Flexible scheduler (3 modes)
- [x] Complete testing infrastructure
- [x] Comprehensive documentation

### 🚀 Next Steps

- [ ] User database integration
- [ ] Memory extraction from sessions
- [ ] Newsletter quality checks (Loop)
- [ ] Email delivery
- [ ] Web UI
- [ ] Monitoring & alerts

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    AgentOS (Port 7777)                   │
│  • Built-in FastAPI server                               │
│  • Session & Memory management                           │
└─────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────┐
│                    Agno Agents                           │
│  • Newsletter Agent (Conversational)                     │
│  • Digest Agent (Content Generator)                      │
│  • Research Agent (Information Gatherer)                 │
└─────────────────────────────────────────────────────────┐
                          ↓
┌─────────────────────────────────────────────────────────┐
│              Newsletter Generation Workflow              │
│  Step 1: Extract User Context                            │
│  Step 2: Parallel Research (Brave + Arxiv)               │
│  Step 3: Generate Newsletter (Digest Agent)              │
│  Step 4: Save Newsletter                                 │
└─────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────┐
│                    Scheduler                             │
│  • Development: Every 2 minutes                          │
│  • Production: Daily at 8:00 AM                          │
│  • Once: Single execution                                │
└─────────────────────────────────────────────────────────┘
```

## 🔧 Key Features

### 1. 💬 Conversational Learning
- Natural conversation interface
- Automatic memory management
- Session persistence

### 2. 🔍 Autonomous Research
- Parallel web & academic search
- MCP-based tool integration
- Automatic content synthesis

### 3. ✍️ Intelligent Generation
- Structured newsletter format
- Personalized content
- Quality-focused output

### 4. ⏰ Flexible Scheduling
- **Development**: Every 2 minutes (testing)
- **Production**: Daily at 8:00 AM (deployment)
- **Once**: Single execution (debugging)

## 🧪 Testing

```bash
# Quick test (recommended)
python quick_test.py

# Full test suite
python test_workflow.py        # All tests
python test_workflow.py 1      # Basic execution
python test_workflow.py 2      # Streaming
python test_workflow.py 3      # Background execution
python test_workflow.py 4      # Multiple users
```

## 📁 Project Structure

```
open_pulse/
├── 📄 README.md                    # Chinese version
├── 📄 README_EN.md                 # This file
├── 📄 SCHEDULER_GUIDE.md           # Scheduler guide
├── 📄 WORKFLOW_SUMMARY.md          # Implementation details
├── 🚀 agentos.py                   # AgentOS server
├── ⏰ scheduler.py                 # Newsletter scheduler
├── 🧪 test_workflow.py             # Test suite
├── ⚡ quick_test.py                # Quick test
├── 🤖 agents/                      # Agent definitions
├── 🔄 workflows/                   # Workflow definitions
├── 🔧 tools/                       # MCP tools
├── ⚙️ config/                      # Configuration
└── 💾 open_pulse.db                # SQLite database
```

## 🛠️ Customization

### Add Research Sources

```python
# workflows/newsletter_generation.py
research_step_3 = Step(
    name="Research Social Media",
    agent=social_media_agent,
)

research_phase = Parallel(
    research_step_1,
    research_step_2,
    research_step_3,  # New!
)
```

### Modify Schedule

```python
# scheduler.py
scheduler.start_development_mode(interval_minutes=5)  # Every 5 min
```

### Add Quality Checks

```python
from agno.workflow import Loop

def quality_check(outputs):
    content = outputs[-1].content
    return len(content) > 500 and "##" in content

newsletter_loop = Loop(
    steps=[generate_newsletter_step],
    end_condition=quality_check,
    max_iterations=3,
)
```

## 🐛 Troubleshooting

| Problem | Solution |
|---------|----------|
| Workflow fails | Check API keys, internet connection |
| Scheduler not running | Verify `SCHEDULER_MODE` in `.env` |
| Tests timeout | Increase `max_wait_seconds` |
| Import errors | Activate venv, reinstall dependencies |

## 📖 Learn More

- [Agno Documentation](https://docs.agno.com)
- [MCP Protocol](https://modelcontextprotocol.io)
- [OpenRouter](https://openrouter.ai)

## 🙏 Acknowledgments

- **Agno Team** - Amazing multi-agent framework
- **Anthropic** - Claude 3.5 Sonnet
- **Brave** - Search API
- **Arxiv** - Academic paper access

---

**Built with ❤️ using [Agno](https://agno.com)**

🌊 **Open Pulse** - Your autonomous newsletter companion

