# Newsletter 封面图片存储指南

## 📋 概述

Newsletter workflow 现在会自动为每个 newsletter 生成封面图片，使用 Google Gemini 2.5 Flash Image 模型。

---

## 🎯 Workflow 集成状态

✅ **已集成到 AgentOS**

- Workflow 名称：`Newsletter Generation Workflow`
- 访问方式：启动 AgentOS 后在 UI 中可见
- 启动命令：`python3 agentos.py`
- UI 地址：http://localhost:7777

---

## 💾 图片存储机制

### 存储位置

图片存储在 **SQLite 数据库** 中：

```
数据库: open_pulse.db
表: agno_sessions
字段: runs (JSON)
路径: runs[-1]['images']
```

### 数据结构

```json
{
  "session_id": "xxx",
  "workflow_id": "newsletter-generation-workflow",
  "runs": [
    {
      "content": "Newsletter 内容...",
      "images": [
        {
          "id": "uuid",
          "mime_type": "image/png",
          "content": "base64_encoded_image_data"
        }
      ]
    }
  ]
}
```

### 为什么这样存储？

1. **简单直接** - 图片和 newsletter 内容在同一条记录中
2. **事务安全** - 一起保存，一起回滚
3. **无需文件管理** - 不用担心文件丢失、权限问题
4. **适合小规模** - 每天几个 newsletter，数据库完全够用

---

## 🔍 如何查看封面图片

### 方法 1: 使用查看脚本（推荐）

```bash
# 查看最新的 newsletter 和封面
python3 view_newsletter_with_cover.py

# 列出所有 newsletters
python3 view_newsletter_with_cover.py list
```

**脚本会自动：**
1. 从数据库提取最新的 newsletter
2. 解码封面图片
3. 保存到 `output/` 文件夹
4. 自动打开图片（macOS）

**输出示例：**
```
📰 Newsletter Viewer with Cover Image
================================================================================

📋 Session ID: 017b2f10-9b62-4398-959c-b1a3d38574cc
🔄 Workflow ID: newsletter-generation-workflow
📅 Created at: 2025-10-03 15:13:28

📝 Newsletter Content:
--------------------------------------------------------------------------------
✅ Newsletter Generated Successfully!
...

🖼️  Found 1 cover image(s) in workflow run

Image 1:
  ID: 1c3acebc-ddfc-4c3b-aa30-438d0042c994
  MIME Type: image/png
  Size: 1088312 bytes (1062.8 KB)
  ✅ Saved to: output/newsletter_cover_017b2f10_1.png
```

### 方法 2: 直接查询数据库

```bash
# 查看最新的 newsletter session
sqlite3 open_pulse.db "
SELECT 
    session_id,
    workflow_id,
    datetime(created_at, 'unixepoch') as created,
    LENGTH(runs) as data_size
FROM agno_sessions
WHERE workflow_id = 'newsletter-generation-workflow'
ORDER BY created_at DESC
LIMIT 5;
"
```

### 方法 3: 使用 Python 脚本提取

```python
import sqlite3
import json
import base64

conn = sqlite3.connect('open_pulse.db')
cursor = conn.cursor()

# 获取最新的 newsletter
cursor.execute("""
    SELECT runs FROM agno_sessions
    WHERE workflow_id = 'newsletter-generation-workflow'
    ORDER BY created_at DESC LIMIT 1
""")

runs_json = cursor.fetchone()[0]
runs = json.loads(runs_json)
if isinstance(runs, str):
    runs = json.loads(runs)  # 双重解析

# 提取图片
latest_run = runs[-1]
if 'images' in latest_run and latest_run['images']:
    image = latest_run['images'][0]
    image_bytes = base64.b64decode(image['content'])
    
    # 保存图片
    with open('cover.png', 'wb') as f:
        f.write(image_bytes)
    
    print(f"✅ Saved: {len(image_bytes)} bytes")

conn.close()
```

---

## 📂 输出文件夹

### 自动保存规则

**当前行为：**
- ❌ Workflow 运行时 **不会** 自动保存图片到文件
- ✅ 图片只存储在数据库中
- ✅ 使用 `view_newsletter_with_cover.py` 时才会提取到 `output/` 文件夹

**文件命名规则：**
```
output/newsletter_cover_{session_id前8位}_{图片序号}.png
```

**示例：**
```
output/
├── newsletter_cover_017b2f10_1.png
├── newsletter_cover_a3b4c5d6_1.png
└── newsletter_cover_f7e8d9c0_1.png
```

### 为什么不自动保存到文件？

1. **避免文件堆积** - 数据库是唯一真实来源
2. **按需提取** - 只在需要查看时才提取
3. **节省空间** - 不重复存储
4. **简化管理** - 只需管理数据库备份

---

## 🚀 使用流程

### 1. 启动 AgentOS

```bash
python3 agentos.py
```

访问：http://localhost:7777

### 2. 运行 Workflow

在 AgentOS UI 中：
1. 进入 **Workflows** 页面
2. 选择 **Newsletter Generation Workflow**
3. 输入兴趣话题，例如：`I'm interested in AI and quantum computing`
4. 点击 **Run**

### 3. 查看结果

**在 UI 中：**
- 可以看到 newsletter 内容
- 显示 "✅ With cover image" 状态

**提取封面图片：**
```bash
python3 view_newsletter_with_cover.py
```

图片会保存到 `output/` 文件夹并自动打开。

---

## 🔧 技术细节

### Workflow 步骤

```
1. Extract User Context
   ↓
2. Research Phase (Parallel)
   ├─ Brave Search
   └─ Arxiv Search
   ↓
3. Generate Newsletter (LLM)
   ↓
4. Generate Cover Image (Gemini 2.5 Flash Image)  ← 新增
   ↓
5. Save Newsletter (with cover)
```

### 图片生成

**模型：** Google Gemini 2.5 Flash Image  
**Prompt 策略：** 基于 newsletter 标题  
**格式：** PNG  
**大小：** 约 1MB  

**Prompt 模板：**
```
Create a modern, professional newsletter cover image for: {title}. 
Style: clean, minimalist, tech-focused, high quality.
```

### 失败处理

如果图片生成失败：
- ✅ Workflow 继续执行（优雅降级）
- ⚠️ Newsletter 保存时标记为 "No cover image"
- 📝 错误日志记录在控制台

---

## 📊 数据库查询示例

### 查看所有 newsletters

```sql
SELECT 
    session_id,
    datetime(created_at, 'unixepoch') as created,
    LENGTH(runs) as size_bytes
FROM agno_sessions
WHERE workflow_id = 'newsletter-generation-workflow'
ORDER BY created_at DESC;
```

### 检查是否有封面图片

```sql
SELECT 
    session_id,
    datetime(created_at, 'unixepoch') as created,
    json_extract(runs, '$[0].images') IS NOT NULL as has_cover
FROM agno_sessions
WHERE workflow_id = 'newsletter-generation-workflow'
ORDER BY created_at DESC;
```

### 统计封面图片数量

```bash
python3 << 'EOF'
import sqlite3
import json

conn = sqlite3.connect('open_pulse.db')
cursor = conn.cursor()

cursor.execute("""
    SELECT runs FROM agno_sessions
    WHERE workflow_id = 'newsletter-generation-workflow'
""")

total = 0
with_cover = 0

for row in cursor.fetchall():
    total += 1
    runs = json.loads(row[0])
    if isinstance(runs, str):
        runs = json.loads(runs)
    
    if runs and 'images' in runs[-1] and runs[-1]['images']:
        with_cover += 1

print(f"Total newsletters: {total}")
print(f"With cover: {with_cover}")
print(f"Without cover: {total - with_cover}")

conn.close()
EOF
```

---

## 🎯 快速参考

| 操作 | 命令 |
|------|------|
| 启动 AgentOS | `python3 agentos.py` |
| 查看最新 newsletter | `python3 view_newsletter_with_cover.py` |
| 列出所有 newsletters | `python3 view_newsletter_with_cover.py list` |
| 查看数据库 | `sqlite3 open_pulse.db` |
| 打开输出文件夹 | `open output/` |

---

## ✅ 总结

1. **存储位置**：数据库 `agno_sessions` 表的 `runs` 字段
2. **查看方式**：运行 `view_newsletter_with_cover.py`
3. **输出位置**：`output/` 文件夹（按需生成）
4. **集成状态**：已集成到 AgentOS，可直接使用
5. **数据安全**：图片和内容一起存储，事务安全

**一句话总结：**  
图片存在数据库里，用脚本提取到 `output/` 文件夹查看。

