#!/usr/bin/env python3
"""
Test script for mock AI functionality
"""

import asyncio
import sys
import os

# Add src to path and set PYTHONPATH
project_root = os.path.dirname(__file__)
src_path = os.path.join(project_root, 'src')
sys.path.insert(0, src_path)
os.environ['PYTHONPATH'] = src_path

from src.chat.llm_chatbot import RepairChatbot
from src.config.settings_simple import Settings


async def test_mock_chat():
    """Test mock chat functionality"""
    print("🧪 Testing Mock Chat Functionality")
    print("=" * 50)
    
    # Initialize settings
    settings = Settings()
    print(f"Mock AI enabled: {settings.should_use_mock_ai()}")
    
    # Initialize chatbot with mock mode
    chatbot = RepairChatbot(use_mock=True)
    print(f"Active client: {chatbot.active_client}")
    
    # Test cases
    test_cases = [
        {
            "message": "My Joy-Con is drifting",
            "device_type": "nintendo_switch",
            "description": "Joy-Con drift issue"
        },
        {
            "message": "My iPhone screen is cracked",
            "device_type": "iphone",
            "description": "iPhone screen crack"
        },
        {
            "message": "My phone battery drains quickly",
            "device_type": "smartphone",
            "description": "Battery drain issue"
        },
        {
            "message": "My laptop won't turn on",
            "device_type": "laptop",
            "description": "Generic hardware issue"
        }
    ]
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n🔸 Test {i}: {test_case['description']}")
        print("-" * 30)
        
        # Update context
        chatbot.update_context(
            device_type=test_case['device_type'],
            user_skill_level="beginner"
        )
        
        # Get response
        try:
            response = chatbot.chat(test_case['message'])
            print(f"✅ Response received ({len(response)} characters)")
            print(f"📝 Preview: {response[:150]}...")
            
            # Check for mock indicator
            if "Mock AI Response" in response:
                print("🤖 Mock response detected ✓")
            else:
                print("❌ Mock indicator not found")
                
        except Exception as e:
            print(f"❌ Error: {e}")
    
    print("\n" + "=" * 50)
    print("Mock chat testing completed!")


async def main():
    """Main test function"""
    print("🚀 RepairGPT Mock AI Test Suite")
    print("=" * 50)
    
    await test_mock_chat()


if __name__ == "__main__":
    asyncio.run(main())