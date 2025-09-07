#!/usr/bin/env python3
"""
Travel Agent using the Game framework
This agent interviews users about their trip purpose and then terminates.
"""

import importlib
import os
from typing import List
from dotenv import load_dotenv

# Import the Game framework
import game.core
importlib.reload(game.core)
from game.core import Environment, Goal, register_tool, PythonActionRegistry, Agent, \
    AgentFunctionCallingActionLanguage, generate_response

# Load environment variables from .env file
load_dotenv()
#litellm._turn_on_debug()

# Configure litellm for OpenRouter function calling
import litellm
litellm.add_function_to_prompt = True

# Define clear goals for the travel agent
goals = [
    Goal(
        priority=1,
        name="Interview User",
        description="Ask the user about the purpose of their trip and understand their travel needs"
    ),
    Goal(
        priority=2,
        name="Terminate",
        description="Terminate the session after gathering the user's trip information"
    )
]

# Define the tools using decorators
@register_tool(tags=["interview", "user_interaction"])
def ask_purpose_of_trip() -> str:
    """Asks the user about the purpose of their trip and acknowledges their response.
    
    This tool prompts the user to share their travel purpose and then responds
    that the agent understands and will look up information on the Internet.
    
    Returns:
        A message acknowledging the user's trip purpose and indicating that
        information will be researched online
    """
    return "I understand you. For your request I will look information on the Internet."

@register_tool(tags=["system"], terminal=True)
def terminate(message: str = "Thank you for sharing your travel purpose!") -> str:
    """Terminates the agent's execution with a final message.
    
    Args:
        message: The final message to return before terminating
        
    Returns:
        The message with a termination note appended
    """
    return f"{message}\nTerminating..."

def create_travel_agent():
    """Create and configure the travel agent"""
    
    # Define the agent language and environment
    agent_language = AgentFunctionCallingActionLanguage()
    environment = Environment()
    
    # Create the agent with the specified goals and tools
    travel_agent = Agent(
        goals=goals,
        agent_language=AgentFunctionCallingActionLanguage(),
        # The ActionRegistry automatically loads tools with these tags
        action_registry=PythonActionRegistry(tags=["interview", "user_interaction", "system"]),
        generate_response=generate_response,
        environment=Environment()
    )
    
    return travel_agent

def run_travel_agent_with_input(user_input: str):
    """Run the travel agent with provided input and return the memory"""
    
    # Create the agent
    agent = create_travel_agent()
    
    # Run the agent
    final_memory = agent.run(user_input, max_iterations=10)
    
    return final_memory

def run_travel_agent():
    """Run the travel agent and display the final memory (standalone version)"""
    
    print("🌍 Travel Agent - Trip Purpose Interview")
    print("=" * 50)
    print("I'm here to help you with your travel planning!")
    print("Let me ask you about the purpose of your trip.\n")
    
    # Get user input
    user_input = input("What is the purpose of your trip? ")
    
    if not user_input.strip():
        user_input = "I want to plan a trip"
    
    print("\n🤖 Agent is processing your request...")
    
    # Run the agent
    final_memory = run_travel_agent_with_input(user_input)
    
    # Display the final memory
    print("\n" + "=" * 50)
    print("📝 AGENT MEMORY:")
    print("=" * 50)
    
    for item in final_memory.get_memories():
        print(f"\n{item['type'].upper()}: {item['content']}")
    
    print("\n" + "=" * 50)
    print("✅ Agent session completed!")

if __name__ == "__main__":
    run_travel_agent()
