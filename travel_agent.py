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

def reset_agent_state():
    """Reset the agent state for a new conversation"""
    global agent_state
    print(f"🔄 Resetting agent state for new conversation")
    # Clear the existing state
    agent_state.clear()
    # Set new values
    agent_state.update({
        "current_goal": 1,
        "user_responses": {},
        "error_count": 0,
        "max_errors": 3,
        "goal_completed": False,
        "conversation_active": True,
        "has_asked_goal_1": False
    })

# Define the main goal for the travel agent - sequential execution
goals = [
    Goal(
        priority=1,
        name="Sequential Travel Planning",
        description="Execute travel planning goals sequentially: 1) Ask trip type, 2) Ask destination, 3) Ask group size, 4) Ask travel dates, 5) Ask departure city, 6) Generate summary with Perplexity, 7) Collect user feedback, 8) Offer human agent connection. Handle errors gracefully."
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
    6. Generate summary with Perplexity
    7. Collect user feedback
    8. Offer human agent connection
    
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
    elif current_goal == 7:
        return ask_user_feedback()
    elif current_goal == 8:
        return offer_human_agent_connection()
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

def get_perplexity_recommendations(trip_type: str, destination: str, group_size: str, travel_dates: str, departure_city: str, history_dialogue: str = "") -> str:
    """Get travel recommendations from Perplexity API.
    
    Args:
        trip_type: Type of trip (organized/independent/business)
        destination: Travel destination
        group_size: Number of travelers
        travel_dates: Travel dates
        departure_city: Departure city
        history_dialogue: History of clarifying questions and answers
        
    Returns:
        Formatted recommendations from Perplexity
    """
    import requests
    import os
    
    # Get API key from environment
    api_key = os.getenv("PERPLEXITY_API_KEY")
    if not api_key:
        # Fallback to hardcoded key for testing (remove in production)
        api_key = "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"
        if not api_key:
            # Debug information
            all_env_vars = {k: v for k, v in os.environ.items() if 'PERPLEXITY' in k or 'API' in k}
            debug_info = f"Доступные переменные окружения: {list(all_env_vars.keys())}"
            return f"❌ API ключ не найден. Пожалуйста, проверьте настройки.\n{debug_info}"
    
    # Construct the prompt according to requirements
    prompt = f"""
    Ты опытный турагент. Проанализируй переписку и дай краткий максимально человечный ответ и в конце Задавай ТОЛЬКО ОДИН вопрос для следующей диалога. Вопрос должен идти в самом конце ответа и самом последнем абзаце.
Вопрос в конце должен раскрывать потребность человека и при этом чтобы каждый следующий вопрос приближал его к переадресации на живого турагента и тем самым покупке тура у агента.

ПРАВИЛА:
1. НИКОГДА не называй цены, отели, рейсы.
2. НИКОГДА не давай конкретных рекомендаций, не навязывай свое мнение, но при этом твои советы должны раскрывать  место куда человек хочет поехать. Возможно чтобы человек посмотрел на это место с другой стороны. Возможно если что то в этом предложенном варианте плохо, то предложить другой вариант места в этой стране или даже другую страну. 
3. Задавай ВОПРОСЫ для уточнения потребностей.
4. Если просят конкретику — предлагай созвон с живым турагентом.
5. Говори как живой человек, естественно

Запрос для Perplexity следующим критериям:

Критерий 1 - Тип поездки: {trip_type}
Критерий 2 — Пункт назначения: {destination}
Критерий 3 - Количество человек: {group_size}
Критерий 4 — Даты поездки: {travel_dates}
Критерий 5 - Город отправления: {departure_city}
Критерий 6 - История уточняющих вопросов и ответов: {history_dialogue}
    """

    try:
        # Make request to Perplexity API using the cheapest model
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        
        data = {
            "model": "sonar",  # Valid model with web search capabilities
            "messages": [
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            "max_tokens": 2000,
            "temperature": 0.2
        }
        
        response = requests.post(
            "https://api.perplexity.ai/chat/completions",
            headers=headers,
            json=data,
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            content = result["choices"][0]["message"]["content"]
            
            # Format the response nicely
            formatted_response = "\n\n" #"🎯 РЕКОМЕНДАЦИИ ОТ ПРОФЕССИОНАЛЬНОГО ТУРАГЕНТА:\n\n"
            formatted_response += content
            #formatted_response += "\n\n📋 Источник: Perplexity AI с веб-поиском"
            
            return formatted_response
        else:
            return f"❌ Ошибка API: {response.status_code} - {response.text}"
            
    except requests.exceptions.Timeout:
        return "❌ Превышено время ожидания ответа от API. Попробуйте позже."
    except requests.exceptions.RequestException as e:
        return f"❌ Ошибка соединения с API: {str(e)}"
    except Exception as e:
        return f"❌ Неожиданная ошибка: {str(e)}"

@register_tool(tags=["summary", "goal_6"])
def generate_travel_summary() -> str:
    """Generate a comprehensive travel summary with Perplexity recommendations.
    
    Returns:
        A formatted summary with travel recommendations from Perplexity
    """
    responses = agent_state["user_responses"]
    
    # Basic summary
    summary = "\n\n"
    #--summary = "Уважаемый турист, вы ввели следующую информацию:\n\n"


    # Add trip type information
    trip_type = responses.get("trip_type", "Not specified")
    trip_type_display = ""
    if trip_type == "2" or "organized" in trip_type.lower():
        trip_type_display = "Организованный туризм с использованием услуг туроператора"
        #--summary += "• Вы выбрали: Организованный туризм с использованием услуг туроператора\n"
    elif trip_type == "1" or "independent" in trip_type.lower():
        trip_type_display = "Самостоятельная поездка"
        #--summary += "• Вы выбрали: Самостоятельная поездка\n"
    elif trip_type == "3" or "business" in trip_type.lower():
        trip_type_display = "Командировка"
        #--summary += "• Вы выбрали: Командировка\n"
    else:
        trip_type_display = trip_type
        #--summary += f"• Тип поездки: {trip_type}\n"


    # Add destination information
    destination = responses.get("destination", "Not specified")
    #--summary += f"• Место назначения: {destination}\n"

    # Add group size information
    group_size = responses.get("group_size", "Not specified")
    #--ummary += f"• Количество человек: {group_size}\n"

    # Add travel dates information
    travel_dates = responses.get("travel_dates", "Not specified")
    #--summary += f"• Даты поездки: {travel_dates}\n"

    # Add departure city information
    departure_city = responses.get("departure_city", "Not specified")
    #--summary += f"• Город отправления: {departure_city}\n"


    
    #summary += "\n" + "="*62 + "\n"
    #summary += "🔍 ИЩЕМ, ДУМАЕМ, ЛОВИМ СЛОТЫ...\n"
    #summary += "="*62 + "\n\n"
    
    # Собираем все записи из dialogue_history в одну строку через перенос строки
    dialogue_history = agent_state["user_responses"].get("dialogue_history", [])
    history_dialogue = "\n".join(dialogue_history) if dialogue_history else ""
    
    # Get Perplexity recommendations
    try:
        perplexity_response = get_perplexity_recommendations(
            trip_type_display, destination, group_size, travel_dates, departure_city, history_dialogue
        )
        summary += perplexity_response
    except Exception as e:
        summary += f"❌ Ошибка при получении рекомендаций: {str(e)}\n"
        summary += "Пожалуйста, попробуйте позже или обратитесь в службу поддержки.\n"
    
    #summary += "\n" + "="*62 + "\n"
    return summary

def analyze_feedback_sentiment(user_feedback: str) -> str:
    """Analyze user feedback to determine if it's positive or negative.
    
    Args:
        user_feedback: User's feedback text
        
    Returns:
        'positive', 'negative', or 'neutral'
    """
    feedback_lower = user_feedback.lower()
    
    # Positive sentiment indicators
    positive_words = [
        "хорошо", "здорово", "супер", "круто", "нравится", "отлично", 
        "прекрасно", "замечательно", "великолепно", "потрясающе", 
        "спасибо", "благодарю", "понравилось", "подходит", "устраивает",
        "да", "согласен", "принимаю", "беру"
    ]
    
    # Negative sentiment indicators
    negative_words = [
        "не очень", "не нравится", "говно", "лажа", "плохо", "ужасно",
        "не подходит", "не устраивает", "не то", "неправильно", 
        "неверно", "неточно", "неактуально", "не подходит", "не подходит",
        "не", "нет", "отказываюсь", "не хочу", "не буду"
    ]
    
    # Check for positive sentiment
    positive_count = sum(1 for word in positive_words if word in feedback_lower)
    
    # Check for negative sentiment
    negative_count = sum(1 for word in negative_words if word in feedback_lower)
    
    if positive_count > negative_count:
        return "positive"
    elif negative_count > positive_count:
        return "negative"
    else:
        return "neutral"

@register_tool(tags=["feedback", "goal_7"])
def ask_user_feedback() -> str:
    """Ask the user for feedback on the travel recommendations from goal #6.
    
    Returns:
        A message asking for user feedback on the recommendations
    """
    return """Спасибо за предоставленную информацию! 

Мы подготовим для вас подробные рекомендации по путешествию на основе ваших предпочтений.

Пожалуйста, оцените, насколько вам понравились предложенные рекомендации:

• Если вам понравилось - напишите что-то вроде "хорошо", "здорово", "супер", "круто", "нравится"
• Если что-то не понравилось - напишите "не очень", "не нравится" или укажите конкретные проблемы

Ваша обратная связь поможет нам улучшить сервис!"""

@register_tool(tags=["feedback_analysis", "goal_7_negative"])
def analyze_negative_feedback() -> str:
    """Analyze negative feedback and ask for specific issues.
    
    Returns:
        A message asking for specific feedback about what didn't work
    """
    return """Понимаю, что рекомендации не полностью соответствуют вашим ожиданиям.

Помогите нам улучшить сервис! Расскажите подробнее:

• Что именно вам не понравилось в рекомендациях?
• Какая информация была неточной или неактуальной?
• Что бы вы хотели изменить или добавить?
• Есть ли конкретные требования, которые мы не учли?

Ваши комментарии помогут нам сделать сервис лучше для будущих пользователей."""

@register_tool(tags=["connection", "goal_8"])
def offer_human_agent_connection() -> str:
    """Offer connection with a human travel agent for further assistance.
    
    Returns:
        A message offering to connect with a human travel agent
    """
    return """Отлично! Рад, что рекомендации вам понравились! 🎉

Если у вас есть дополнительные вопросы или вы хотите получить более персонализированную помощь, я могу связать вас с нашим живым турагентом.

Наш специалист поможет вам:
• Уточнить детали поездки
• Забронировать отели и билеты
• Ответить на любые вопросы о путешествии
• Предоставить персональные рекомендации

Хотите ли вы связаться с нашим турагентом? Напишите "да" или "нет".

Спасибо за использование нашего сервиса! ✈️"""

@register_tool(tags=["error_handling", "goal_9"])
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
        if not agent_state["user_responses"].get("travel_dates"):
            agent_state["current_goal"] = 4
            response = ask_travel_dates()
        else:
            response = generate_travel_summary()
            # Сохраняем последний ответ агента для использования в уточняющем цикле
            agent_state["last_agent_response"] = response
    elif current_goal == 7:
        response = ask_user_feedback()
    elif current_goal == 8:
        response = offer_human_agent_connection()
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
        # Переход на следующую цель после успешного ответа
        agent_state["current_goal"] = 2
    elif current_goal == 2:
        agent_state["user_responses"]["destination"] = user_response
        # Переход на следующую цель после успешного ответа
        agent_state["current_goal"] = 3
    elif current_goal == 3:
        agent_state["user_responses"]["group_size"] = user_response
        # Переход на следующую цель после успешного ответа
        agent_state["current_goal"] = 4
    elif current_goal == 4:
        agent_state["user_responses"]["travel_dates"] = user_response
        # Переход на следующую цель после успешного ответа
        agent_state["current_goal"] = 5
    elif current_goal == 5:
        agent_state["user_responses"]["departure_city"] = user_response
        # Переход на следующую цель после успешного ответа
        agent_state["current_goal"] = 6
    elif current_goal == 7:
        # Handle feedback analysis
        agent_state["user_responses"]["feedback"] = user_response
        sentiment = analyze_feedback_sentiment(user_response)
        
        if sentiment == "negative":
            # Stay on goal 7 but show negative feedback analysis
            agent_state["current_goal"] = 7  # Stay on current goal
            agent_state["error_count"] = 0
            agent_state["has_asked_goal_1"] = True
            
            # Create memory with negative feedback response
            from game.core import Memory
            memory = Memory()
            memory.add_memory({"type": "user", "content": user_response})
            memory.add_memory({"type": "assistant", "content": analyze_negative_feedback()})
            return memory
        elif sentiment == "positive":
            # Move to goal 8 (human agent connection)
            agent_state["current_goal"] = 8
        else:
            # Neutral feedback - ask for clarification
            agent_state["current_goal"] = 7  # Stay on current goal
            agent_state["error_count"] = 0
            agent_state["has_asked_goal_1"] = True
            
            # Create memory with clarification request
            from game.core import Memory
            memory = Memory()
            memory.add_memory({"type": "user", "content": user_response})
            memory.add_memory({"type": "assistant", "content": "Пожалуйста, уточните ваше мнение. Вам понравились рекомендации или есть что-то, что нужно улучшить?"})
            return memory
    elif current_goal == 8:
        # Handle human agent connection response
        agent_state["user_responses"]["human_agent_request"] = user_response
        # End the conversation
        agent_state["conversation_active"] = False
        agent_state["goal_completed"] = True
        
        # Create final memory
        from game.core import Memory
        memory = Memory()
        memory.add_memory({"type": "user", "content": user_response})
        
        if "да" in user_response.lower() or "yes" in user_response.lower():
            final_response = "Отлично! Наш турагент свяжется с вами в ближайшее время. Спасибо за использование нашего сервиса! ✈️"
        else:
            final_response = "Спасибо за использование нашего сервиса! Если у вас возникнут вопросы, мы всегда готовы помочь. Удачного путешествия! 🎉"
        
        memory.add_memory({"type": "assistant", "content": final_response})
        return memory
    elif current_goal == 6:
        # Локализованный цикл на Goal 6
        ok_words = ["да", "ок", "хорошо", "подходит", "супер", "отлично", "устраивает"]
        if any(word in user_response.lower() for word in ok_words):
            # Если есть подтверждение, переходим на цель 7
            agent_state["current_goal"] = 7
        else:
            # Если пользователь НЕ ввел подтверждение, сохраняем историю диалога
            # Извлекаем текст последнего ответа агента из agent_state
            last_agent_question = agent_state.get("last_agent_response", "")
            
            # Инициализируем dialogue_history если его нет
            if "dialogue_history" not in agent_state["user_responses"]:
                agent_state["user_responses"]["dialogue_history"] = []
            
            # Сохраняем новую запись в dialogue_history
            dialogue_entry = f"Вопрос: {last_agent_question} | Ответ: {user_response}"
            agent_state["user_responses"]["dialogue_history"].append(dialogue_entry)
            
            # Строго оставляем current_goal = 6 (не меняем ни на 7, ни на 1)
            agent_state["current_goal"] = 6

    # Return the next question or summary
    return run_travel_agent_with_input("continue")

def process_travel_request(message: str, user_id: str = None) -> Dict[str, Any]:
    """
    Common function to process travel requests for both API and Telegram.
    
    Args:
        message: User's message/input
        user_id: Optional user ID for session management (for Telegram)
        
    Returns:
        Dictionary with response data including memory and status
    """
    try:
        # Проверяем состояние разговора
        conversation_active = agent_state.get("conversation_active", True)
        goal_completed = agent_state.get("goal_completed", False)
        current_goal = agent_state.get("current_goal", 1)
        
        # НЕ сбрасываем состояние, если разговор активен и мы находимся на цели > 1
        # Это гарантирует, что обычные ответы пользователя не будут распознаны как новый разговор
        if conversation_active and current_goal > 1:
            # Продолжаем активный разговор без сброса
            pass
        elif goal_completed or not conversation_active:
            # Сбрасываем только если разговор завершен или не активен
            reset_agent_state()
        else:
            # Для цели 1 проверяем, является ли это явным запросом на новый разговор
            # Ключевые слова должны быть в начале сообщения
            message_lower = message.lower().strip()
            new_conversation_keywords = ["travel", "поездка", "путешествие", "начать", "новый", "снова", "привет"]
            is_new_conversation = any(message_lower.startswith(keyword) for keyword in new_conversation_keywords)
            
            if is_new_conversation and not agent_state.get("has_asked_goal_1", False):
                reset_agent_state()
        
        # Check if this is a continuation of an existing conversation
        if agent_state["current_goal"] > 1 or (agent_state["current_goal"] == 1 and agent_state.get("has_asked_goal_1", False)):
            # Process user response and advance to next goal
            final_memory = process_user_response(message)
        else:
            # Start new conversation
            final_memory = run_travel_agent_with_input(message)

        # Convert memory to list format for JSON response
        memory_list = []
        for item in final_memory.get_memories():
            memory_list.append({
                "type": item["type"],
                "content": item["content"]
            })

        # Determine status based on current goal
        if agent_state["current_goal"] > 8 or agent_state.get("goal_completed", False):
            status = "completed"
        else:
            status = "in_progress"
        
        return {
            "memory": memory_list,
            "status": status,
            "current_goal": agent_state["current_goal"],
            "conversation_active": agent_state.get("conversation_active", True)
        }
        
    except Exception as e:
        return {
            "memory": [{"type": "error", "content": f"Error processing request: {str(e)}"}],
            "status": "error",
            "current_goal": agent_state.get("current_goal", 1),
            "conversation_active": False
        }

def run_travel_agent():
    """Run the travel agent and display the final memory (standalone version)"""
    
    print("🌍 Advanced Travel Agent - Comprehensive Travel Planning")
    print("=" * 62)
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
    print("\n" + "=" * 62)
    print("📝 AGENT MEMORY:")
    print("=" * 62)
    
    for item in final_memory.get_memories():
        print(f"\n{item['type'].upper()}: {item['content']}")
    
    print("\n" + "=" * 62)
    print("✅ Agent session completed!")

if __name__ == "__main__":
    run_travel_agent()
