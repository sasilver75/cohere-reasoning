import os

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
file_path = "datasets/perturbed_solutions.csv"
data = pd.read_csv(file_path)

# Loop through the first 50 records and print them out
# TODO: Set temperature correctly?
for index, row in data[6:9].iterrows():
    print("\n ------------------ \n")
    # print(row["problem"], "\n", row["stepped"], "\n", row["perturbed"], "\n", row["type"], "\n", row["trace"], "\n",)
    print(
        f"""
    Question: {row["question"]} \n
    Answer: {row["solution"]} \n
    Stepped: {row["stepped"]} \n
    Perturbed: {row["perturbed"]} \n
    Step: {row["step"]} \n
    Type: {row["type"]} \n
    Trace: {row["trace"]} \n
    """
    )
    # print(prompts.COMPLETION_PROMPT.format(question=row["problem"], perturbed_reasoning=row["perturbed"]))
    print("\n\n")

    completion = client.messages.create(
        model="claude-3-5-sonnet-20240620",
        messages=[
            {
                "role": "user",
                "content": prompts.COMPLETION_PROMPT.format(
                    question=row["problem"], perturbed_reasoning=row["perturbed"]
                ),
            },
        ],
        max_tokens=4096,
    )

    print("COMPLETION: ", completion.content[0].text)
    print("\n ------------------ \n")
