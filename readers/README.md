# Custom Readers for Open Pulse

This directory contains custom reader implementations for the Open Pulse knowledge system.

## 📚 Available Readers

### JinaWebReader

A custom web content reader using [Jina AI's Reader API](https://jina.ai/reader).

**Why use JinaWebReader?**
- ✅ **Solves Agno's web reader bugs**: All built-in web readers (WebsiteReader, FirecrawlReader) have issues
- ✅ **Free tier available**: No credit card required
- ✅ **Handles complex sites**: Works with JavaScript-rendered pages, WeChat public accounts, etc.
- ✅ **LLM-optimized output**: Returns clean markdown perfect for RAG
- ✅ **Simple HTTP API**: No SDK installation required

**Setup:**

1. Get a free API key from https://jina.ai/reader

2. Add to your `.env` file:
   ```bash
   JINA_API_KEY=jina_xxxxxxxxxxxxxxxxxxxxxxxxxxxxx
   ```

3. Restart AgentOS:
   ```bash
   python agentos.py
   ```

**Usage in UI:**

1. Click "Add" in the Knowledge panel
2. Enter a URL
3. Open "Advanced Options"
4. Select "Jina Web Reader" from the Reader Type dropdown
5. Click Upload

**Usage in Code:**

```python
from readers import JinaWebReader

# Initialize reader
reader = JinaWebReader(api_key="jina_xxx...")

# Read a URL
docs = reader.read("https://example.com")

# Or async
docs = await reader.async_read("https://example.com")

# Add to knowledge base
knowledge.add_content(
    url="https://example.com",
    reader=reader,
    chunk=True
)
```

**Supported Chunking Strategies:**
- FixedSizeChunking
- SemanticChunking
- RecursiveChunking
- DocumentChunking
- AgenticChunking

## 🔧 Creating Custom Readers

To create your own custom reader:

1. Create a new file in this directory (e.g., `my_reader.py`)

2. Inherit from Agno's `Reader` base class:

```python
from typing import List
from agno.document import Document
from agno.knowledge.reader.base import Reader
from agno.utils.log import logger


class MyCustomReader(Reader):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # Your initialization code
    
    def read(self, obj, name: str = None) -> List[Document]:
        """Synchronous read method"""
        try:
            # Your reading logic here
            content = self._fetch_content(obj)
            
            doc = Document(
                name=name or str(obj),
                content=content,
                meta_data={
                    "source": str(obj),
                    "reader": "MyCustomReader"
                }
            )
            return [doc]
        except Exception as e:
            logger.error(f"Error reading: {e}")
            return []
    
    async def async_read(self, obj, name: str = None) -> List[Document]:
        """Asynchronous read method"""
        import asyncio
        return await asyncio.to_thread(self.read, obj, name)
    
    def get_supported_chunking_strategies(self) -> List[str]:
        """Return list of supported chunking strategies"""
        return [
            "FixedSizeChunking",
            "SemanticChunking",
            "RecursiveChunking"
        ]
```

3. Register your reader in `agents/digest_agent.py` and `agents/newsletter_agent.py`:

```python
from agno.knowledge.reader.factory import ReaderFactory
from readers import MyCustomReader

# Register custom reader
my_reader = MyCustomReader()
ReaderFactory.register_reader("MyCustomReader", my_reader)
```

4. Add to the UI dropdown in `agent-ui/src/components/chat/Sidebar/Knowledge/UploadFileDialog.tsx`:

```tsx
<SelectItem value="MyCustomReader">My Custom Reader</SelectItem>
```

## 📖 Resources

- [Agno Documentation](https://docs.agno.com)
- [Agno Reader Guide](https://docs.agno.com/knowledge/readers)
- [Jina AI Reader API](https://jina.ai/reader)

## 🐛 Troubleshooting

**JinaWebReader not showing in UI:**
- Make sure you've restarted AgentOS after adding the JINA_API_KEY
- Check the console output for "✅ Registered JinaWebReader"

**"No Jina API key provided" warning:**
- Add JINA_API_KEY to your `.env` file
- Get a free key at https://jina.ai/reader

**Content processing stuck at "processing":**
- Check AgentOS logs for errors
- Try refreshing the Knowledge panel
- The status polling will automatically update when processing completes

**Rate limit errors:**
- Jina's free tier has rate limits
- Wait a few seconds between requests
- Consider upgrading to a paid plan for higher limits

