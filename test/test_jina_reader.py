"""
Test script for JinaWebReader
"""
import os
from dotenv import load_dotenv
from readers import JinaWebReader

# Load environment variables
load_dotenv()

def test_jina_reader():
    """Test JinaWebReader with various URLs"""
    
    # Get API key
    api_key = os.getenv("JINA_API_KEY")
    if not api_key:
        print("❌ JINA_API_KEY not found in environment variables")
        print("   Get a free key at https://jina.ai/reader")
        return
    
    print(f"✅ Found JINA_API_KEY: {api_key[:10]}...")
    
    # Initialize reader
    reader = JinaWebReader(api_key=api_key)
    print("✅ Initialized JinaWebReader")
    
    # Test URLs
    test_urls = [
        "https://mksaas.com/zh/docs",  # User's example
        "https://mp.weixin.qq.com/s/RJhW2B3SUaclskyFc5QO7Q",  # WeChat (problematic)
        "https://example.com",  # Simple test
    ]
    
    for url in test_urls:
        print(f"\n{'='*60}")
        print(f"Testing URL: {url}")
        print('='*60)
        
        try:
            docs = reader.read(url)
            
            if docs:
                doc = docs[0]
                print(f"✅ Successfully read content")
                print(f"   Name: {doc.name}")
                print(f"   Content length: {len(doc.content)} characters")
                print(f"   First 200 chars: {doc.content[:200]}...")
                print(f"   Metadata: {doc.meta_data}")
            else:
                print(f"❌ No content returned")
        
        except Exception as e:
            print(f"❌ Error: {str(e)}")
    
    print(f"\n{'='*60}")
    print("Test completed!")
    print('='*60)

if __name__ == "__main__":
    test_jina_reader()

