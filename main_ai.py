import os
import json
import sys
import requests
from dotenv import load_dotenv
from openai import OpenAI

# 1. Setup
load_dotenv(override=True)
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
TAVILY_API_KEY = os.getenv("TAVILY_API_KEY")

# --- Week 4 | Day 5: Real-World Search Integration ---

def search_web(query):
    """
    Searches the live internet for the given query.
    Returns a list of search results with titles, URLs, and snippets.
    """
    print(f"[🌐 Tool] Searching the web for: '{query}'...")
    
    if not TAVILY_API_KEY:
        return {"error": "Tavily API Key missing. Please add it to your .env file."}

    url = "https://api.tavily.com/search"
    payload = {
        "api_key": TAVILY_API_KEY,
        "query": query,
        "search_depth": "basic",
        "max_results": 3
    }
    
    try:
        response = requests.post(url, json=payload)
        response.raise_for_status()
        results = response.json()
        
        # We format the results into a clean string for the LLM to read
        formatted_results = []
        for res in results.get("results", []):
            formatted_results.append(f"Source: {res['url']}\nContent: {res['content']}")
            
        return {"results": "\n\n".join(formatted_results)}
    except Exception as e:
        return {"error": f"Search failed: {str(e)}"}

def get_unit_converter(value, from_unit, to_unit):
    """Converts values between units"""
    print(f"[🔧 Tool] Converting {value} {from_unit} to {to_unit}...")
    if from_unit.lower() == "celsius" and to_unit.lower() == "fahrenheit":
        result = (float(value) * 9/5) + 32
        return {"result": f"{result:.1f}", "unit": to_unit}
    return {"error": "Conversion not supported yet"}

# Updated Dispatcher
available_functions = {
    "search_web": search_web,
    "get_unit_converter": get_unit_converter
}

# Updated Tool Schemas
tools = [
    {
        "type": "function",
        "function": {
            "name": "search_web",
            "description": "Search the internet for current events, news, or facts that require live data.",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {"type": "string", "description": "The search query to look up on the internet"},
                },
                "required": ["query"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_unit_converter",
            "description": "Convert values between different units",
            "parameters": {
                "type": "object",
                "properties": {
                    "value": {"type": "number", "description": "The numerical value"},
                    "from_unit": {"type": "string", "description": "Source unit"},
                    "to_unit": {"type": "string", "description": "Target unit"},
                },
                "required": ["value", "from_unit", "to_unit"],
            },
        },
    }
]

def run_conversation(user_prompt):
    messages = [{"role": "user", "content": user_prompt}]
    print(f"\nUser: {user_prompt}")
    
    while True:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=messages,
            tools=tools,
            tool_choice="auto",
        )
        
        response_message = response.choices[0].message
        tool_calls = response_message.tool_calls

        if not tool_calls:
            print(f"AI Response: {response_message.content}")
            break

        print(f"🧠 AI: 'I need to use {len(tool_calls)} tool(s).'")
        messages.append(response_message) 

        for tool_call in tool_calls:
            function_name = tool_call.function.name
            function_args = json.loads(tool_call.function.arguments)
            
            function_to_call = available_functions.get(function_name)
            if function_to_call:
                function_response = function_to_call(**function_args)
                
                messages.append({
                    "tool_call_id": tool_call.id,
                    "role": "tool",
                    "name": function_name,
                    "content": json.dumps(function_response),
                })
        
if __name__ == "__main__":
    # Test with a current event
    prompt = "Search for the temperature in Tokyo right now and convert it to Fahrenheit"
    run_conversation(prompt)