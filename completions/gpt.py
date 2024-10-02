import os

from openai import OpenAI
from dotenv import load_dotenv
import pandas as pd

import prompts

load_dotenv()

key = os.getenv("OPENAI_API_KEY")
organization = os.getenv("OPENAI_ORGANIZATION")

client = OpenAI(api_key=key, base_url="https://api.openai.com/v1", organization="org-62CllBpIXV3KJBB9kJMO2bAs")

# Load the dataset
file_path = "datasets/cn_k12_math_problems.csv"
data = pd.read_csv(file_path, nrows=50)  # Only the first 50 records

# Loop through the first 50 records and print them out
for index, row in data.iterrows():
    chat_completion = client.chat.completions.create(
        model="o1-mini",
        messages=[
            {"role": "user", "content": prompts.COMPLETION_PROMPT.format(problem=row["problem"], partial_solution=row["partial_solution"])}
        ]
    )
    print(chat_completion)