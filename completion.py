import os

from openai import OpenAI

key = os.getenv("OPENAI_API_KEY")

client = OpenAI(api_key=key)

res = client.chat.completions.create(
    model="gpt-4o-mini",
    messages=[
        {"role": "user", "content": "Hello, world"}
    ]
)

print(res)
