# 📦 Newsletter 存储指南

## 概述

Open Pulse 使用 **Agno 的自动存储系统**来保存生成的 newsletter。你不需要手动编写存储逻辑！

## 🔑 关键概念

### 1. **Workflow 自动存储**

当你在 workflow 中配置 `db=db` 时，Agno 会自动：
- ✅ 保存每次 workflow 执行到数据库
- ✅ 存储完整的输出内容
- ✅ 记录所有执行事件（如果启用 `store_events=True`）
- ✅ 维护 session 历史

### 2. **数据库表结构**

根据 Agno 文档，workflow sessions 存储在 `sessions` 表中：

```sql
CREATE TABLE sessions (
    session_id TEXT PRIMARY KEY,
    workflow_id TEXT,
    workflow_name TEXT,
    user_id TEXT,
    runs TEXT,              -- JSON list of all workflow runs
    session_data TEXT,      -- JSON session data
    session_state TEXT,     -- JSON session state
    workflow_data TEXT,     -- JSON workflow configuration
    metadata TEXT,          -- JSON metadata
    created_at INTEGER,     -- Unix timestamp
    updated_at INTEGER      -- Unix timestamp
);
```

**重要字段：**
- `runs`: JSON 列表，包含所有 workflow 执行记录
- 每个 run 包含：
  - `run_id`: 执行 ID
  - `content`: **完整的 newsletter 内容**
  - `status`: 执行状态
  - `metrics`: 性能指标
  - `created_at`: 创建时间

### 3. **Event Storage（可选）**

我们启用了 `store_events=True`，这意味着：
- ✅ 所有 workflow 事件都会被记录
- ✅ 可以追踪每个 step 的执行
- ✅ 方便调试和分析

```python
workflow = Workflow(
    name="Newsletter Generation Workflow",
    db=db,
    store_events=True,  # 🔑 启用事件存储
    steps=[...],
)
```

## 📊 如何查看生成的 Newsletter

### 方法 1: 使用 `view_newsletters.py` 脚本

```bash
# 查看所有 newsletters
python view_newsletters.py

# 查看最新的 newsletter（完整内容）
python view_newsletters.py latest

# 查看特定 session 的 newsletter
python view_newsletters.py <session_id>
```

### 方法 2: 在 AgentOS UI 中查看

1. 打开 AgentOS UI: http://localhost:7777
2. 进入 **Sessions** 页面
3. 筛选 `type=workflow`
4. 点击任意 session 查看详情
5. 在 **Runs** 标签中查看完整的 newsletter 内容

### 方法 3: 直接查询数据库

```python
import sqlite3
import json

conn = sqlite3.connect('tmp/data.db')
cursor = conn.cursor()

# 获取最新的 newsletter
cursor.execute("""
    SELECT session_id, runs 
    FROM sessions 
    WHERE workflow_id IS NOT NULL 
    ORDER BY created_at DESC 
    LIMIT 1
""")

session_id, runs_json = cursor.fetchone()
runs = json.loads(runs_json)
latest_run = runs[-1]
content = latest_run['content']

print(content)
```

## 🎯 为什么 UI 上只显示预览？

**之前的问题：**
`save_newsletter` 函数返回的是一个摘要，而不是完整内容：

```python
# ❌ 旧版本（只返回预览）
save_result = f"""
    Preview:
    {newsletter_content[:200]}...
"""
```

**现在的解决方案：**
```python
# ✅ 新版本（返回完整内容）
complete_output = f"""
    ✅ Newsletter Generated Successfully!
    
    {newsletter_content}  # 完整内容
    
    📊 Stats: {len(newsletter_content)} characters
"""
```

## 💡 存储最佳实践

### 1. **不要手动存储 Newsletter**

❌ **错误做法：**
```python
# 不需要这样做！
def save_newsletter(content):
    with open('newsletter.txt', 'w') as f:
        f.write(content)
```

✅ **正确做法：**
```python
# Agno 会自动存储！
return StepOutput(
    content=complete_newsletter,  # 返回完整内容即可
    success=True,
)
```

### 2. **使用 `store_events` 进行调试**

开发阶段：
```python
workflow = Workflow(
    store_events=True,  # 存储所有事件
    steps=[...],
)
```

生产环境（可选优化）：
```python
from agno.run.workflow import WorkflowRunEvent

workflow = Workflow(
    store_events=True,
    events_to_skip=[
        WorkflowRunEvent.step_started,  # 跳过冗余事件
        WorkflowRunEvent.parallel_execution_started,
    ],
    steps=[...],
)
```

### 3. **Session 管理**

每次 workflow 执行都会创建一个新的 session（除非你指定 `session_id`）：

```python
# 自动生成新 session
result = await workflow.arun(input="...")

# 继续现有 session
result = await workflow.arun(
    input="...",
    session_id="existing_session_id"
)
```

## 🔍 数据大小考虑

### Newsletter 大小估算

典型的 newsletter：
- 文本内容: 2-10 KB
- JSON 元数据: 1-2 KB
- 总计: ~5-15 KB per newsletter

### SQLite 限制

- 默认最大数据库大小: **140 TB** (理论上)
- 单行最大大小: **1 GB**
- 对于 newsletter 应用完全足够！

### 如果需要存储大量数据

如果你计划存储大量 newsletters（例如 >100万条），考虑：

1. **定期清理旧数据**
```python
# 删除 30 天前的 newsletters
cursor.execute("""
    DELETE FROM sessions 
    WHERE workflow_id IS NOT NULL 
    AND created_at < ?
""", (time.time() - 30*24*3600,))
```

2. **迁移到 PostgreSQL**
```python
from agno.db.postgres import PostgresDb

db = PostgresDb(db_url="postgresql://...")
```

3. **使用外部存储**（如 S3）存储 newsletter 内容，数据库只存储元数据

## 📝 总结

✅ **你已经有了完整的存储系统！**
- Workflow 自动保存到数据库
- 完整内容存储在 `runs` 字段
- 使用 `view_newsletters.py` 查看
- 在 AgentOS UI 中也可以查看

✅ **不需要额外的存储逻辑！**
- 不需要手动写文件
- 不需要额外的数据库表
- Agno 已经处理好了一切

✅ **存储是持久化的！**
- 数据保存在 `tmp/data.db`
- 重启服务器后数据仍然存在
- 可以随时查询历史 newsletters

🎉 **现在你可以专注于改进 newsletter 的内容质量，而不用担心存储问题！**

