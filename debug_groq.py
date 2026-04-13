#!/usr/bin/env python3
"""Debug script to check Groq API key configuration"""

import os
from dotenv import load_dotenv
import requests

# Load environment variables
load_dotenv(".env.local")

GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")
GROQ_API_URL = "https://api.groq.com/openai/v1/chat/completions"

print(f"🔍 Groq API Key Debug")
print(f"Key (first 20 chars): {GROQ_API_KEY[:20]}..." if GROQ_API_KEY else "❌ No key found")
print(f"Key length: {len(GROQ_API_KEY)}")
print(f"Key repr: {repr(GROQ_API_KEY)}")

if not GROQ_API_KEY:
    print("❌ No API key found in .env.local")
    exit(1)

# Test the API key
print("\n🧪 Testing Groq API connection...")

headers = {
    "Authorization": f"Bearer {GROQ_API_KEY}",
    "Content-Type": "application/json"
}

test_payload = {
    "model": "llama-3.1-8b-instant",
    "messages": [{"role": "user", "content": "What is 2+2?"}],
    "temperature": 0.7,
    "max_tokens": 10
}

try:
    response = requests.post(
        GROQ_API_URL,
        headers=headers,
        json=test_payload,
        timeout=10
    )
    
    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.text[:500]}")
    
    if response.status_code == 200:
        print("✅ API key is valid!")
    elif response.status_code == 401:
        print("❌ Invalid API key (401)")
    else:
        print(f"⚠️ Unexpected status code: {response.status_code}")
        
except Exception as e:
    print(f"❌ Error: {e}")
