import os
import pytest
from openai import OpenAI
from anthropic import Anthropic
import google.generativeai as genai
import requests
from groq import Groq

def test_openai_connection():
    client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
    try:
        response = client.chat.completions.create(
            model="gpt-4-turbo-preview",
            messages=[{"role": "user", "content": "Hello, this is a test message."}],
            max_tokens=10
        )
        assert response.choices[0].message.content is not None
        print("✅ OpenAI API connection successful")
        return True
    except Exception as e:
        print(f"❌ OpenAI API connection failed: {str(e)}")
        return False

def test_anthropic_connection():
    client = Anthropic(api_key=os.getenv('ANTHROPIC_API_KEY'))
    try:
        response = client.messages.create(
            model="claude-3-opus-20240229",
            max_tokens=10,
            messages=[{"role": "user", "content": "Hello, this is a test message."}]
        )
        assert response.content[0].text is not None
        print("✅ Anthropic API connection successful")
        return True
    except Exception as e:
        print(f"❌ Anthropic API connection failed: {str(e)}")
        return False

def test_google_connection():
    genai.configure(api_key=os.getenv('GOOGLE_API_KEY'))
    try:
        model = genai.GenerativeModel('gemini-1.5-pro')
        response = model.generate_content("Hello, this is a test message.")
        assert response.text is not None
        print("✅ Google API connection successful")
        return True
    except Exception as e:
        print(f"❌ Google API connection failed: {str(e)}")
        return False

def test_deepseek_connection():
    api_key = os.getenv('DEEPSEEK_API_KEY')
    try:
        response = requests.post(
            "https://api.deepseek.com/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json"
            },
            json={
                "model": "deepseek-chat",
                "messages": [{"role": "user", "content": "Hello, this is a test message."}],
                "max_tokens": 10
            }
        )
        assert response.status_code == 200
        print("✅ DeepSeek API connection successful")
        return True
    except Exception as e:
        print(f"❌ DeepSeek API connection failed: {str(e)}")
        return False

def test_deepseek_reasoning():
    api_key = os.getenv('DEEPSEEK_API_KEY')
    try:
        response = requests.post(
            "https://api.deepseek.com/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json"
            },
            json={
                "model": "deepseek-reasoner",  # Using DeepSeek's reasoning model
                "messages": [{"role": "user", "content": "Explain the concept of recursion in programming."}],
                "max_tokens": 100
            }
        )
        assert response.status_code == 200
        # Check for reasoning_content in the response
        response_data = response.json()
        assert 'reasoning_content' in response_data['choices'][0]['message']
        print("✅ DeepSeek Reasoning API connection successful")
        return True
    except Exception as e:
        print(f"❌ DeepSeek Reasoning API connection failed: {str(e)}")
        return False

def test_groq_connection():
    client = Groq(api_key=os.getenv('GROQ_API_KEY'))
    try:
        response = client.chat.completions.create(
            model="llama2-70b-4096",
            messages=[{"role": "user", "content": "Hello, this is a test message."}],
            max_tokens=10
        )
        assert response.choices[0].message.content is not None
        print("✅ Groq API connection successful")
        return True
    except Exception as e:
        print(f"❌ Groq API connection failed: {str(e)}")
        return False

def test_ollama_connection():
    try:
        response = requests.post(
            "http://localhost:11434/api/generate",
            json={
                "model": "codellama",
                "prompt": "Hello, this is a test message.",
                "max_tokens": 10
            }
        )
        assert response.status_code == 200
        print("✅ Ollama connection successful")
        return True
    except Exception as e:
        print(f"❌ Ollama connection failed: {str(e)}")
        return False

if __name__ == "__main__":
    print("\nTesting LLM API Connections...\n")
    
    results = {
        "OpenAI": test_openai_connection(),
        "Anthropic": test_anthropic_connection(),
        "Google": test_google_connection(),
        "DeepSeek": test_deepseek_connection(),
        "DeepSeek Reasoning": test_deepseek_reasoning(),
        "Groq": test_groq_connection(),
        "Ollama": test_ollama_connection()
    }
    
    print("\nTest Results Summary:")
    print("-" * 30)
    for provider, success in results.items():
        status = "✅" if success else "❌"
        print(f"{status} {provider}") 