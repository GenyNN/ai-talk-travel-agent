#!/usr/bin/env python3
"""
Test script to verify the AI Talk Travel Agent setup
"""

import sys
import importlib

def test_imports():
    """Test if all required packages can be imported"""
    required_packages = [
        'fastapi',
        'uvicorn', 
        'litellm',
        'python-dotenv',
        'pydantic',
        'requests'
    ]
    
    print("🔍 Testing package imports...")
    
    for package in required_packages:
        try:
            importlib.import_module(package)
            print(f"✅ {package}")
        except ImportError as e:
            print(f"❌ {package}: {e}")
            return False
    
    return True

def test_env_file():
    """Test if .env file exists and has required keys"""
    import os
    
    print("\n🔍 Testing environment configuration...")
    
    if not os.path.exists('.env'):
        print("⚠️  .env file not found")
        print("   Please create .env file with your API keys")
        return False
    
    # Load .env file
    from dotenv import load_dotenv
    load_dotenv()
    
    # Check for required API key
    openai_key = os.getenv('OPENAI_API_KEY')
    if not openai_key or openai_key == 'your_openai_api_key_here':
        print("❌ OPENAI_API_KEY not set in .env file")
        print("   Please add your OpenAI API key to .env file")
        return False
    
    print("✅ Environment configuration looks good")
    return True

def test_fastapi_app():
    """Test if FastAPI app can be created"""
    print("\n🔍 Testing FastAPI application...")
    
    try:
        from main import app
        print("✅ FastAPI app created successfully")
        return True
    except Exception as e:
        print(f"❌ Failed to create FastAPI app: {e}")
        return False

def main():
    """Run all tests"""
    print("🧪 AI Talk Travel Agent - Setup Test")
    print("=" * 40)
    
    tests = [
        test_imports,
        test_env_file,
        test_fastapi_app
    ]
    
    all_passed = True
    
    for test in tests:
        if not test():
            all_passed = False
    
    print("\n" + "=" * 40)
    if all_passed:
        print("🎉 All tests passed! Your setup is ready.")
        print("\nTo start the application:")
        print("   python main.py")
        print("\nOr use the startup script:")
        print("   ./start.sh")
    else:
        print("❌ Some tests failed. Please fix the issues above.")
        sys.exit(1)

if __name__ == "__main__":
    main()
