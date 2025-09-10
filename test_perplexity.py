#!/usr/bin/env python3
"""
Test script for Perplexity API integration
"""

import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def test_perplexity_integration():
    """Test the Perplexity API integration with sample data"""
    
    # Import the function from travel_agent
    from travel_agent import get_perplexity_recommendations
    
    # Test data
    trip_type = "Организованный туризм с использованием услуг туроператора"
    destination = "Турция, Анталья"
    group_size = "2 человека"
    travel_dates = "15-25 июня 2024"
    departure_city = "Москва"
    
    print("🧪 Тестирование интеграции с Perplexity API...")
    print("=" * 60)
    print(f"Тип поездки: {trip_type}")
    print(f"Направление: {destination}")
    print(f"Количество человек: {group_size}")
    print(f"Даты: {travel_dates}")
    print(f"Город отправления: {departure_city}")
    print("=" * 60)
    
    try:
        result = get_perplexity_recommendations(
            trip_type, destination, group_size, travel_dates, departure_city
        )
        print("\n✅ РЕЗУЛЬТАТ:")
        print(result)
        return True
    except Exception as e:
        print(f"\n❌ ОШИБКА: {str(e)}")
        return False

if __name__ == "__main__":
    # Check if API key is available
    api_key = os.getenv("PERPLEXITY_API_KEY")
    if not api_key:
        print("❌ PERPLEXITY_API_KEY не найден в .env файле")
        print("Пожалуйста, добавьте PERPLEXITY_API_KEY=your_key в .env файл")
        exit(1)
    
    print(f"✅ API ключ найден: {api_key[:10]}...")
    test_perplexity_integration()


