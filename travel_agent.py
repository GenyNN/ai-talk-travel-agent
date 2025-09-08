#!/usr/bin/env python3
"""
Advanced Travel Agent using the Game framework
This agent conducts a structured interview with users about their travel preferences
and includes error handling for invalid responses.
"""

import importlib
import os
from typing import List, Dict, Any
from dotenv import load_dotenv

# Import the Game framework
import game.core
importlib.reload(game.core)
from game.core import Environment, Goal, register_tool, PythonActionRegistry, Agent, \
    AgentFunctionCallingActionLanguage, generate_response

# Load environment variables from .env file
load_dotenv()

# Configure litellm for OpenRouter function calling
import litellm
litellm.set_verbose=True
# Note: add_function_to_prompt can cause issues with newer litellm versions
# litellm.add_function_to_prompt = True

# Global state to track current goal and user responses
agent_state = {
    "current_goal": 1,
    "user_responses": {},
    "error_count": 0,
    "max_errors": 3,
    "goal_completed": False,
    "conversation_active": True,
    "has_asked_goal_1": False
}

# Define the main goal for the travel agent - sequential execution
goals = [
    Goal(
        priority=1,
        name="Sequential Travel Planning",
        description="Execute travel planning goals sequentially: 1) Ask trip type, 2) Ask destination, 3) Ask group size, 4) Ask travel dates, 5) Ask departure city, 6) Generate summary. Handle errors gracefully."
    )
]

# Define the tools using decorators
@register_tool(tags=["sequential", "main"])
def execute_sequential_travel_planning() -> str:
    """Execute the travel planning process sequentially through all goals.
    
    This function manages the sequential execution of travel planning goals:
    1. Ask trip type
    2. Ask destination  
    3. Ask group size
    4. Ask travel dates
    5. Ask departure city
    6. Generate summary
    
    Returns:
        The appropriate question or response based on current goal
    """
    current_goal = agent_state["current_goal"]
    
    if current_goal == 1:
        return ask_trip_type()
    elif current_goal == 2:
        return ask_destination()
    elif current_goal == 3:
        return ask_group_size()
    elif current_goal == 4:
        return ask_travel_dates()
    elif current_goal == 5:
        return ask_departure_city()
    elif current_goal == 6:
        return generate_travel_summary()
    else:
        return "Travel planning session completed. Thank you!"

@register_tool(tags=["interview", "goal_1"])
def ask_trip_type() -> str:
    """Ask the user about the type of trip they are planning.
    
    Returns:
        A message asking about trip type with three options
    """
    return """Какую поездку вы планируете?

Выберите один из следующих вариантов:
1) Самостоятельная поездка — вы всё организуете сами
2) Организованный туризм — воспользуйтесь услугами туроператора (рекомендуется)
3) Деловая поездка

Укажите номер (1, 2 или 3) или полное название варианта."""

@register_tool(tags=["interview", "goal_2"])
def ask_destination() -> str:
    """Ask the user about their travel destination.
    
    Returns:
        A message asking about destination
    """
    return "Какую страну, город или курорт вы хотели бы посетить? Укажите конкретное место назначения."

@register_tool(tags=["interview", "goal_3"])
def ask_group_size() -> str:
    """Ask the user about the number of people traveling.
    
    Returns:
        A message asking about group size
    """
    return "Сколько человек планирует отправиться в эту поездку? Укажите, пожалуйста, количество путешественников."

@register_tool(tags=["interview", "goal_4"])
def ask_travel_dates() -> str:
    """Ask the user about their travel dates.
    
    Returns:
        A message asking about travel dates
    """
    return "На какие приблизительные даты вы планируете поездку? Укажите конкретные даты или диапазон дат."

@register_tool(tags=["interview", "goal_5"])
def ask_departure_city() -> str:
    """Ask the user about their departure city.
    
    Returns:
        A message asking about departure city
    """
    return "Из какого города или ближайшего крупного города вы планируете начать путешествие? Укажите, пожалуйста, город отправления."

@register_tool(tags=["summary", "goal_6"])
def generate_travel_summary() -> str:
    """Generate a summary of all collected travel information.
    
    Returns:
        A formatted summary of the user's travel preferences
    """
    responses = agent_state["user_responses"]
    
    summary = "Уважаемый турист, вы ввели следующую информацию:\n\n"
    
    # Add trip type information
    trip_type = responses.get("trip_type", "Not specified")
    if trip_type == "2" or "organized" in trip_type.lower():
        summary += "• Вы выбрали: Организованный туризм с использованием услуг туроператора\n"
    elif trip_type == "1" or "independent" in trip_type.lower():
        summary += "• Вы выбрали: Самостоятельная поездка \n"
    elif trip_type == "3" or "business" in trip_type.lower():
        summary += "• Вы выбрали: Командировка \n"
    else:
        summary += f"• Тип поездки: {trip_type}\n"
    
    # Add destination information
    destination = responses.get("destination", "Not specified")
    summary += f"• Место назначения: {destination}\n"
    
    # Add group size information
    group_size = responses.get("group_size", "Not specified")
    summary += f"• Количество человек:{group_size}\n"
    
    # Add travel dates information
    travel_dates = responses.get("travel_dates", "Not specified")
    summary += f"• Даты поездки:{travel_dates}\n"
    
    # Add departure city information
    departure_city = responses.get("departure_city", "Not specified")
    summary += f"• Город отправления: {departure_city}\n"
    
    summary += "\nЖелаю вам счастливого пути!"


    return summary

@register_tool(tags=["error_handling", "goal_7"])
def handle_user_error() -> str:
    """Handle user errors or invalid responses.
    
    Returns:
        A polite message asking for clarification
    """
    current_goal = agent_state["current_goal"]
    error_count = agent_state["error_count"]
    
    if error_count >= agent_state["max_errors"]:
        return "I apologize, but I'm having trouble understanding your responses. Please try again later or contact our support team for assistance. Thank you for your time!"
    
    goal_messages = {
        1: "trip type (1, 2, or 3)",
        2: "destination (country, city, or resort)",
        3: "number of people traveling",
        4: "travel dates",
        5: "departure city"
    }
    
    current_question = goal_messages.get(current_goal, "the current question")
    
    return f"""I apologize, but I didn't understand your response clearly. 

Could you please answer the question about {current_question}? 

If you're unsure or embarrassed to answer, please let me know when would be a good time to ask you again about this.

Please provide a clear answer so we can continue with your travel planning."""

@register_tool(tags=["system"], terminal=True)
def terminate(message: str = "Thank you for using our travel planning service!") -> str:
    """Terminates the agent's execution with a final message.
    
    Args:
        message: The final message to return before terminating
        
    Returns:
        The message with a termination note appended
    """
    return f"{message}\nTerminating..."

# Custom environment to handle state management
class TravelAgentEnvironment(Environment):
    def __init__(self):
        super().__init__()
        self.state = agent_state
    
    def execute_action(self, action, args: dict) -> dict:
        """Execute an action and return the result with state management."""
        try:
            result = action.execute(**args)
            
            # Update state based on action type
            if "sequential" in action.name or "main" in action.name:
                self._handle_sequential_response(result)
            elif "error" in action.name:
                self._handle_error_response(result)
            elif "terminate" in action.name:
                agent_state["conversation_active"] = False
                agent_state["goal_completed"] = True
            
            return self.format_result(result)
        except Exception as e:
            return {
                "tool_executed": False,
                "error": str(e),
                "traceback": str(e)
            }
    
    def _handle_sequential_response(self, result):
        """Handle response for sequential travel planning."""
        current_goal = agent_state["current_goal"]
        
        # Store the user's response based on current goal
        if current_goal == 1:
            agent_state["user_responses"]["trip_type"] = "User specified trip type"
        elif current_goal == 2:
            agent_state["user_responses"]["destination"] = "User specified destination"
        elif current_goal == 3:
            agent_state["user_responses"]["group_size"] = "User specified group size"
        elif current_goal == 4:
            agent_state["user_responses"]["travel_dates"] = "User specified dates"
        elif current_goal == 5:
            agent_state["user_responses"]["departure_city"] = "User specified departure city"
        elif current_goal == 6:
            # Summary generated, conversation complete
            agent_state["conversation_active"] = False
            agent_state["goal_completed"] = True
            return
        
        # Move to next goal
        agent_state["current_goal"] += 1
        agent_state["error_count"] = 0
    
    def _handle_error_response(self, result):
        """Handle error response."""
        agent_state["error_count"] += 1
        # Stay on current goal to retry

def create_travel_agent():
    """Create and configure the advanced travel agent"""
    
    # Reset global state
    global agent_state
    agent_state = {
        "current_goal": 1,
        "user_responses": {},
        "error_count": 0,
        "max_errors": 3
    }
    
    # Define the agent language and environment
    agent_language = AgentFunctionCallingActionLanguage()
    environment = TravelAgentEnvironment()
    
    # Create the agent with the specified goals and tools
    travel_agent = Agent(
        goals=goals,
        agent_language=AgentFunctionCallingActionLanguage(),
        # The ActionRegistry automatically loads tools with these tags
        action_registry=PythonActionRegistry(tags=["sequential", "main", "error_handling", "system"]),
        generate_response=generate_response,
        environment=environment
    )
    
    return travel_agent

def run_travel_agent_with_input(user_input: str):
    """Run the travel agent with provided input and return the memory"""
    
    # Create a simple memory to track the conversation
    from game.core import Memory
    memory = Memory()
    
    # Add the initial user input
    memory.add_memory({"type": "user", "content": user_input})
    
    # Execute the sequential travel planning based on current goal
    current_goal = agent_state["current_goal"]
    
    if current_goal == 1:
        response = ask_trip_type()
        # Mark that we've asked the first goal question so the next input is treated as an answer
        agent_state["has_asked_goal_1"] = True
    elif current_goal == 2:
        response = ask_destination()
    elif current_goal == 3:
        response = ask_group_size()
    elif current_goal == 4:
        response = ask_travel_dates()
    elif current_goal == 5:
        response = ask_departure_city()
    elif current_goal == 6:
        response = generate_travel_summary()
    else:
        response = "Travel planning session completed. Thank you!"
    
    memory.add_memory({"type": "assistant", "content": response})
    
    return memory

def process_user_response(user_response: str):
    """Process user response and advance to next goal"""
    
    # Store the user's response based on current goal
    current_goal = agent_state["current_goal"]
    
    if current_goal == 1:
        agent_state["user_responses"]["trip_type"] = user_response
    elif current_goal == 2:
        agent_state["user_responses"]["destination"] = user_response
    elif current_goal == 3:
        agent_state["user_responses"]["group_size"] = user_response
    elif current_goal == 4:
        agent_state["user_responses"]["travel_dates"] = user_response
    elif current_goal == 5:
        agent_state["user_responses"]["departure_city"] = user_response
    
    # Move to next goal
    agent_state["current_goal"] += 1
    agent_state["error_count"] = 0
    # Once we start processing answers, we no longer need the flag
    agent_state["has_asked_goal_1"] = True
    
    # Return the next question or summary
    return run_travel_agent_with_input("continue")

def run_travel_agent():
    """Run the travel agent and display the final memory (standalone version)"""
    
    print("🌍 Advanced Travel Agent - Comprehensive Travel Planning")
    print("=" * 60)
    print("Welcome! I'm here to help you plan your perfect trip.")
    print("I'll ask you a series of questions to understand your travel preferences.\n")
    
    # Get user input
    user_input = input("Let's start planning your trip! Please tell me what you're looking for: ")
    
    if not user_input.strip():
        user_input = "I want to plan a trip"
    
    print("\n🤖 Agent is processing your request...")
    
    # Run the agent
    final_memory = run_travel_agent_with_input(user_input)
    
    # Display the final memory
    print("\n" + "=" * 60)
    print("📝 AGENT MEMORY:")
    print("=" * 60)
    
    for item in final_memory.get_memories():
        print(f"\n{item['type'].upper()}: {item['content']}")
    
    print("\n" + "=" * 60)
    print("✅ Agent session completed!")

if __name__ == "__main__":
    run_travel_agent()