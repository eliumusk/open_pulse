"""
测试带封面图片的 Newsletter Workflow
"""
import asyncio
from workflows import create_newsletter_workflow


async def test_workflow():
    """
    测试 workflow 是否正常工作
    """
    print("\n" + "="*80)
    print("🧪 Testing Newsletter Workflow with Cover Image")
    print("="*80 + "\n")
    
    # 创建 workflow
    workflow = create_newsletter_workflow()
    
    # 运行 workflow
    print("🚀 Running workflow...")
    print()
    
    result = await workflow.arun(
        input="I'm interested in AI, quantum computing, and space exploration",
        additional_data={
            "user_id": "test_user_cover",
            "session_id": "test_session_cover",
        },
        stream=False,
    )
    
    print("\n" + "="*80)
    print("✅ Workflow completed!")
    print("="*80 + "\n")
    
    print("📊 Result:")
    print(f"  Status: {result.status}")
    print(f"  Content length: {len(result.content)} characters")
    print(f"  Has images: {result.images is not None and len(result.images) > 0}")
    
    if result.images:
        print(f"  Number of images: {len(result.images)}")
        for idx, img in enumerate(result.images):
            print(f"    Image {idx+1}: {img.id if hasattr(img, 'id') else 'N/A'}")
    
    print()
    print("📝 Content preview:")
    print("-" * 80)
    print(result.content[:500])
    print("...")
    print("-" * 80)
    
    print("\n✅ Test completed! Run 'python3 view_newsletter_with_cover.py' to view the cover image.")


if __name__ == "__main__":
    asyncio.run(test_workflow())

