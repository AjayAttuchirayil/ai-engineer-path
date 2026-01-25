import os
from dotenv import load_dotenv

# 1. Load the variables from the .env file into the system environment
load_dotenv()

# 2. Retrieve the specific variable
api_key = os.getenv("MY_TEST_KEY")

# 3. Validation Logic
if api_key:
    print("✅ Success! The environment variable was found.")
    print(f"The key starts with: {api_key[:5]}...") # Security tip: never print the whole key!
else:
    print("❌ Error: Could not find MY_TEST_KEY. Check your .env file.")
