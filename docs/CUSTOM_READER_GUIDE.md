# 📚 自定义 Reader 开发指南

完整的自定义 Reader 实现指南，包含关键点总结和最佳实践。

## 🎯 核心概念

### 什么是 Reader？
Reader 是 Agno Knowledge 系统中用于解析和提取内容的组件。每个 reader 负责处理特定类型的数据源（文件、URL、文本等）。

### 为什么需要自定义 Reader？
- Agno 内置的 web readers（WebsiteReader, FirecrawlReader）存在 bug
- 需要支持特定的数据源（如微信公众号、特定网站）
- 需要自定义解析逻辑

---

## ✅ 关键点总结（最重要！）

### 1. **双重注册机制** 🔑

这是**最关键**的部分！AgentOS 处理 `reader_id` 时有两个查找路径：

```python
# AgentOS 源码 (knowledge.py:815-830)
if reader_id:
    reader = None
    # 1️⃣ 首先检查 knowledge.readers 字典（优先级最高）
    if knowledge.readers and reader_id in knowledge.readers:
        reader = knowledge.readers[reader_id]
    # 2️⃣ 如果没找到，尝试通过 ReaderFactory 创建
    else:
        key = reader_id.lower().strip().replace("-", "_").replace(" ", "_")
        reader = ReaderFactory.create_reader(key)
```

**因此必须同时注册到两个地方：**

```python
# ✅ 正确做法
# 1. 添加到 knowledge.readers（AgentOS 优先检查这里！）
if not knowledge.readers:
    knowledge.readers = {}
knowledge.readers["MyReader"] = my_reader_instance

# 2. 注册到 ReaderFactory（作为备用）
def create_my_reader(**kwargs):
    return MyReader(**kwargs)

ReaderFactory.register_reader(
    key="MyReader",
    reader_method=create_my_reader,
    name="My Reader",
    description="Description",
    extensions=None
)
```

**❌ 错误做法（只注册到 ReaderFactory）：**
```python
# 这样不行！AgentOS 找不到 reader
ReaderFactory.register_reader(...)  # 只注册这个是不够的
```

### 2. **Reader 接口要求**

所有 reader 必须实现两个方法：

```python
from agno.knowledge.reader.base import Reader
from agno.document import Document
from typing import List, Optional

class MyReader(Reader):
    def read(self, obj, name: Optional[str] = None) -> List[Document]:
        """同步读取和处理内容"""
        pass
    
    async def async_read(self, obj, name: Optional[str] = None) -> List[Document]:
        """异步读取和处理内容"""
        # 简单情况下可以直接包装同步版本
        import asyncio
        return await asyncio.to_thread(self.read, obj, name)
```

### 3. **统一注册系统**

使用 `readers/registry.py` 统一管理所有自定义 readers：

```python
# agents/digest_agent.py
from readers import register_all_readers

knowledge = Knowledge(...)
reader_status = register_all_readers(knowledge)  # 一行代码搞定！

# 输出注册状态
for reader_name, status in reader_status.items():
    if status == "registered":
        print(f"✅ Registered {reader_name}")
```

### 4. **前端集成**

前端通过 `reader_id` 参数指定 reader：

```typescript
await uploadKnowledgeContentAPI(endpoint, dbId, {
  url: "https://example.com",
  reader_id: "MyCustomReader",  // 必须与注册时的 key 一致！
  chunker: "default"
})
```

---

## 🔧 完整实现步骤

### 步骤 1: 创建 Reader 类

在 `readers/` 目录下创建新文件（如 `my_reader.py`）：

```python
"""
My Custom Reader - Description of what it does
"""
import os
import requests
from typing import List, Optional
from agno.knowledge.reader.base import Reader
from agno.document import Document


class MyCustomReader(Reader):
    """
    Custom reader for [your data source]
    
    Args:
        api_key: API key for the service (optional)
        timeout: Request timeout in seconds
        max_retries: Maximum number of retry attempts
        **kwargs: Additional arguments passed to Reader base class
    """
    
    def __init__(
        self,
        api_key: Optional[str] = None,
        timeout: int = 30,
        max_retries: int = 3,
        **kwargs
    ):
        super().__init__(**kwargs)
        self.api_key = api_key or os.getenv("MY_API_KEY")
        self.timeout = timeout
        self.max_retries = max_retries
        
        if not self.api_key:
            print("⚠️  Warning: MY_API_KEY not set")
    
    def read(self, obj, name: Optional[str] = None) -> List[Document]:
        """
        Synchronously read and process content
        
        Args:
            obj: Input object (URL, file path, etc.)
            name: Optional name for the document
            
        Returns:
            List of Document objects
        """
        print(f"📖 Reading with MyCustomReader: {obj}")
        
        try:
            # 1. Fetch/read the content
            content = self._fetch_content(obj)
            
            # 2. Process/clean the content
            processed_content = self._process_content(content)
            
            # 3. Create Document objects
            doc = Document(
                name=name or f"Document from {obj}",
                content=processed_content,
                meta_data={
                    "source": obj,
                    "reader": "MyCustomReader",
                }
            )
            
            print(f"✅ Successfully read {len(processed_content)} characters")
            return [doc]
            
        except Exception as e:
            print(f"❌ Error reading {obj}: {e}")
            raise
    
    async def async_read(self, obj, name: Optional[str] = None) -> List[Document]:
        """Asynchronously read and process content"""
        import asyncio
        return await asyncio.to_thread(self.read, obj, name)
    
    def _fetch_content(self, obj: str) -> str:
        """Fetch content from source with retry logic"""
        for attempt in range(self.max_retries):
            try:
                # Your fetching logic here
                response = requests.get(obj, timeout=self.timeout)
                response.raise_for_status()
                return response.text
            except Exception as e:
                if attempt == self.max_retries - 1:
                    raise
                print(f"⚠️  Retry {attempt + 1}/{self.max_retries}: {e}")
                
    def _process_content(self, content: str) -> str:
        """Process and clean the content"""
        # Your processing logic here
        return content.strip()
```

### 步骤 2: 注册到 Registry

编辑 `readers/registry.py`，添加注册函数：

```python
from .my_reader import MyCustomReader

def _register_my_custom_reader(knowledge: Knowledge) -> str:
    """Register MyCustomReader with the Knowledge instance."""
    api_key = os.getenv("MY_API_KEY")
    
    if not api_key:
        return "skipped: MY_API_KEY not found"
    
    try:
        # 1. Create reader instance
        custom_reader = MyCustomReader(
            api_key=api_key,
            name="My Custom Reader",
            description="Description of what this reader does"
        )
        
        # 2. Add to knowledge.readers (AgentOS checks this first!)
        knowledge.readers["MyCustomReader"] = custom_reader
        
        # 3. Also register with ReaderFactory (for fallback)
        def create_custom_reader(**kwargs):
            return MyCustomReader(api_key=api_key, **kwargs)
        
        ReaderFactory.register_reader(
            key="MyCustomReader",
            reader_method=create_custom_reader,
            name="My Custom Reader",
            description="Description of what this reader does",
            extensions=None  # or [".ext"] for file-based readers
        )
        
        return "registered"
        
    except Exception as e:
        return f"failed: {str(e)}"


def register_all_readers(knowledge: Knowledge) -> dict:
    """Register all custom readers"""
    status = {}
    
    # Existing readers
    jina_status = _register_jina_reader(knowledge)
    status['JinaWebReader'] = jina_status
    
    # Add your custom reader
    custom_status = _register_my_custom_reader(knowledge)
    status['MyCustomReader'] = custom_status
    
    return status
```

### 步骤 3: 导出 Reader

编辑 `readers/__init__.py`：

```python
from .jina_reader import JinaWebReader
from .my_reader import MyCustomReader
from .registry import register_all_readers

__all__ = ['JinaWebReader', 'MyCustomReader', 'register_all_readers']
```

### 步骤 4: 添加到前端

编辑 `agent-ui/src/components/chat/Sidebar/Knowledge/UploadFileDialog.tsx`：

```typescript
<Select value={readerId} onValueChange={setReaderId}>
  <SelectItem value="auto">Auto-detect</SelectItem>
  {/* ... existing readers ... */}
  <SelectItem value="MyCustomReader">My Custom Reader</SelectItem>
</Select>
```

### 步骤 5: 配置环境变量

在 `.env.example` 和 `.env` 中添加：

```bash
# My Custom Reader API Key
MY_API_KEY=your_api_key_here
```

---

## 🧪 测试 Reader

创建测试文件 `test_my_reader.py`：

```python
import asyncio
from readers import MyCustomReader

async def test_reader():
    print("🧪 Testing MyCustomReader\n")
    
    reader = MyCustomReader(api_key="your_key")
    
    # Test sync
    print("1️⃣ Testing sync read...")
    docs = reader.read("https://example.com")
    print(f"   ✅ Got {len(docs)} documents\n")
    
    # Test async
    print("2️⃣ Testing async read...")
    docs = await reader.async_read("https://example.com")
    print(f"   ✅ Got {len(docs)} documents\n")
    
    print("✅ All tests passed!")

if __name__ == "__main__":
    asyncio.run(test_reader())
```

---

## 📝 最佳实践

### 1. API Key 管理
```python
# ✅ 好的做法
self.api_key = api_key or os.getenv("MY_API_KEY")
if not self.api_key:
    print("⚠️  Warning: MY_API_KEY not set")

# ❌ 不好的做法
self.api_key = api_key  # 没有从环境变量读取
if not self.api_key:
    raise ValueError("API key required")  # 太严格，应该允许可选
```

### 2. 错误处理
```python
# ✅ 好的做法：重试机制
for attempt in range(self.max_retries):
    try:
        return self._fetch()
    except Exception as e:
        if attempt == self.max_retries - 1:
            raise
        print(f"⚠️  Retry {attempt + 1}: {e}")
        time.sleep(2 ** attempt)  # 指数退避

# ❌ 不好的做法：直接失败
return self._fetch()  # 没有重试
```

### 3. 日志记录
```python
# ✅ 好的做法
print(f"📖 Reading with MyReader: {url}")
print(f"✅ Successfully read {len(content)} characters")
print(f"❌ Error: {e}")

# ❌ 不好的做法
# 没有任何日志输出
```

### 4. 元数据
```python
# ✅ 好的做法
Document(
    name=name or f"Document from {url}",
    content=content,
    meta_data={
        "source": url,
        "reader": "MyReader",
        "timestamp": datetime.now().isoformat(),
    }
)

# ❌ 不好的做法
Document(content=content)  # 缺少元数据
```

---

## 💡 常见问题

### Q: 为什么我的 reader 没有被调用？
**A:** 检查是否同时注册到了 `knowledge.readers` 和 `ReaderFactory`。这是最常见的问题！

### Q: 如何调试 reader？
**A:** 在 reader 中添加 `print()` 语句，查看 AgentOS 终端日志。

### Q: 可以覆盖内置 reader 吗？
**A:** 可以！只需使用相同的 key 注册即可覆盖。

### Q: 如何支持多种输入类型？
**A:** 在 `read()` 方法中检查 `obj` 的类型：
```python
def read(self, obj, name=None):
    if isinstance(obj, str):
        if obj.startswith("http"):
            return self._read_url(obj)
        else:
            return self._read_file(obj)
    elif isinstance(obj, bytes):
        return self._read_bytes(obj)
```

---

## 🔗 参考资源

- [JinaWebReader 实现](../readers/jina_reader.py) - 完整的参考实现
- [Registry 系统](../readers/registry.py) - 统一注册系统
- [Agno Knowledge 文档](https://docs.agno.com/concepts/knowledge)
- [Agno Reader 接口](https://docs.agno.com/api-reference/knowledge/reader)

---

## 📊 实现检查清单

在提交你的自定义 reader 之前，确保：

- [ ] 实现了 `read()` 和 `async_read()` 方法
- [ ] 同时注册到 `knowledge.readers` 和 `ReaderFactory`
- [ ] 添加到 `readers/registry.py` 的 `register_all_readers()`
- [ ] 导出到 `readers/__init__.py`
- [ ] 添加到前端 dropdown
- [ ] 配置环境变量
- [ ] 编写测试代码
- [ ] 添加错误处理和重试机制
- [ ] 包含详细的日志输出
- [ ] 添加元数据到 Document

---

需要帮助？查看 [JinaWebReader 实现](../readers/jina_reader.py) 作为完整示例！

