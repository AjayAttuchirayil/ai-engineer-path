import os
from dotenv import load_dotenv
from openai import OpenAI, RateLimitError

# 1. Load the variables from the .env file
load_dotenv()

# 2. Setup the API Key
# Replace "OPENAI_API_KEY" with the exact name used in your .env file
api_key = os.getenv("OPENAI_API_KEY")

# 3. Initialize the OpenAI Client
# This client object will be our primary tool for all AI interactions
client = OpenAI(api_key=api_key)

# 4. Validation & Connection Test
if not api_key:
    print("❌ Error: OPENAI_API_KEY not found in .env file.")
else:
    print("✅ System Ready: OpenAI Client Initialized.")
    
    try:
        # Sending a simple request to test the connection
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": "Write a one-sentence greeting to a new AI Engineer."}
            ]
        )

        # Printing the result
        print(f"\nAI Response: {response.choices[0].message.content}")

    except RateLimitError as e:
        print("\n❌ Quota Error (429): You have hit your OpenAI rate limit or exhausted your credits.")
        print("💡 Tips to fix this:")
        print("1. Check your billing dashboard at https://platform.openai.com/account/billing")
        print("2. Ensure you have at least $5.00 in credits (OpenAI requires a minimum balance for API access).")
        print("3. If using a new account, wait a few minutes; sometimes there is a delay in credit activation.")
    except Exception as e:
        print(f"\n❌ An unexpected error occurred: {e}")
