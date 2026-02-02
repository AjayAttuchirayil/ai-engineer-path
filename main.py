import os
import sys
import json
from dotenv import load_dotenv
from openai import OpenAI

# 1. Setup
load_dotenv(override=True)
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

HISTORY_FILE = 'chat_history.json'

# Day 3: Advanced Role Management
# We are creating a 'Persona Bot' to show how the System role dominates behavior.
SYSTEM_PROMPT = """
You are a 'Senior Code Reviewer'. 
Your personality: Strict, efficient, and slightly sarcastic.
Your rule: You only answer coding questions.
"""

chat_history = [
    {"role": "system", "content": SYSTEM_PROMPT}
]

def save_history(history):
    """Dumps the conversation in json file to persist in multiple sessions"""
    try:
        with open(HISTORY_FILE, "w") as f:
            json.dump(history, f, indent=4)
    except Exception as e:
        print(f"⚠️ Warning: Could not save history. {e}")

def load_history():
    """Loads history from the JSON file or returns a fresh history if file doesn't exist."""
    if os.path.exists(HISTORY_FILE):
        try:
            with open(HISTORY_FILE, "r") as f:
                return json.load(f)
        except Exception as e:
            print(f"⚠️ Warning: History file corrupted. Starting fresh. {e}")
        
    # Default starting point if no file exists
    return [{"role": "system", "content": SYSTEM_PROMPT}]


def chat():
    #global chat_history

    chat_history = load_history()
    print("--- 🧐 Persistent Reviewer Bot ---")
    print(f"(Current history size: {len(chat_history)} messages)")
    
    while True:
        user_input = input("\nYou: ")
        if user_input.lower() in ["exit", "quit"]:
            save_history(chat_history)
            print("👋 History saved. Goodbye!")
            break

        chat_history.append({"role": "user", "content": user_input})

        try:
            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=chat_history,
                temperature=0.9,
                stream=True
            )

            print("AI: ", end="")
            
            ai_message = ""
            for chunk in response:
                if len(chunk.choices) > 0:
                    content = chunk.choices[0].delta.content
                    if content:
                        sys.stdout.write(content)
                        sys.stdout.flush()
                        ai_message += content

            #print(f"\nReviewer: {ai_message}")

            chat_history.append({"role": "assistant", "content": ai_message})
            # Auto-save after every turn so we don't lose data on a crash
            save_history(chat_history)
            

        except Exception as e:
            print(f"\n❌ Error: {e}")

if __name__ == "__main__":
    chat()
