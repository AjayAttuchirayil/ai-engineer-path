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
PROFILE_FILE = "user_profile.json"
# 2KB threshold for testing - change to 10240 (10KB) for real use
SIZE_THRESHOLD_BYTES = 4096  

def load_json(filepath, default_value):
    """Generic loader for JSON files."""
    if os.path.exists(filepath):
        try:
            with open(filepath, "r") as f:
                return json.load(f)
        except Exception as e:
            print(f"⚠️ Warning: Could not load {filepath}. {e}")
    return default_value

def save_json(filepath, data):
    """Generic saver for JSON files."""
    try:
        with open(filepath, "w") as f:
            json.dump(data, f, indent=4)
    except Exception as e:
        print(f"⚠️ Warning: Could not save {filepath}. {e}")

def load_history():
    """Loads history or returns an empty list."""
    return load_json(HISTORY_FILE, [])

def summarize_history(history):
    """Condenses older messages while preserving the system instructions."""
    print("\n[🔄 System: Summarizing conversation to optimize context...]")
    
    if len(history) < 5:
        return history
        
    system_instruction = history[0]
    recent_exchange = history[-2:]
    middle_content = history[1:-2]

    text_to_summarize = "\n".join([f"{m['role']}: {m['content']}" for m in middle_content])
    
    try:
        summary_response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {
                    "role": "system", 
                    "content": "Summarize the following technical support interaction into a concise bulleted list of facts and resolutions. Avoid conversational filler."
                },
                {"role": "user", "content": text_to_summarize}
            ],
            temperature=0.3
        )
        summary = summary_response.choices[0].message.content
        
        # New history: System Instructions + Summary + Last Interaction
        return [
            system_instruction, 
            {"role": "system", "content": f"Previous Context Summary: {summary}"}
        ] + recent_exchange
    except Exception as e:
        print(f"⚠️ Summarization failed: {e}")
        return history

def get_user_profile():
    """Initializes or loads a persistent user profile."""
    profile = load_json(PROFILE_FILE, {})
    if not profile:
        print("--- 🆕 First Time Setup ---")
        profile['name'] = input("Welcome! What is your name? ")
        profile['level'] = input("What is your technical level? (Beginner/Intermediate/Expert): ")
        profile['topic'] = input("What project or topic are you focusing on? ")
        save_json(PROFILE_FILE, profile)
        print(f"Thanks, {profile['name']}! Profile saved.\n")
    return profile

def chat():
    # Load profile and history
    profile = get_user_profile()
    chat_history = load_history()
    
    # Construct a dynamic System Prompt based on the User Profile
    # Using a clean f-string format to ensure all quotes are closed correctly
    system_prompt = (
        f"You are a Technical Support Engineer. "
        f"You are helping {profile['name']}, who is at an '{profile['level']}' level. "
        f"Their current focus is: {profile['topic']}. "
        f"Adjust your explanations to match their technical level. "
        f"Be helpful, patient, and professional."
    )
    
    # Ensure the history has the correct updated system prompt at index 0
    if chat_history and chat_history[0].get('role') == 'system':
        chat_history[0]['content'] = system_prompt
    else:
        chat_history.insert(0, {"role": "system", "content": system_prompt})

    print(f"--- 🛠️ Support Bot Active (User: {profile['name']}) ---")
    
    while True:
        user_input = input("\nYou: ")
        if user_input.lower() in ["exit", "quit"]:
            save_json(HISTORY_FILE, chat_history)
            print("👋 Session saved. Goodbye!")
            break

        chat_history.append({"role": "user", "content": user_input})

        try:
            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=chat_history,
                stream=True
            )

            print("\nSupport: ", end="")
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
            save_json(HISTORY_FILE, chat_history)

            # Context Management (Summarization based on file size)
            if os.path.exists(HISTORY_FILE) and os.path.getsize(HISTORY_FILE) > SIZE_THRESHOLD_BYTES:
                chat_history = summarize_history(chat_history)
                save_json(HISTORY_FILE, chat_history)

        except Exception as e:
            print(f"\n❌ Error: {e}")

if __name__ == "__main__":
    chat()