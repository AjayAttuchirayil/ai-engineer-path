import os
import sys
import json
from dotenv import load_dotenv
from openai import OpenAI

# 1. Setup
load_dotenv(override=True)
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# The file where we will store our conversation
HISTORY_FILE = "chat_history.json"
# 2KB threshold for testing - change to 10240 (10KB) for real use
SIZE_THRESHOLD_BYTES = 2048  

SYSTEM_PROMPT = """
You are a 'Senior Code Reviewer'. 
Your personality: Strict, efficient, and slightly sarcastic.
Your rule: You only answer coding questions.
"""

def save_history(history):
    """Saves the chat history list to a JSON file."""
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
    
    return [{"role": "system", "content": SYSTEM_PROMPT}]

def summarize_history(history):
    """
    Condenses older messages into a summary to keep the history file small.
    """
    initial_size = os.path.getsize(HISTORY_FILE)
    print(f"\n[🔄 System: Size limit ({initial_size} bytes) exceeded. Summarizing...]")
    
    # Keep the original System instructions
    system_instruction = history[0]
    # Keep the most recent exchange (last 2 messages) for immediate continuity
    recent_exchange = history[-2:]
    # Everything else goes into the blender
    middle_content = history[1:-2]

    if len(middle_content) < 2:
        return history

    # Prepare the string for the LLM to summarize
    text_to_summarize = "\n".join([f"{m['role']}: {m['content']}" for m in middle_content])
    
    try:
        summary_response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are a context-manager. Summarize the provided chat history into 3-4 bullet points. Focus ONLY on technical facts, project details, and user preferences mentioned. Ignore greetings and fluff."},
                {"role": "user", "content": text_to_summarize}
            ],
            temperature=0.3
        )
        
        summary = summary_response.choices[0].message.content
        
        # New History structure: [System] + [Summary] + [Most Recent Interaction]
        new_history = [
            system_instruction,
            {"role": "system", "content": f"Summary of previous context: {summary}"}
        ] + recent_exchange
        
        return new_history
    except Exception as e:
        print(f"⚠️ Summarization failed: {e}")
        return history

def chat():
    chat_history = load_history()
    
    print("--- 🧐 Self-Optimizing Reviewer Bot ---")
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

            print("\nReviewer: ", end="")
            full_ai_response = ""
            
            for chunk in response:
                if len(chunk.choices) > 0:
                    content = chunk.choices[0].delta.content
                    if content:
                        sys.stdout.write(content)
                        sys.stdout.flush()
                        full_ai_response += content
            
            print()
            chat_history.append({"role": "assistant", "content": full_ai_response})
            
            # 1. Save and Check Size
            save_history(chat_history)
            
            if os.path.exists(HISTORY_FILE):
                current_size = os.path.getsize(HISTORY_FILE)
                if current_size > SIZE_THRESHOLD_BYTES:
                    chat_history = summarize_history(chat_history)
                    save_history(chat_history)
                    new_size = os.path.getsize(HISTORY_FILE)
                    reduction = ((current_size - new_size) / current_size) * 100
                    print(f"✨ Compression complete. Saved {reduction:.1f}% space ({new_size} bytes remaining).")

        except Exception as e:
            print(f"\n❌ Error: {e}")

if __name__ == "__main__":
    chat()