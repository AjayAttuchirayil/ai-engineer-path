import os
import sys
from dotenv import load_dotenv
from openai import OpenAI

# 1. Setup
load_dotenv(override=True)
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Configuration: How many messages to keep (excluding system prompt)
MAX_HISTORY = 6 

chat_history = [
    {"role": "system", "content": "You are a helpful coding assistant."}
]

def trim_history(history, max_messages):
    """
    Keeps the system message (index 0) and the most recent N messages.
    """
    if len(history) > max_messages:
        # Keep the system message + the most recent (max_messages - 1)
        # Slicing from the end: history[-(max_messages-1):]
        system_message = [history[0]]
        recent_messages = history[-(max_messages - 1):]
        return system_message + recent_messages
    return history

def chat():
    global chat_history
    print(f"--- 🕰️ Sliding Window Memory (Limit: {MAX_HISTORY}) ---")
    
    while True:
        user_input = input("\nYou: ")
        if user_input.lower() in ["exit", "quit"]:
            break

        chat_history.append({"role": "user", "content": user_input})

        # CRITICAL: Prune history BEFORE the API call to save money
        chat_history = trim_history(chat_history, MAX_HISTORY)

        try:
            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=chat_history,
                stream=True
            )

            print("AI: ", end="")
            full_ai_response = ""
            for chunk in response:
                if len(chunk.choices) > 0:
                    content = chunk.choices[0].delta.content
                    if content:
                        sys.stdout.write(content)
                        sys.stdout.flush()
                        full_ai_response += content

            chat_history.append({"role": "assistant", "content": full_ai_response})
            print()
            
            # Print debug info to see the 'sliding' in action
            print(f"\n[System Note: Context size is now {len(chat_history)} messages]")

        except Exception as e:
            print(f"\n❌ Error: {e}")

if __name__ == "__main__":
    chat()
