#!/usr/bin/env python3
"""
Test script for Telegram integration
This script tests the Telegram bot functionality without requiring the actual bot
"""

import os
import sys
import json
from dotenv import load_dotenv

# Add current directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Load environment variables
load_dotenv()

def test_imports():
    """Test if all required modules can be imported"""
    print("🧪 Testing imports...")
    
    try:
        from travel_agent import run_travel_agent_with_input, process_user_response, agent_state, reset_agent_state
        print("✅ Travel agent imports successful")
    except ImportError as e:
        print(f"❌ Travel agent import failed: {e}")
        return False
    
    try:
        # Test telebot import (might fail if not installed)
        import telebot
        from telebot import types
        print("✅ Telebot imports successful")
    except ImportError as e:
        print(f"⚠️  Telebot import failed (expected if not installed): {e}")
        print("   Run: pip install pyTelegramBotAPI")
    
    return True

def test_travel_agent_functions():
    """Test travel agent functions"""
    print("\n🧪 Testing travel agent functions...")
    
    try:
        from travel_agent import run_travel_agent_with_input, process_user_response, agent_state, reset_agent_state
        
        # Test reset function
        reset_agent_state()
        print("✅ Agent state reset successful")
        
        # Test initial conversation
        memory = run_travel_agent_with_input("хочу спланировать поездку")
        print("✅ Initial conversation successful")
        
        # Test response processing
        memory = process_user_response("2")
        print("✅ Response processing successful")
        
        return True
        
    except Exception as e:
        print(f"❌ Travel agent test failed: {e}")
        return False

def test_api_endpoints():
    """Test API endpoint structure"""
    print("\n🧪 Testing API endpoint structure...")
    
    try:
        from main import app
        print("✅ FastAPI app import successful")
        
        # Check if endpoints exist
        routes = [route.path for route in app.routes]
        required_endpoints = [
            "/telegram/webhook",
            "/telegram/set-webhook", 
            "/telegram/bot-info",
            "/travel-agent",
            "/chat"
        ]
        
        for endpoint in required_endpoints:
            if endpoint in routes:
                print(f"✅ Endpoint {endpoint} found")
            else:
                print(f"❌ Endpoint {endpoint} missing")
                return False
        
        return True
        
    except Exception as e:
        print(f"❌ API endpoint test failed: {e}")
        return False

def test_environment_config():
    """Test environment configuration"""
    print("\n🧪 Testing environment configuration...")
    
    # Check required environment variables
    required_vars = ["TELEGRAM_BOT_TOKEN"]
    optional_vars = ["PERPLEXITY_API_KEY", "OPENROUTER_API_KEY"]
    
    for var in required_vars:
        if os.getenv(var):
            print(f"✅ {var} is set")
        else:
            print(f"❌ {var} is missing")
            return False
    
    for var in optional_vars:
        if os.getenv(var):
            print(f"✅ {var} is set")
        else:
            print(f"⚠️  {var} is not set (optional)")
    
    return True

def test_webhook_structure():
    """Test webhook data structure"""
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
            "text": "test message"
        }
    }
    
    try:
        # Test JSON serialization
        json_data = json.dumps(sample_webhook)
        parsed_data = json.loads(json_data)
        print("✅ Webhook data structure is valid")
        return True
    except Exception as e:
        print(f"❌ Webhook data structure test failed: {e}")
        return False

def main():
    """Run all tests"""
    print("🤖 Telegram Integration Test Suite")
    print("=" * 50)
    
    tests = [
        test_imports,
        test_travel_agent_functions,
        test_api_endpoints,
        test_environment_config,
        test_webhook_structure
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
        print("🎉 All tests passed! Telegram integration is ready.")
        print("\nNext steps:")
        print("1. Install dependencies: pip install -r requirements.txt")
        print("2. Start server: python main.py")
        print("3. Set up webhook: python setup_telegram.py")
    else:
        print("⚠️  Some tests failed. Please check the errors above.")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
