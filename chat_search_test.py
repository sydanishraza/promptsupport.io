#!/usr/bin/env python3
"""
Additional test to investigate chat search functionality
"""

import requests
import json
import uuid

BACKEND_URL = "https://c14dc277-70df-425b-a9d5-f1d91d1168d4.preview.emergentagent.com/api"

def test_chat_search():
    """Test chat with different queries to see if search is working"""
    session_id = str(uuid.uuid4())
    
    # Test with different queries
    queries = [
        "PromptSupport",
        "AI-native support platform", 
        "document upload",
        "features",
        "getting started",
        "natural language processing"
    ]
    
    print("🔍 Testing Chat Search with Various Queries...")
    
    for query in queries:
        print(f"\n📝 Query: '{query}'")
        
        chat_data = {
            "message": query,
            "session_id": session_id
        }
        
        try:
            response = requests.post(
                f"{BACKEND_URL}/chat", 
                json=chat_data,
                headers={"Content-Type": "application/json"},
                timeout=15
            )
            
            if response.status_code == 200:
                data = response.json()
                print(f"Response: {data['response'][:100]}...")
                if data.get('sources'):
                    print(f"Sources found: {data['sources']}")
                else:
                    print("No sources found")
            else:
                print(f"Error: {response.status_code}")
                
        except Exception as e:
            print(f"Error: {str(e)}")

if __name__ == "__main__":
    test_chat_search()