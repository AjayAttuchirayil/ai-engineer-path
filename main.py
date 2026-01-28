import os
import sys
from dotenv import load_dotenv
from openai import OpenAI, RateLimitError, AuthenticationError, APIConnectionError, APIError

# 1. Load the variables from the .env file
load_dotenv(override=True)

# 2. Setup the API Key
api_key = os.getenv("OPENAI_API_KEY")

# 3. Initialize the OpenAI Client
try:
    client = OpenAI(api_key=api_key)
except Exception as e:
    print(f"❌ Initialization Error: {e}")
    sys.exit(1)

def translate_text():
    """Main function to handle the translation logic."""
    if not api_key:
        print("❌ Error: OPENAI_API_KEY not found in .env file.")
        return

    print("--- 🤖 AI Translator Bot ---")
    text_to_translate = input("Enter the text you want to translate: ")
    target_language = input("Enter the target language (e.g., Spanish, French, Japanese): ")

    try:
        # Week 2 | Day 7: The Translator Bot Finale
        # We combine streaming, system roles, and user inputs
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {
                    "role": "system", 
                    "content": f"You are a professional translator. Translate the user's text into {target_language}. Provide only the translation, no extra commentary."
                },
                {"role": "user", "content": text_to_translate}
            ],
            temperature=0.3, # Lower temperature for more accurate translations
            stream=True,
            stream_options={"include_usage": True}
        )

        print(f"\n{target_language} Translation: ", end="")
        
        total_usage = None
        for chunk in response:
            if chunk.usage is not None:
                total_usage = chunk.usage
            
            if len(chunk.choices) > 0:
                content = chunk.choices[0].delta.content
                if content:
                    sys.stdout.write(content)
                    sys.stdout.flush()

        if total_usage:
            print(f"\n\n📊 Stats: Used {total_usage.total_tokens} tokens.")

    except AuthenticationError:
        print("\n❌ Error: Invalid API Key.")
    except RateLimitError:
        print("\n❌ Error: API Quota exceeded.")
    except APIConnectionError:
        print("\n❌ Error: Check your internet connection.")
    except Exception as e:
        print(f"\n❌ Unexpected Error: {e}")
    
    finally:
        print("\n--- Translation Task Complete ---")

if __name__ == "__main__":
    translate_text()
