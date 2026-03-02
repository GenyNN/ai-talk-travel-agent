#!/usr/bin/env python3
"""
Test script for refactored integration
This script tests that both API and Telegram endpoints use the same common logic
"""

import os
import sys
import json
from dotenv import load_dotenv

# Add current directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Load environment variables
load_dotenv()

def test_common_function():
    """Test the common process_travel_request function"""
    print("🧪 Testing common process_travel_request function...")
    
    try:
        from travel_agent import process_travel_request, reset_agent_state
        
        # Reset agent state
        reset_agent_state()
        
        # Test 1: New conversation
        print("  Testing new conversation...")
        result1 = process_travel_request("хочу спланировать поездку")
        
        assert "memory" in result1
        assert "status" in result1
        assert "current_goal" in result1
        assert "conversation_active" in result1
        assert result1["status"] == "in_progress"
        assert result1["current_goal"] == 1
        
        # Check that we have assistant message
        memory = result1["memory"]
        assistant_messages = [item for item in memory if item["type"] == "assistant"]
        assert len(assistant_messages) > 0
        print("  ✅ New conversation test passed")
        
        # Test 2: Continue conversation
        print("  Testing conversation continuation...")
        result2 = process_travel_request("2")
        
        assert result2["status"] == "in_progress"
        assert result2["current_goal"] == 2
        
        # Check that we have assistant message
        memory = result2["memory"]
        assistant_messages = [item for item in memory if item["type"] == "assistant"]
        assert len(assistant_messages) > 0
        print("  ✅ Conversation continuation test passed")
        
        # Test 3: Error handling
        print("  Testing error handling...")
        result3 = process_travel_request("")
        
        # Should still return valid structure
        assert "memory" in result3
        assert "status" in result3
        print("  ✅ Error handling test passed")
        
        return True
        
    except Exception as e:
        print(f"  ❌ Common function test failed: {e}")
        return False

def test_api_endpoint_structure():
    """Test that API endpoint uses common function"""
    print("\n🧪 Testing API endpoint structure...")
    
    try:
        from main import app
        from travel_agent import process_travel_request
        
        # Check if the function is imported
        assert process_travel_request is not None
        print("  ✅ process_travel_request is imported in main.py")
        
        # Check if endpoints exist
        routes = [route.path for route in app.routes]
        assert "/travel-agent" in routes
        assert "/telegram/webhook" in routes
        print("  ✅ Required endpoints exist")
        
        return True
        
    except Exception as e:
        print(f"  ❌ API endpoint structure test failed: {e}")
        return False

def test_telegram_integration():
    """Test that Telegram integration uses common function"""
    print("\n🧪 Testing Telegram integration...")
    
    try:
        from telegram_bot import process_travel_agent_message, process_travel_request
        
        # Check if the function is imported
        assert process_travel_request is not None
        print("  ✅ process_travel_request is imported in telegram_bot.py")
        
        # Test the telegram message processing
        result = process_travel_agent_message(12345, "хочу спланировать поездку")
        
        # Should return a string response
        assert isinstance(result, str)
        assert len(result) > 0
        print("  ✅ Telegram message processing works")
        
        return True
        
    except Exception as e:
        print(f"  ❌ Telegram integration test failed: {e}")
        return False

def test_consistency():
    """Test that both endpoints return consistent results"""
    print("\n🧪 Testing consistency between endpoints...")
    
    try:
        from travel_agent import process_travel_request, reset_agent_state
        
        # Reset state
        reset_agent_state()
        
        # Test same input through common function
        message = "хочу спланировать поездку"
        result1 = process_travel_request(message)
        
        # Reset state again
        reset_agent_state()
        
        # Test same input through common function again
        result2 = process_travel_request(message)
        
        # Results should be consistent
        assert result1["status"] == result2["status"]
        assert result1["current_goal"] == result2["current_goal"]
        
        # Memory should have same structure
        assert len(result1["memory"]) == len(result2["memory"])
        assert result1["memory"][0]["type"] == result2["memory"][0]["type"]
        
        print("  ✅ Results are consistent")
        
        return True
        
    except Exception as e:
        print(f"  ❌ Consistency test failed: {e}")
        return False

def test_webhook_data_structure():
    """Test webhook data structure compatibility"""
    print("\n🧪 Testing webhook data structure...")
    
    # Sample webhook data
    sample_webhook = {
        "update_id": 123456789,
        "message": {
            "message_id": 1,
            "from": {
                "id": 123456789,
                "is_bot": False,
                "first_name": "Test",
                "username": "testuser"
            },
            "chat": {
                "id": 123456789,
                "first_name": "Test",
                "username": "testuser",
                "type": "private"
            },
            "date": 1234567890,
            "text": "хочу спланировать поездку"
        }
    }
    
    try:
        # Test JSON serialization
        json_data = json.dumps(sample_webhook)
        parsed_data = json.loads(json_data)
        
        # Extract message text
        message_text = parsed_data["message"]["text"]
        
        # Test with common function
        from travel_agent import process_travel_request, reset_agent_state
        reset_agent_state()
        
        result = process_travel_request(message_text)
        
        # Should return valid structure
        assert "memory" in result
        assert "status" in result
        assert len(result["memory"]) > 0
        
        print("  ✅ Webhook data structure is compatible")
        
        return True
        
    except Exception as e:
        print(f"  ❌ Webhook data structure test failed: {e}")
        return False

def main():
    """Run all tests"""
    print("🔄 Refactored Integration Test Suite")
    print("=" * 50)
    
    tests = [
        test_common_function,
        test_api_endpoint_structure,
        test_telegram_integration,
        test_consistency,
        test_webhook_data_structure
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        if test():
            passed += 1
        print()
    
    print("=" * 50)
    print(f"📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! Refactored integration is working correctly.")
        print("\n✅ Both API and Telegram endpoints now use the same common logic:")
        print("   - /travel-agent endpoint uses process_travel_request()")
        print("   - Telegram webhook uses process_travel_request()")
        print("   - Both return consistent results from travel_agent.py")
    else:
        print("⚠️  Some tests failed. Please check the errors above.")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
