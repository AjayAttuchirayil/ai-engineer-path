import os
import sys
from dotenv import load_dotenv
from openai import OpenAI

# 1. Setup
load_dotenv(override=True)
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# 2. THE MEMORY (The core of Week 3)
# We store the entire conversation in a list of dictionaries.
chat_history = [
    {"role": "system", "content": "You are a friendly AI tutor."}
]

def chat():
    print("--- 🧠 AI with Memory (Type 'exit' to stop) ---")
    
    while True:
        user_input = input("\nYou: ")
        
        if user_input.lower() in ["exit", "quit"]:
            break

        # 3. Add the user's message to our history
        chat_history.append({"role": "user", "content": user_input})

        try:
            # 4. We send the WHOLE history, not just the new message
            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=chat_history, # Sending the full list
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

            # 5. CRITICAL STEP: Add the AI's response to history 
            # so it remembers what it said in the next turn!
            chat_history.append({"role": "assistant", "content": full_ai_response})
            print()

        except Exception as e:
            print(f"\n❌ Error: {e}")

if __name__ == "__main__":
    chat()
