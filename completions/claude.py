import os
import re

import anthropic
import pandas as pd
import prompts
from dotenv import load_dotenv

# Anthropic SDK will look for "ANTHROPIC_API_KEY" as an environment variable
load_dotenv()

# # Check if the API key is retrieved correctly
api_key = os.environ.get("ANTHROPIC_API_KEY")
if not api_key:
    raise ValueError("API key not found. Please set the ANTHROPIC_API_KEY environment variable.")


client = anthropic.Anthropic()

# Load the dataset
file_path = "datasets/perturbed_solutions_0.csv"
data = pd.read_csv(file_path)
print(len(data))

# for index, row in data.iterrows():
#     print(row["id"], row["question"], row["stepped"].count("<step>"))
#     print("\n\n\n\n")

rows = [row for index, row in data.iterrows() if len(re.findall(r"Step \d+:", row["stepped"])) <= 3]
print(f"Number of rows: {len(rows)}")

for row in rows:
    print("\n --------START--------- \n")
    print(  # [[Stepped]]: {row["stepped"]} \n
        f"""
    [[ID]]: {row["id"]}
    [[Question]]: {row["question"]}
    [[Stepified Answer]]: {row["stepped"]} 
    [[Type]]: {row["type"]}
    [[Step]]: {row["step"]}
    [[Trace]]: {row["trace"]} \n
    [[Perturbed]]: {row["perturbed"]} \n
    """
    )
    # print(prompts.COMPLETION_PROMPT.format(question=row["problem"], perturbed_reasoning=row["perturbed"]))
    print("\n~~~~~~~~~Completion~~~~~~~~~~~~~ (Should continue from the Perturbed reasoning)\n")

    completion = client.messages.create(
        model="claude-3-5-sonnet-20240620",
        messages=[
            {
                "role": "user",
                "content": prompts.COMPLETION_PROMPT_V2_USER.format(question=row["question"]),
            },
            {  # Final assistant message cannot gend with trailing whitespace, so we need to .strip() the perturbed reasoning.
                "role": "assistant",
                "content": prompts.COMPLETION_PROMPT_V2_ASSISTANT.format(perturbed_reasoning=row["perturbed"]).strip(),
            },
        ],
        max_tokens=4096,
    )

    print(completion.content[0].text)
    print("\n --------END---------- \n\n")
