import os
import sys
from dotenv import load_dotenv
from openai import OpenAI

# 1. Setup
load_dotenv(override=True)
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Day 3: Advanced Role Management
# We are creating a 'Persona Bot' to show how the System role dominates behavior.
SYSTEM_PROMPT = """
You are a 'Senior Code Reviewer'. 
Your personality: Strict, efficient, and slightly sarcastic.
Your rule: You only answer coding questions. If the user asks about anything else, 
politely but firmly tell them you are here to review code, not chat about life.
"""

chat_history = [
    {"role": "system", "content": SYSTEM_PROMPT}
]

def chat():
    #global chat_history
    print("--- 🧐 Senior Code Reviewer Bot ---")
    
    while True:
        user_input = input("\nYou: ")
        if user_input.lower() in ["exit", "quit"]:
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
            

        except Exception as e:
            print(f"\n❌ Error: {e}")

if __name__ == "__main__":
    chat()
