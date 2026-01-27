import os
import sys
from dotenv import load_dotenv
from openai import OpenAI, RateLimitError, AuthenticationError, APIConnectionError, APIError

# 1. Load the variables from the .env file
load_dotenv(override=True)

# 2. Setup the API Key
api_key = os.getenv("OPENAI_API_KEY")

# 3. Initialize the OpenAI Client
# We wrap the initialization in a try-block as well
try:
    client = OpenAI(api_key=api_key)
except Exception as e:
    print(f"❌ Initialization Error: {e}")
    sys.exit(1)

# 4. The "Production-Ready" Request Logic
if not api_key:
    print("❌ Error: OPENAI_API_KEY not found in .env file.")
else:
    print("✅ System Ready: OpenAI Client Initialized.")
    
    try:
        # Week 2 | Day 6: Robust Error Handling
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are a senior software architect."},
                {"role": "user", "content": "What are the top 3 best practices for error handling in Python?"}
            ],
            temperature=0.7,
            max_tokens=300,
            stream=True,
            stream_options={"include_usage": True} 
        )

        print("\nAI Response: ", end="")
        
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
            print(f"\n\n📊 Total Tokens Used: {total_usage.total_tokens}")

    except AuthenticationError:
        print("\n❌ Authentication Error: Your API key is invalid or has been revoked.")
    except RateLimitError:
        print("\n❌ Rate Limit Error: You've hit your quota or are sending requests too fast.")
    except APIConnectionError:
        print("\n❌ Network Error: Could not connect to OpenAI. Check your internet connection.")
    except APIError as e:
        print(f"\n❌ OpenAI Server Error: Something went wrong on their end. {e}")
    except Exception as e:
        print(f"\n❌ Unexpected Error: {e}")
