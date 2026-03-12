#!/usr/bin/env python3
"""
Telegram Bot Integration for AI Travel Agent
This module handles Telegram bot interactions and webhook processing
"""

import os
import logging
from typing import Dict, Any, Optional
from telebot import TeleBot, types
from telebot.util import quick_markup
import json
from dotenv import load_dotenv

# Import the travel agent functions
from travel_agent import run_travel_agent_with_input, process_user_response, agent_state, reset_agent_state, process_travel_request

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Get Telegram bot token from environment
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "8197325061:AAG1hBi0upczFxDKg8T9KtTnmGBtUQQzxiM")

# Initialize the bot
bot = TeleBot(TELEGRAM_BOT_TOKEN)

# Store user sessions
user_sessions: Dict[int, Dict[str, Any]] = {}

def get_user_session(user_id: int) -> Dict[str, Any]:
    """Get or create user session"""
    if user_id not in user_sessions:
        user_sessions[user_id] = {
            "conversation_active": False,
            "current_goal": 1,
            "user_responses": {},
            "error_count": 0,
            "max_errors": 3,
            "goal_completed": False,
            "has_asked_goal_1": False
        }
    return user_sessions[user_id]

def reset_user_session(user_id: int):
    """Reset user session for new conversation"""
    user_sessions[user_id] = {
        "conversation_active": False,
        "current_goal": 1,
        "user_responses": {},
        "error_count": 0,
        "max_errors": 3,
        "goal_completed": False,
        "has_asked_goal_1": False
    }

async def process_travel_agent_message(user_id: int, message_text: str) -> str:
    """Process message through travel agent and return response (async)."""
    try:
        # Get user session
        session = get_user_session(user_id)
        
        # Update global agent state with user session
        global agent_state
        agent_state.update(session)
        
        # Use the common function to process the travel request
        result = await process_travel_request(message_text)  # str(user_id)
        
        # Update user session with current agent state
        session.update(agent_state)
        
        # Get the last assistant message from memory
        memory_list = result["memory"]
        assistant_messages = [item for item in memory_list if item["type"] == "assistant"]
        
        if assistant_messages:
            return assistant_messages[-1]["content"]
        else:
            return "Извините, произошла ошибка при обработке вашего запроса. Попробуйте еще раз."
            
    except Exception as e:
        logger.error(f"Error processing travel agent message: {str(e)}")
        return f"Произошла ошибка: {str(e)}. Попробуйте еще раз."

@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    """Handle /start and /help commands"""
    welcome_text = """🌍 Добро пожаловать в AI Travel Agent!

Я помогу вам спланировать идеальную поездку! Просто напишите мне, и я проведу с вами интервью, чтобы понять ваши предпочтения.

Что я могу для вас сделать:
• Помочь выбрать тип поездки
• Подобрать подходящее направление
• Учесть количество путешественников
• Предложить оптимальные даты
• Дать рекомендации по городам отправления
• Предоставить подробные советы и ссылки

Просто напишите "хочу спланировать поездку" или "travel" и начнем! ✈️

Команды:
/start - Начать новую беседу
/help - Показать эту справку
/status - Показать текущий статус планирования"""
    
    bot.reply_to(message, welcome_text)

@bot.message_handler(commands=['status'])
def send_status(message):
    """Handle /status command"""
    user_id = message.from_user.id
    session = get_user_session(user_id)
    
    if session["goal_completed"]:
        status_text = "✅ Планирование поездки завершено!"
    elif session["conversation_active"]:
        goal_descriptions = {
            1: "Выбор типа поездки",
            2: "Выбор направления",
            3: "Количество путешественников",
            4: "Даты поездки",
            5: "Город отправления",
            6: "Генерация рекомендаций",
            7: "Обратная связь",
            8: "Связь с турагентом"
        }
        current_goal = session["current_goal"]
        status_text = f"🔄 Текущий этап: {current_goal}/8 - {goal_descriptions.get(current_goal, 'Неизвестно')}"
    else:
        status_text = "❌ Активная беседа не найдена. Напишите /start для начала планирования."
    
    bot.reply_to(message, status_text)

@bot.message_handler(func=lambda message: True)
def handle_message(message):
    """Handle all other messages"""
    try:
        user_id = message.from_user.id
        message_text = message.text
        
        logger.info(f"Received message from user {user_id}: {message_text}")
        
        # Process message through travel agent
        response = process_travel_agent_message(user_id, message_text)
        
        # Send response back to user
        bot.reply_to(message, response)
        
        logger.info(f"Sent response to user {user_id}: {response[:100]}...")
        
    except Exception as e:
        logger.error(f"Error handling message: {str(e)}")
        bot.reply_to(message, "Извините, произошла ошибка при обработке вашего сообщения. Попробуйте еще раз.")

def set_webhook(webhook_url: str):
    """Set webhook for the bot"""
    try:
        bot.remove_webhook()
        bot.set_webhook(url=webhook_url)
        logger.info(f"Webhook set to: {webhook_url}")
        return True
    except Exception as e:
        logger.error(f"Error setting webhook: {str(e)}")
        return False

def process_webhook_update(update_data: Dict[str, Any]) -> bool:
    """Process webhook update"""
    try:
        update = types.Update.de_json(update_data)
        bot.process_new_updates([update])
        return True
    except Exception as e:
        logger.error(f"Error processing webhook update: {str(e)}")
        return False

def get_bot_info():
    """Get bot information"""
    try:
        bot_info = bot.get_me()
        return {
            "id": bot_info.id,
            "username": bot_info.username,
            "first_name": bot_info.first_name,
            "can_join_groups": bot_info.can_join_groups,
            "can_read_all_group_messages": bot_info.can_read_all_group_messages,
            "supports_inline_queries": bot_info.supports_inline_queries
        }
    except Exception as e:
        logger.error(f"Error getting bot info: {str(e)}")
        return None

def run_polling():
    """Run bot in polling mode (for development)"""
    logger.info("Starting bot in polling mode...")
    bot.infinity_polling()

if __name__ == "__main__":
    # Run in polling mode for development
    run_polling()
