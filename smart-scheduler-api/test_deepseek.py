# Test DeepSeek API Connection

import asyncio
import sys
import os

# Add parent directory to path to import from chatbot module
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from chatbot.client import get_bot_response


async def test_deepseek():
    """Test basic DeepSeek API connection"""
    print("Testing DeepSeek API connection...")
    print("-" * 50)
    
    try:
        # Test simple question
        test_message = "Xin chào, bạn có thể giúp tôi không?"
        print(f"\nUser: {test_message}")
        
        response = await get_bot_response(test_message)
        print(f"\nBot: {response}")
        
        print("\n" + "-" * 50)
        print("✅ Test passed! DeepSeek API is working correctly.")
        return True
        
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        print("\nTroubleshooting:")
        print("1. Check your internet connection")
        print("2. Verify the API key is correct")
        print("3. Check DeepSeek API status")
        return False


if __name__ == "__main__":
    result = asyncio.run(test_deepseek())
    sys.exit(0 if result else 1)
