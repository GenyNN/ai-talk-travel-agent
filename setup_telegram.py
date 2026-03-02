#!/usr/bin/env python3
"""
Telegram Bot Setup Script
This script helps set up the Telegram bot webhook and test the integration
"""

import os
import requests
import json
from dotenv import load_dotenv
from telegram_bot import get_bot_info, set_webhook

# Load environment variables
load_dotenv()

def get_webhook_url():
    """Get webhook URL from environment or prompt user"""
    webhook_url = os.getenv("WEBHOOK_URL")
    
    if not webhook_url:
        print("Please set WEBHOOK_URL in your .env file or provide it now:")
        webhook_url = input("Enter your webhook URL (e.g., https://yourdomain.com/telegram/webhook): ")
    
    return webhook_url

def test_bot_connection():
    """Test bot connection and get info"""
    print("🔍 Testing bot connection...")
    
    bot_info = get_bot_info()
    if bot_info:
        print("✅ Bot connection successful!")
        print(f"Bot ID: {bot_info['id']}")
        print(f"Bot Username: @{bot_info['username']}")
        print(f"Bot Name: {bot_info['first_name']}")
        return True
    else:
        print("❌ Bot connection failed!")
        return False

def setup_webhook():
    """Set up webhook for the bot"""
    print("🔗 Setting up webhook...")
    
    webhook_url = get_webhook_url()
    if not webhook_url:
        print("❌ No webhook URL provided!")
        return False
    
    success = set_webhook(webhook_url)
    if success:
        print(f"✅ Webhook set successfully: {webhook_url}")
        return True
    else:
        print("❌ Failed to set webhook!")
        return False

def test_webhook():
    """Test webhook by sending a test update"""
    print("🧪 Testing webhook...")
    
    webhook_url = get_webhook_url()
    if not webhook_url:
        print("❌ No webhook URL provided!")
        return False
    
    # Create a test update
    test_update = {
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
            "text": "test"
        }
    }
    
    try:
        response = requests.post(webhook_url, json=test_update, timeout=10)
        if response.status_code == 200:
            print("✅ Webhook test successful!")
            return True
        else:
            print(f"❌ Webhook test failed: {response.status_code} - {response.text}")
            return False
    except Exception as e:
        print(f"❌ Webhook test error: {str(e)}")
        return False

def main():
    """Main setup function"""
    print("🤖 Telegram Bot Setup for AI Travel Agent")
    print("=" * 50)
    
    # Check if .env file exists
    if not os.path.exists(".env"):
        print("⚠️  .env file not found. Please copy env.example to .env and configure it.")
        return
    
    # Test bot connection
    if not test_bot_connection():
        print("❌ Setup failed: Cannot connect to bot")
        return
    
    # Set up webhook
    if not setup_webhook():
        print("❌ Setup failed: Cannot set webhook")
        return
    
    # Test webhook
    if not test_webhook():
        print("⚠️  Webhook setup completed but test failed. Check your server.")
        return
    
    print("\n🎉 Setup completed successfully!")
    print("\nNext steps:")
    print("1. Start your server: python main.py")
    print("2. Test the bot by sending a message to @your_bot_username")
    print("3. Use /start command to begin travel planning")

if __name__ == "__main__":
    main()
