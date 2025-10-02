"""
Test script for Newsletter Generation Workflow
Run this to test the workflow without waiting for scheduled execution
"""
import asyncio
import sys
from datetime import datetime

from workflows import create_newsletter_workflow
from config.settings import validate_settings


async def test_workflow_basic():
    """Test basic workflow execution"""
    print("\n" + "="*60)
    print("🧪 Test 1: Basic Workflow Execution")
    print("="*60 + "\n")
    
    workflow = create_newsletter_workflow()
    
    result = await workflow.arun(
        input="I'm interested in artificial intelligence, quantum computing, and space exploration",
        additional_data={
            "user_id": "test_user_123",
            "session_id": "test_session_456",
        },
        stream=False,
    )
    
    print("\n" + "="*60)
    print("✅ Test 1 Completed!")
    print("="*60)
    print(f"\nResult Preview:\n{result.content[:500]}...\n")
    
    return result


async def test_workflow_streaming():
    """Test workflow with streaming"""
    print("\n" + "="*60)
    print("🧪 Test 2: Workflow with Streaming")
    print("="*60 + "\n")
    
    workflow = create_newsletter_workflow()
    
    result = workflow.arun(
        input="I want to learn about the latest developments in machine learning and robotics",
        additional_data={
            "user_id": "test_user_456",
            "session_id": "test_session_789",
        },
        stream=True,
        stream_intermediate_steps=True,
    )
    
    async for event in result:
        print(f"📡 Event: {event.event}")
        if hasattr(event, 'step_name'):
            print(f"   Step: {event.step_name}")
        if hasattr(event, 'content') and event.content:
            print(f"   Content: {event.content[:100]}...")
        print()
    
    print("\n" + "="*60)
    print("✅ Test 2 Completed!")
    print("="*60 + "\n")


async def test_workflow_background():
    """Test workflow with background execution"""
    print("\n" + "="*60)
    print("🧪 Test 3: Background Workflow Execution")
    print("="*60 + "\n")
    
    workflow = create_newsletter_workflow()
    
    # Start workflow in background
    result = await workflow.arun(
        input="Generate a newsletter about blockchain technology and cryptocurrency",
        additional_data={
            "user_id": "test_user_789",
            "session_id": "test_session_012",
        },
        background=True,
    )
    
    print(f"✅ Workflow started in background")
    print(f"   Run ID: {result.run_id}")
    print(f"   Started at: {datetime.now().isoformat()}")
    print(f"\n⏳ Polling for completion...\n")
    
    # Poll for completion
    max_wait = 300  # 5 minutes
    elapsed = 0
    while not result.has_completed() and elapsed < max_wait:
        await asyncio.sleep(5)
        elapsed += 5
        result = workflow.get_run(result.run_id)
        print(f"   ⏳ Still running... ({elapsed}s elapsed)")
    
    if result.has_completed():
        print(f"\n✅ Workflow completed after {elapsed}s")
        print(f"\nResult Preview:\n{result.content[:500]}...\n")
    else:
        print(f"\n⚠️  Workflow timed out after {elapsed}s")
    
    print("\n" + "="*60)
    print("✅ Test 3 Completed!")
    print("="*60 + "\n")
    
    return result


async def test_multiple_users():
    """Test workflow for multiple users"""
    print("\n" + "="*60)
    print("🧪 Test 4: Multiple Users (Sequential)")
    print("="*60 + "\n")
    
    workflow = create_newsletter_workflow()
    
    users = [
        {
            "user_id": "user_001",
            "interests": "AI and machine learning",
        },
        {
            "user_id": "user_002",
            "interests": "Web development and JavaScript",
        },
        {
            "user_id": "user_003",
            "interests": "Data science and statistics",
        },
    ]
    
    results = []
    for i, user in enumerate(users, 1):
        print(f"\n📰 Processing user {i}/{len(users)}: {user['user_id']}")
        
        result = await workflow.arun(
            input=f"Generate a newsletter about {user['interests']}",
            additional_data={
                "user_id": user["user_id"],
            },
            background=True,
        )
        
        results.append({
            "user_id": user["user_id"],
            "run_id": result.run_id,
            "started_at": datetime.now().isoformat(),
        })
        
        print(f"   ✅ Started (Run ID: {result.run_id})")
        
        # Small delay between users
        await asyncio.sleep(2)
    
    print(f"\n✅ All {len(users)} workflows started")
    print(f"\nResults:")
    for r in results:
        print(f"   - {r['user_id']}: {r['run_id']}")
    
    print("\n" + "="*60)
    print("✅ Test 4 Completed!")
    print("="*60 + "\n")
    
    return results


async def main():
    """Run all tests"""
    print("\n" + "🌟"*30)
    print("Newsletter Generation Workflow - Test Suite")
    print("🌟"*30 + "\n")
    
    # Validate settings
    try:
        validate_settings()
        print("✅ Settings validated\n")
    except Exception as e:
        print(f"❌ Settings validation failed: {e}")
        print("Please check your .env file\n")
        return
    
    # Get test selection from command line
    if len(sys.argv) > 1:
        test_num = sys.argv[1]
        
        if test_num == "1":
            await test_workflow_basic()
        elif test_num == "2":
            await test_workflow_streaming()
        elif test_num == "3":
            await test_workflow_background()
        elif test_num == "4":
            await test_multiple_users()
        else:
            print(f"❌ Unknown test number: {test_num}")
            print("Available tests: 1, 2, 3, 4")
    else:
        # Run all tests
        print("Running all tests...\n")
        
        try:
            await test_workflow_basic()
            await asyncio.sleep(2)
            
            await test_workflow_streaming()
            await asyncio.sleep(2)
            
            await test_workflow_background()
            await asyncio.sleep(2)
            
            await test_multiple_users()
            
        except KeyboardInterrupt:
            print("\n\n⚠️  Tests interrupted by user")
        except Exception as e:
            print(f"\n\n❌ Test failed with error: {e}")
            import traceback
            traceback.print_exc()
    
    print("\n" + "🌟"*30)
    print("Test Suite Completed!")
    print("🌟"*30 + "\n")


if __name__ == "__main__":
    print("""
Usage:
    python test_workflow.py           # Run all tests
    python test_workflow.py 1         # Test 1: Basic execution
    python test_workflow.py 2         # Test 2: Streaming
    python test_workflow.py 3         # Test 3: Background execution
    python test_workflow.py 4         # Test 4: Multiple users
    """)
    
    asyncio.run(main())

