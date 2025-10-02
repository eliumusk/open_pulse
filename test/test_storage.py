"""
测试 Workflow 存储的简化脚本
用于验证 workflow 数据是否正确保存到数据库
"""
import asyncio
import sqlite3
import json
from datetime import datetime
from agno.db.sqlite import SqliteDb
from agno.workflow import Workflow, Step
from agno.workflow.types import StepInput, StepOutput
from config.settings import DATABASE_FILE


def simple_newsletter_step(step_input: StepInput) -> StepOutput:
    """
    简化的 newsletter 生成步骤
    只返回一个简单的测试内容，不调用 LLM
    """
    user_input = step_input.input or "AI and technology"
    
    newsletter_content = f"""
# 📰 Test Newsletter

**Generated at:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
**Topic:** {user_input}

## Summary

This is a simplified test newsletter to verify storage functionality.

## Key Points

1. **Storage Test**: Verifying that workflow outputs are saved correctly
2. **Database**: Using SQLite with Agno's default schema
3. **Table**: Data should be in the 'sessions' table
4. **Field**: Complete content should be in the 'runs' JSON field

## Conclusion

If you can see this complete content in the database, storage is working correctly!

---
**Newsletter ID:** test_{datetime.now().strftime('%Y%m%d_%H%M%S')}
**Length:** {len(user_input)} characters input
    """.strip()
    
    print(f"✅ Generated test newsletter: {len(newsletter_content)} characters")
    
    return StepOutput(
        content=newsletter_content,
        success=True,
    )


def create_test_workflow(db: SqliteDb) -> Workflow:
    """
    创建一个简化的测试 workflow
    只有一个步骤，不需要 LLM API
    """
    # 定义步骤
    test_step = Step(
        name="Generate Test Newsletter",
        executor=simple_newsletter_step,
        description="Generate a simple test newsletter without LLM",
    )
    
    # 创建 workflow
    workflow = Workflow(
        name="Test Storage Workflow",
        description="Simplified workflow to test storage functionality",
        db=db,
        store_events=True,  # 存储所有事件
        steps=[test_step],
    )
    
    return workflow


def check_database_storage():
    """
    检查数据库中的 workflow 数据
    """
    print("\n" + "="*80)
    print("📊 Database Storage Check")
    print("="*80 + "\n")
    
    try:
        conn = sqlite3.connect(DATABASE_FILE)
        cursor = conn.cursor()
        
        # 检查表是否存在
        cursor.execute("""
            SELECT name FROM sqlite_master 
            WHERE type='table' 
            ORDER BY name
        """)
        tables = [row[0] for row in cursor.fetchall()]
        print(f"📋 Available tables: {', '.join(tables)}\n")
        
        # 检查 agno_sessions 表中的 workflow 数据（Agno 默认表）
        cursor.execute("""
            SELECT COUNT(*)
            FROM agno_sessions
            WHERE workflow_id IS NOT NULL
        """)
        workflow_count = cursor.fetchone()[0]
        print(f"🔢 Workflow sessions in 'agno_sessions' table: {workflow_count}")

        # 如果有数据，显示最新的一条
        if workflow_count > 0:
            cursor.execute("""
                SELECT session_id, workflow_id, runs, created_at
                FROM agno_sessions
                WHERE workflow_id IS NOT NULL
                ORDER BY created_at DESC
                LIMIT 1
            """)

            row = cursor.fetchone()
            if row:
                session_id, workflow_id, runs_json, created_at = row
                print(f"\n📝 Latest workflow session:")
                print(f"  Session ID: {session_id}")
                print(f"  Workflow ID: {workflow_id}")
                print(f"  Created at: {datetime.fromtimestamp(created_at).strftime('%Y-%m-%d %H:%M:%S')}")

                # 解析 runs（可能需要双重解析）
                if runs_json:
                    # 第一次解析
                    parsed = json.loads(runs_json)

                    # 如果结果是字符串，需要再解析一次（双重 JSON 编码）
                    if isinstance(parsed, str):
                        runs = json.loads(parsed)
                    else:
                        runs = parsed

                    print(f"  Number of runs: {len(runs)}")

                    if runs and len(runs) > 0:
                        latest_run = runs[-1]
                        # runs 可能是字符串或字典
                        if isinstance(latest_run, dict):
                            content = latest_run.get('content', '')
                        elif isinstance(latest_run, str):
                            content = latest_run
                        else:
                            content = str(latest_run)

                        print(f"\n  📄 Content preview:")
                        print(f"  {content[:200]}...")
                        print(f"\n  ✅ Full content length: {len(content)} characters")

        # 检查是否还有其他冗余表
        redundant_tables = ['sessions', 'workflow_sessions', 'newsletter_sessions',
                           'digest_sessions', 'research_sessions']
        found_redundant = False
        for table_name in redundant_tables:
            if table_name in tables:
                cursor.execute(f"SELECT COUNT(*) FROM {table_name} WHERE workflow_id IS NOT NULL")
                count = cursor.fetchone()[0]
                if count > 0:
                    print(f"\n⚠️  Found {count} workflow sessions in '{table_name}' table (should be migrated!)")
                    found_redundant = True

        if not found_redundant:
            print(f"\n✅ No redundant tables found - database is clean!")
        
        conn.close()
        
    except Exception as e:
        print(f"❌ Error checking database: {e}")


async def run_test():
    """
    运行完整的测试流程
    """
    print("\n" + "="*80)
    print("🧪 Workflow Storage Test")
    print("="*80 + "\n")
    
    # 1. 创建数据库实例
    print("1️⃣  Creating database instance...")
    db = SqliteDb(db_file=DATABASE_FILE)
    print(f"   ✅ Database: {DATABASE_FILE}\n")
    
    # 2. 创建测试 workflow
    print("2️⃣  Creating test workflow...")
    workflow = create_test_workflow(db)
    print(f"   ✅ Workflow: {workflow.name}\n")
    
    # 3. 运行 workflow
    print("3️⃣  Running workflow...")
    result = await workflow.arun(
        input="AI, quantum computing, and space exploration",
        user_id="test_user",
    )
    print(f"   ✅ Workflow completed")
    print(f"   📊 Status: {result.status if hasattr(result, 'status') else 'completed'}")
    print(f"   📝 Content length: {len(result.content)} characters\n")
    
    # 4. 显示结果预览
    print("4️⃣  Result preview:")
    print("   " + "-"*76)
    preview = result.content[:300].replace('\n', '\n   ')
    print(f"   {preview}...")
    print("   " + "-"*76 + "\n")
    
    # 5. 检查数据库存储
    print("5️⃣  Checking database storage...")
    await asyncio.sleep(1)  # 等待数据写入
    check_database_storage()
    
    print("\n" + "="*80)
    print("✅ Test completed!")
    print("="*80 + "\n")


if __name__ == "__main__":
    print("""
╔══════════════════════════════════════════════════════════════╗
║                                                              ║
║              🧪 Workflow Storage Test 🧪                     ║
║                                                              ║
║  This script tests if workflow outputs are correctly         ║
║  saved to the database.                                      ║
║                                                              ║
╚══════════════════════════════════════════════════════════════╝
    """)
    
    asyncio.run(run_test())

