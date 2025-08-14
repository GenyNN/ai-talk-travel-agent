#!/usr/bin/env python3
"""
Console client for the AI Talk Travel Agent
Provides a simple interface to send messages to the neural network
"""

import requests
import json
import sys
from typing import Optional

class AITalkClient:
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.session = requests.Session()
    
    def send_message(self, message: str, model: str = "openai/gpt-4o", max_tokens: int = 1024) -> Optional[dict]:
        """
        Send a message to the AI agent and get response
        """
        try:
            payload = {
                "message": message,
                "model": model,
                "max_tokens": max_tokens
            }
            
            response = self.session.post(
                f"{self.base_url}/chat",
                json=payload,
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                print(f"Error: {response.status_code} - {response.text}")
                return None
                
        except requests.exceptions.ConnectionError:
            print(f"Error: Could not connect to server at {self.base_url}")
            print("Make sure the FastAPI server is running with: python main.py")
            return None
        except Exception as e:
            print(f"Error: {str(e)}")
            return None
    
    def check_health(self) -> bool:
        """
        Check if the server is healthy
        """
        try:
            response = self.session.get(f"{self.base_url}/health")
            return response.status_code == 200
        except:
            return False

def main():
    """
    Main console interface
    """
    print("🤖 AI Talk Travel Agent - Console Interface")
    print("=" * 50)
    
    # Initialize client
    client = AITalkClient()
    
    # Check server health
    if not client.check_health():
        print("❌ Server is not available. Please start the server first:")
        print("   python main.py")
        sys.exit(1)
    
    print("✅ Server is running and healthy!")
    print("\nType your messages below. Type 'quit' or 'exit' to stop.")
    print("-" * 50)
    
    while True:
        try:
            # Get user input
            user_input = input("\n💬 You: ").strip()
            
            # Check for exit commands
            if user_input.lower() in ['quit', 'exit', 'q']:
                print("👋 Goodbye!")
                break
            
            if not user_input:
                continue
            
            # Send message to AI
            print("🤔 AI is thinking...")
            result = client.send_message(user_input)
            
            if result:
                print(f"\n🤖 AI ({result.get('model_used', 'unknown')}):")
                print(result.get('response', 'No response received'))
                
                if result.get('tokens_used'):
                    print(f"\n📊 Tokens used: {result['tokens_used']}")
            else:
                print("❌ Failed to get response from AI")
                
        except KeyboardInterrupt:
            print("\n\n👋 Goodbye!")
            break
        except Exception as e:
            print(f"❌ Error: {str(e)}")

if __name__ == "__main__":
    main()
