#!/usr/bin/env python3
"""
Console client for the AI Talk Travel Agent
Provides an interactive interface to connect to the advanced travel agent
"""

import requests
import json
import sys
import time
from typing import Optional, Dict, Any

class AITalkClient:
    def __init__(self, base_url: str = "http://localhost:8001"):
        self.base_url = base_url
        self.session = requests.Session()
    
    def send_message(self, message: str, model: str = "openrouter/google/gemini-2.0-flash-exp:free", max_tokens: int = 1024) -> Optional[dict]:
        """
        Send a message to the AI agent and get response
        """
        try:
            payload = {
                "message": message
            }
            
            response = self.session.post(
                f"{self.base_url}/travel-agent",
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
    
    def run_travel_agent(self, message: str) -> Optional[dict]:
        """
        Run the travel agent with a message about trip purpose
        """
        try:
            payload = {
                "message": message
            }
            
            response = self.session.post(
                f"{self.base_url}/travel-agent",
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
    print("🤖 Привет! Я консультант Кумар-Аравинд-Шива. Я могу проконсультировать Вас, по поводу вашей поездки. Я знаю очень многое по путеществиям. Я брахман, трахман, шаман в 105-м поколении. Я знаю почти все, либо все, что могу найти в интернете. Задавайте ваши вопроса!")
    print("=" * 50)
    
    # Initialize client
    client = AITalkClient()
    
    # Check server health
    if not client.check_health():
        print("❌ Server is not available. Please start the server first:")
        print("   python main.py")
        sys.exit(1)
    
    #print("✅ Server is running and healthy!")
    print("\nДоступные режимы:")
    print("1. Обычный чат — просто напишите сообщение")
    print("2. Турагент — введите «путешествие», чтобы начать собеседование о цели поездки.")
    print("Чтобы остановить, введите «quit» или «exit».")
    print("-" * 50)
    
    while True:
        try:
            # Get user input
            user_input = input("\n💬 Вы: ").strip()
            
            # Check for exit commands
            if user_input.lower() in ['quit', 'exit', 'q']:
                print("👋 Пока!")
                break
            
            if not user_input:
                continue
            
            # Check for travel agent mode
            if user_input.lower() == 'Путешествие':
                print("\n🌍 Starting Travel Agent - Trip Purpose Interview")
                print("What is the purpose of your trip?")
                trip_purpose = input("Trip purpose: ").strip()
                
                if not trip_purpose:
                    trip_purpose = "I want to plan a trip"
                
                print("\n🤖 Travel Agent is processing your request...")
                result = client.run_travel_agent(trip_purpose)
                
                if result:
                    print(f"\n📝 Travel Agent Memory:")
                    print("=" * 50)
                    for item in result.get('memory', []):
                        print(f"\n{item['type'].upper()}: {item['content']}")
                    print("\n" + "=" * 50)
                    #print(f"Status: {result.get('status', 'unknown')}")
                else:
                    print("❌ Failed to get response from Travel Agent")
                continue
            
            # Regular chat mode
            print("🤔 Я думаю...")
            result = client.send_message(user_input)
            
            if result:
                print(f"\n📝 Travel Agent Memory:")
                print("=" * 50)
                for item in result.get('memory', []):
                    print(f"\n{item['type'].upper()}: {item['content']}")
                print("\n" + "=" * 50)
                #print(f"Status: {result.get('status', 'unknown')}")
            else:
                print("❌ Failed to get response from AI")
                
        except KeyboardInterrupt:
            print("\n\n👋 Goodbye!")
            break
        except Exception as e:
            print(f"❌ Error: {str(e)}")

if __name__ == "__main__":
    main()
