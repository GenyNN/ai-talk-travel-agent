#!/usr/bin/env python3
"""
Advanced Travel Agent using the Game framework
This agent conducts a structured interview with users about their travel preferences
and includes error handling for invalid responses.
"""

import importlib
import os
import json
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
#
agent_state = {
    "current_goal": 1,
    "user_responses": {},
    "error_count": 0,
    "max_errors": 3,
    "goal_completed": False,
    "conversation_active": True,
    "has_asked_goal_1": False,
    "dynamic_questions_count": 0,
    "dynamic_completed": False
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
        "has_asked_goal_1": False,
        "dynamic_questions_count": 0,
        "dynamic_completed": False
    })

# Define the main goal for the travel agent - sequential execution
goals = [
    Goal(
        priority=1,
        name="Sequential Travel Planning",
        description=(
            "Execute travel planning goals sequentially: "
            "1) Capture travel dates, 2) Ask group size, 3) Ask if children will travel, "
            "4) Ask children age (if applicable), 5) Ask destination preferences, "
            "6) Ask budget, 7) Ask departure city, 8) Run dynamic Perplexity clarification loop, "
            "9) Ask final catch-all question, 10) Terminate conversation. Handle errors gracefully."
        )
    )
]

@register_tool(tags=["sequential", "main"])
def execute_sequential_travel_planning() -> str:
    """Execute the travel planning process sequentially through all goals."""
    current_goal = agent_state["current_goal"]
    if current_goal == 2:
        return ask_group_size()
    elif current_goal == 3:
        return ask_children_exist()
    elif current_goal == 4:
        return ask_children_age()
    elif current_goal == 5:
        return ask_destination_preferences()
    elif current_goal == 6:
        return ask_budget()
    elif current_goal == 7:
        return ask_departure_city()
    elif current_goal == 9:
        return ask_final_catch_all()
    elif current_goal == 10:
        return terminate("Отлично! Все ваши вводные учтем максимально. Эксперт подготовит для вас подборку туров, и свяжется с вами")
    else:
        return "Travel planning session completed. Thank you!"


@register_tool(tags=["interview", "goal_2"])
def ask_group_size() -> str:
    """Ask who will travel and how many adults."""
    return "Хорошо. Кто поедет? Сколько взрослых?"


@register_tool(tags=["interview", "goal_3"])
def ask_children_exist() -> str:
    """Ask if children will travel."""
    return "Поедут ли дети? (Да/Нет)"


@register_tool(tags=["interview", "goal_4"])
def ask_children_age() -> str:
    """Ask about children's ages."""
    return "Уточните возраст детей?"


@register_tool(tags=["interview", "goal_5"])
def ask_destination_preferences() -> str:
    """Ask about destination preferences."""
    return "Есть ли пожелания по направлению/стране/городу назначения?"


@register_tool(tags=["interview", "goal_6"])
def ask_budget() -> str:
    """Ask about desired budget."""
    return "Хорошо. В какой общий бюджет хотели бы уложиться?"


@register_tool(tags=["interview", "goal_7"])
def ask_departure_city() -> str:
    """Ask about departure city."""
    return "Откуда планируете стартовать?"


@register_tool(tags=["interview", "goal_9"])
def ask_final_catch_all() -> str:
    """Ask final catch-all question before termination."""
    return (
        "Спасибо за Ваши ответы. Подскажите, какие еще моменты важно учесть "
        "при составлении подборки туров, которые ранее не обсудили?"
    )

def get_perplexity_recommendations(
    trip_type: str,
    destination: str,
    group_size: str,
    travel_dates: str,
    departure_city: str,
    budget: str,
    children_info: str,
    history_dialogue: str = "",
) -> str:
    """Get dynamic clarification question and short answer from Perplexity API."""
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
    
    # Construct the prompt according to new requirements
    prompt = f"""
    Ты опытный турагент. Проанализируй переписку и дай краткий максимально человечный ответ не более 11-12 слов и в конце Задавай ТОЛЬКО ОДИН вопрос для следующего диалога. Вопрос должен идти в самом конце ответа и самом последнем абзаце.
Вопрос в конце должен раскрывать потребность человека и при этом чтобы каждый следующий вопрос не повторял предыдущие, проверял на адекватность, квалифицировал как лида и двигал по маркетинговой воронке к покупке тура у агента.

ПРАВИЛА:
1. НИКОГДА не называй цены, отели, рейсы.
2. НИКОГДА не давай конкретных рекомендаций, не навязывай свое мнение, но при этом твои советы должны раскрывать потребность туриста. 
3. Задавай ВОПРОСЫ для уточнения потребностей.
4. Если просят конкретику — вежливо поясни, что нужно больше данных для составления индивидуальной подборки и ненавязчиво предлагай созвон или встречу в офисе с живым турагентом.
5. Говори как живой человек, естественно.

Используй следующие критерии:
Критерий 1 - Тип поездки: {trip_type}
Критерий 2 — Пункт назначения: {destination}
Критерий 3 - Количество человек: {group_size}
Критерий 4 — Даты поездки: {travel_dates}
Критерий 5 - Город отправления: {departure_city}
Критерий 6 - Бюджет: {budget}
Критерий 7 - Наличие и возраст детей: {children_info}
Критерий 8 - История уточняющих вопросов и ответов: {history_dialogue}
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
            
            return content
        else:
            return f"❌ Ошибка API: {response.status_code} - {response.text}"
            
    except requests.exceptions.Timeout:
        return "❌ Превышено время ожидания ответа от API. Попробуйте позже."
    except requests.exceptions.RequestException as e:
        return f"❌ Ошибка соединения с API: {str(e)}"
    except Exception as e:
        return f"❌ Неожиданная ошибка: {str(e)}"

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
        1: "travel dates",
        2: "group size (number of adults)",
        3: "whether children will travel",
        4: "children's ages",
        5: "destination preferences",
        6: "budget",
        7: "departure city",
        8: "clarifying question",
        9: "any additional important details",
    }
    
    current_question = goal_messages.get(current_goal, "the current question")
    
    return f"""I apologize, but I didn't understand your response clearly. 

Could you please answer the question about {current_question}? 

If you're unsure or embarrassed to answer, please let me know when would be a good time to ask you again about this.

Please provide a clear answer so we can continue with your travel planning."""


def validate_user_input(question_asked: str, user_answer: str) -> dict:
    """Validate user input with a fast LLM before accepting it.
    
    Returns a dict with keys: is_valid (bool), reason (str).
    """
    system_prompt = (
        "Ты строгий, но вежливый ассистент. Твоя задача — проверить, отвечает ли "
        "реплика пользователя на заданный вопрос. Если ответ адекватный (даже если короткий) — "
        'верни JSON {"is_valid": true, "reason": ""}. Если пользователь пишет явный бред, '
        "оскорбления или текст не по теме — верни JSON "
        '{"is_valid": false, "reason": "Вежливая просьба ответить на вопрос: [текст вопроса]"}."'
    )
    
    try:
        messages = [
            {"role": "system", "content": system_prompt},
            {
                "role": "user",
                "content": (
                    f"Вопрос: {question_asked}\n"
                    f"Ответ пользователя: {user_answer}\n"
                    "Верни только JSON без пояснений."
                ),
            },
        ]
        
        response = litellm.completion(
            model="gemini-2.0-flash-exp:free",
            messages=messages,
            max_tokens=128,
            temperature=0.0,
        )
        content = response["choices"][0]["message"]["content"]
        
        # Попробуем вытащить JSON даже если вокруг есть лишний текст/форматирование
        start = content.find("{")
        end = content.rfind("}")
        if start != -1 and end != -1:
            json_str = content[start : end + 1]
            return json.loads(json_str)
    except Exception:
        # При ошибке валидатор не блокирует пользователя
        pass
    
    return {"is_valid": True, "reason": ""}

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
    return f"{message}\nДо связи..."

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
        "max_errors": 3,
        "goal_completed": False,
        "conversation_active": True,
        "has_asked_goal_1": False,
        "dynamic_questions_count": 0,
        "dynamic_completed": False,
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
    
    current_goal = agent_state["current_goal"]
    
    # Generate next question or response based on current goal
    if current_goal == 2:
        response = ask_group_size()
    elif current_goal == 3:
        response = ask_children_exist()
    elif current_goal == 4:
        response = ask_children_age()
    elif current_goal == 5:
        response = ask_destination_preferences()
    elif current_goal == 6:
        response = ask_budget()
    elif current_goal == 7:
        response = ask_departure_city()
    elif current_goal == 8:
        # Первая итерация динамического цикла Perplexity
        responses = agent_state["user_responses"]
        trip_type = responses.get("trip_type", "Организованный туризм через турфирму")
        destination = responses.get("destination", "")
        group_size = responses.get("group_size", "")
        travel_dates = responses.get("travel_dates", "")
        departure_city = responses.get("departure_city", "")
        budget = responses.get("budget", "")
        children_info = responses.get("children_info", "")
        dialogue_history = responses.get("dialogue_history", [])
        history_dialogue = "\n".join(dialogue_history) if dialogue_history else ""
        
        response = get_perplexity_recommendations(
            trip_type,
            destination,
            group_size,
            travel_dates,
            departure_city,
            budget,
            children_info,
            history_dialogue,
        )
        agent_state["last_agent_response"] = response
        agent_state["dynamic_questions_count"] = agent_state.get("dynamic_questions_count", 0) + 1
    elif current_goal == 9:
        response = ask_final_catch_all()
    elif current_goal == 10:
        # Завершающее сообщение и терминатор
        final_message = (
            "Отлично! Все ваши вводные учтем максимально. Эксперт подготовит для вас "
            "подборку туров, и свяжется с вами"
        )
        response = terminate(final_message)
        agent_state["conversation_active"] = False
        agent_state["goal_completed"] = True
    else:
        response = "Travel planning session completed. Thank you!"
    
    memory.add_memory({"type": "assistant", "content": response})
    # Храним последний ответ агента для истории диалога
    agent_state["last_agent_response"] = response
    
    return memory

def process_user_response(user_response: str):
    """Process user response and advance to next goal"""
    
    from game.core import Memory
    
    current_goal = agent_state["current_goal"]
    responses = agent_state["user_responses"]
    
    # Жестко фиксируем тип поездки
    responses["trip_type"] = "Организованный туризм через турфирму"
    
    # Подготовка текста вопроса для валидатора по текущей цели
    question_text_map = {
        1: "Пожалуйста, укажите даты поездки",
        2: "Хорошо. Кто поедет? Сколько взрослых?",
        3: "Поедут ли дети? (Да/Нет)",
        4: "Уточните возраст детей?",
        5: "Есть ли пожелания по направлению/стране/городу назначения?",
        6: "Хорошо. В какой общий бюджет хотели бы уложиться?",
        7: "Откуда планируете стартовать?",
        8: "Пожалуйста, ответьте на уточняющий вопрос по путешествию",
        9: (
            "Спасибо за Ваши ответы. Подскажите, какие еще моменты важно учесть "
            "при составлении подборки туров, которые ранее не обсудили?"
        ),
    }
    question_asked = question_text_map.get(current_goal, "")
    
    # Валидация ответа пользователя (защита от "дурака")
    if question_asked:
        validation_result = validate_user_input(question_asked, user_response)
        if not validation_result.get("is_valid", True):
            # Не меняем current_goal, возвращаем вежливую просьбу
            reason = validation_result.get("reason") or question_asked
            memory = Memory()
            memory.add_memory({"type": "user", "content": user_response})
            memory.add_memory({"type": "assistant", "content": reason})
            return memory
    
    # Сохранение ответа и переходы по целям
    if current_goal == 1:
        # Первый ответ всегда трактуем как даты поездки
        responses["travel_dates"] = user_response
        agent_state["current_goal"] = 2
    elif current_goal == 2:
        responses["group_size"] = user_response
        agent_state["current_goal"] = 3
    elif current_goal == 3:
        responses["children_exist"] = user_response
        # Если детей нет, сразу прыгаем на Goal 5
        if "нет" in user_response.lower() or "no" in user_response.lower():
            responses["children_info"] = "Детей нет"
            agent_state["current_goal"] = 5
        else:
            agent_state["current_goal"] = 4
    elif current_goal == 4:
        responses["children_age"] = user_response
        # Формируем сводную информацию о детях
        responses["children_info"] = f"Дети: {user_response}"
        agent_state["current_goal"] = 5
    elif current_goal == 5:
        responses["destination"] = user_response
        agent_state["current_goal"] = 6
    elif current_goal == 6:
        responses["budget"] = user_response
        agent_state["current_goal"] = 7
    elif current_goal == 7:
        responses["departure_city"] = user_response
        agent_state["current_goal"] = 8
    elif current_goal == 8:
        # Динамический цикл Perplexity
        # Накапливаем историю уточняющих вопросов и ответов
        last_agent_question = agent_state.get("last_agent_response", "")
        if "dialogue_history" not in responses:
            responses["dialogue_history"] = []
        dialogue_entry = f"Вопрос: {last_agent_question} | Ответ: {user_response}"
        responses["dialogue_history"].append(dialogue_entry)
        
        # Увеличиваем счетчик динамических вопросов
        agent_state["dynamic_questions_count"] = agent_state.get("dynamic_questions_count", 0) + 1
        
        # Если достигнут лимит, переходим на Goal 9
        if agent_state["dynamic_questions_count"] >= 10:
            agent_state["dynamic_completed"] = True
            agent_state["current_goal"] = 9
            
            # Задаем финальный вопрос (Goal 9)
            memory = Memory()
            memory.add_memory({"type": "user", "content": user_response})
            memory.add_memory({"type": "assistant", "content": ask_final_catch_all()})
            agent_state["last_agent_response"] = ask_final_catch_all()
            return memory
        else:
            # Остаемся на Goal 8 и генерируем следующий вопрос через Perplexity
            trip_type = responses.get("trip_type", "Организованный туризм через турфирму")
            destination = responses.get("destination", "")
            group_size = responses.get("group_size", "")
            travel_dates = responses.get("travel_dates", "")
            departure_city = responses.get("departure_city", "")
            budget = responses.get("budget", "")
            children_info = responses.get("children_info", "")
            dialogue_history = responses.get("dialogue_history", [])
            history_dialogue = "\n".join(dialogue_history) if dialogue_history else ""
            
            perplexity_answer = get_perplexity_recommendations(
                trip_type,
                destination,
                group_size,
                travel_dates,
                departure_city,
                budget,
                children_info,
                history_dialogue,
            )
            agent_state["last_agent_response"] = perplexity_answer
            
            memory = Memory()
            memory.add_memory({"type": "user", "content": user_response})
            memory.add_memory({"type": "assistant", "content": perplexity_answer})
            return memory
    elif current_goal == 9:
        # Финальный открытый ответ перед завершением
        responses["final_notes"] = user_response
        agent_state["current_goal"] = 10
        # Следующее сообщение будет терминальным
        return run_travel_agent_with_input("continue")
    elif current_goal == 10:
        # Если пользователь что-то пишет после финального сообщения, просто завершаем
        memory = Memory()
        memory.add_memory({"type": "user", "content": user_response})
        final_message = (
            "Отлично! Все ваши вводные учтем максимально. Эксперт подготовит для вас "
            "подборку туров, и свяжется с вами"
        )
        memory.add_memory({"type": "assistant", "content": terminate(final_message)})
        agent_state["conversation_active"] = False
        agent_state["goal_completed"] = True
        return memory
    
    # По умолчанию — отдаем управление генерации следующего шага
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
        
        # Сбрасываем состояние только если разговор явно завершен или не активен
        if goal_completed or not conversation_active:
            reset_agent_state()
        
        # Всегда трактуем входящее сообщение как ответ на текущую цель
        final_memory = process_user_response(message)

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
