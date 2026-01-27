import os
import sys
from dotenv import load_dotenv
from openai import OpenAI, RateLimitError

# 1. Load the variables from the .env file
load_dotenv()

# 2. Setup the API Key
api_key = os.getenv("OPENAI_API_KEY")

# 3. Initialize the OpenAI Client
client = OpenAI(api_key=api_key)

# 4. Validation & Connection Test
if not api_key:
    print("❌ Error: OPENAI_API_KEY not found in .env file.")
else:
    print("✅ System Ready: OpenAI Client Initialized.")
    
    try:
        # Week 2 | Day 5: Streaming Responses
        # We add 'stream=True' to get the response chunk by chunk
        # 'stream_options' allows us to still get usage data at the end of the stream
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are a helpful assistant who explains complex topics simply."},
                {"role": "user", "content": "Explain how a solar panel works in 3 paragraphs."}
            ],
            temperature=0.7,
            max_tokens=300,
            stream=True,
            stream_options={"include_usage": True} 
        )

        print("\nAI Response: ", end="")
        
        # When streaming, we must iterate through the chunks
        total_usage = None
        for chunk in response:
            # Check if this chunk contains usage data (usually the last chunk)
            if chunk.usage is not None:
                total_usage = chunk.usage
            
            # Check if this chunk contains text content
            if len(chunk.choices) > 0:
                content = chunk.choices[0].delta.content
                if content:
                    # Print the chunk immediately to the terminal
                    sys.stdout.write(content)
                    sys.stdout.flush()

        # Printing the final usage stats
        if total_usage:
            print(f"\n\n📊 Total Tokens Used: {total_usage.total_tokens}")
            print(f"   (Prompt: {total_usage.prompt_tokens}, Completion: {total_usage.completion_tokens})")

    except RateLimitError:
        print("\n❌ Quota Error (429): You have hit your OpenAI rate limit or exhausted your credits.")
    except Exception as e:
        print(f"\n❌ An unexpected error occurred: {e}")
