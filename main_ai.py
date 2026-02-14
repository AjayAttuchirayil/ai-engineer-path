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

# --- Week 4 | Day 6: The AI Assistant Project ---

def search_web(query):
    """Searches the live internet for the given query."""
    print(f"[🌐 Tool] Searching the web for: '{query}'...")
    if not TAVILY_API_KEY:
        return {"error": "Tavily API Key missing."}

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
        formatted_results = [f"Source: {res['url']}\nContent: {res['content']}" for res in results.get("results", [])]
        return {"results": "\n\n".join(formatted_results)}
    except Exception as e:
        return {"error": f"Search failed: {str(e)}"}

def save_to_file(filename, content):
    """Saves text content to a local file."""
    print(f"[💾 Tool] Saving content to '{filename}'...")
    try:
        # We ensure the filename is safe and simple
        safe_filename = os.path.basename(filename)
        with open(safe_filename, "w", encoding="utf-8") as f:
            f.write(content)
        return {"status": "success", "message": f"File '{safe_filename}' saved successfully."}
    except Exception as e:
        return {"status": "error", "message": str(e)}

# Dispatcher
available_functions = {
    "search_web": search_web,
    "save_to_file": save_to_file
}

# Tool Schemas
tools = [
    {
        "type": "function",
        "function": {
            "name": "search_web",
            "description": "Search the internet for current events, news, or facts.",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {"type": "string", "description": "The search query"},
                },
                "required": ["query"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "save_to_file",
            "description": "Save research results or summaries to a local text file.",
            "parameters": {
                "type": "object",
                "properties": {
                    "filename": {"type": "string", "description": "The name of the file (e.g., report.txt)"},
                    "content": {"type": "string", "description": "The full text content to save"},
                },
                "required": ["filename", "content"],
            },
        },
    }
]

def run_conversation(user_prompt):
    messages = [
        {"role": "system", "content": "You are a Research Assistant. Use the web to find facts and save important reports to files when requested."},
        {"role": "user", "content": user_prompt}
    ]
    
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
    # The ultimate test: Research + Synthesis + File I/O
    project_prompt = "Research the top 3 AI news stories from this week and save a summarized report to 'ai_news_weekly.txt'."
    run_conversation(project_prompt)