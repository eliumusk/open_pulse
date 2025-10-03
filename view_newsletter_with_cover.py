"""
查看 Newsletter 和封面图片
从数据库中提取最新的 newsletter 和封面图片
"""
import sqlite3
import json
import base64
from datetime import datetime
from pathlib import Path

from config.settings import DATABASE_FILE


def view_latest_newsletter():
    """
    查看最新的 newsletter 和封面图片
    """
    print("\n" + "="*80)
    print("📰 Newsletter Viewer with Cover Image")
    print("="*80 + "\n")
    
    try:
        conn = sqlite3.connect(DATABASE_FILE)
        cursor = conn.cursor()
        
        # 查询最新的 workflow session
        cursor.execute("""
            SELECT 
                session_id,
                workflow_id,
                session_data,
                runs,
                created_at
            FROM agno_sessions
            WHERE workflow_id = 'newsletter-generation-workflow'
            ORDER BY created_at DESC
            LIMIT 1
        """)
        
        row = cursor.fetchone()
        
        if not row:
            print("❌ No newsletter found in database")
            return
        
        session_id, workflow_id, session_data_json, runs_json, created_at = row
        
        print(f"📋 Session ID: {session_id}")
        print(f"🔄 Workflow ID: {workflow_id}")
        print(f"📅 Created at: {datetime.fromtimestamp(created_at).strftime('%Y-%m-%d %H:%M:%S')}")
        print()
        
        # 解析 runs（双重 JSON 编码）
        runs = json.loads(runs_json)
        if isinstance(runs, str):
            runs = json.loads(runs)
        
        if runs and len(runs) > 0:
            latest_run = runs[-1]
            content = latest_run.get('content', '') if isinstance(latest_run, dict) else str(latest_run)

            print("📝 Newsletter Content:")
            print("-" * 80)
            # 显示前 500 字符
            print(content[:500])
            if len(content) > 500:
                print(f"\n... (total {len(content)} characters)")
            print("-" * 80)
            print()

            # 检查 runs 中的图片（Agno 将图片存储在这里）
            if isinstance(latest_run, dict) and 'images' in latest_run:
                images = latest_run['images']

                if images and len(images) > 0:
                    print(f"🖼️  Found {len(images)} cover image(s) in workflow run")
                    print()

                    for idx, image_data in enumerate(images):
                        print(f"Image {idx + 1}:")

                        if isinstance(image_data, dict):
                            image_id = image_data.get('id', 'unknown')
                            mime_type = image_data.get('mime_type', 'image/png')

                            # 图片数据在 'content' 字段
                            image_bytes = None
                            if 'content' in image_data:
                                content_data = image_data['content']
                                if isinstance(content_data, str):
                                    # Base64 编码
                                    try:
                                        image_bytes = base64.b64decode(content_data)
                                    except:
                                        print(f"  ⚠️  Failed to decode base64 image")
                                elif isinstance(content_data, bytes):
                                    image_bytes = content_data

                            if image_bytes:
                                print(f"  ID: {image_id}")
                                print(f"  MIME Type: {mime_type}")
                                print(f"  Size: {len(image_bytes)} bytes ({len(image_bytes) / 1024:.1f} KB)")

                                # 保存图片到文件
                                output_dir = Path("output")
                                output_dir.mkdir(exist_ok=True)

                                filename = f"newsletter_cover_{session_id[:8]}_{idx+1}.png"
                                output_path = output_dir / filename

                                with open(output_path, 'wb') as f:
                                    f.write(image_bytes)

                                print(f"  ✅ Saved to: {output_path}")
                                print()
                            else:
                                print(f"  ⚠️  No image data found")
                                print(f"  Debug: image_data keys: {list(image_data.keys())}")
                else:
                    print("⚠️  No cover images found in workflow run")
            else:
                print("⚠️  No 'images' field in workflow run")
        
        conn.close()
        
        print("="*80)
        print("✅ Done!")
        print("="*80)
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()


def list_all_newsletters():
    """
    列出所有的 newsletters
    """
    print("\n" + "="*80)
    print("📚 All Newsletters")
    print("="*80 + "\n")
    
    try:
        conn = sqlite3.connect(DATABASE_FILE)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT 
                session_id,
                workflow_id,
                created_at,
                LENGTH(session_data) as session_data_size,
                LENGTH(runs) as runs_size
            FROM agno_sessions
            WHERE workflow_id = 'newsletter-generation-workflow'
            ORDER BY created_at DESC
        """)
        
        rows = cursor.fetchall()
        
        if not rows:
            print("❌ No newsletters found")
            return
        
        print(f"Found {len(rows)} newsletter(s):\n")
        
        for idx, row in enumerate(rows, 1):
            session_id, workflow_id, created_at, session_data_size, runs_size = row
            created = datetime.fromtimestamp(created_at).strftime('%Y-%m-%d %H:%M:%S')
            
            print(f"{idx}. Session: {session_id[:20]}...")
            print(f"   Created: {created}")
            print(f"   Session Data: {session_data_size} bytes")
            print(f"   Runs Data: {runs_size} bytes")
            print()
        
        conn.close()
        
    except Exception as e:
        print(f"❌ Error: {e}")


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "list":
        list_all_newsletters()
    else:
        view_latest_newsletter()

