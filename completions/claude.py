import os
import anthropic
from dotenv import load_dotenv

load_dotenv()

# Retrieve the API key from the environment variable
api_key = os.environ.get("ANTHROPIC_API_KEY")

# Check if the API key is retrieved correctly
if not api_key:
    raise ValueError("API key not found. Please set the ANTHROPIC_API_KEY environment variable.")


client = anthropic.Anthropic(
    api_key=api_key,
)

message = client.messages.create(
    model="claude-3-5-sonnet-20240620",
    max_tokens=1024,
    messages=[
        {"role": "user", "content": "Hello, Claude"}
    ],
)

print(message.content[0].text)