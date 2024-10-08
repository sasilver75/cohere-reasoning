import os

import pandas as pd
import prompts
from cohere import Client
from dotenv import load_dotenv
from tqdm import tqdm

load_dotenv()
co = Client(os.getenv("COHERE_API_KEY"))
model_name = "command-r-plus-08-2024"  # Latest release of Command-R Plus

filepath = "datasets/perturbed_solutions_0.csv"
data = pd.read_csv(filepath)


def print_row_information(row: pd.Series):
    print("~~~Row Information~~~")
    print(f"ID: {row['id']}")
    print(f"Question: {row['question']}")
    print(f"Stepped Answer: {row['stepped']}")
    print(f"Type: {row['type']}")
    print(f"Step: {row['step']}")
    print(f"Trace: {row['trace']}")
    print(f"Perturbed: {row['perturbed']}")
    print("~~~End of Row Information~~~")


def get_row_completion(row: pd.Series):
    user_turn = prompts.COMPLETION_PROMPT_V2_USER.format(question=row["question"])
    assistant_turn = prompts.COMPLETION_PROMPT_V2_ASSISTANT.format(perturbed_reasoning=row["perturbed"])
    print(f"\n\n User propmt: {user_turn}\n\n Assistant prompt: {assistant_turn}\n\n")
    completion = co.chat(
        message=prompts.RAW_COMPLETION_TEMPLATE.format(user_turn=user_turn, assitant_turn=assistant_turn),
        raw_prompting=True,
    )
    print(f"\n\n Completion: {completion.text}\n\n")
    return completion.text


completions = []
data.head()
from tqdm import tqdm

for index, row in tqdm(data[0:10].iterrows(), total=len(data), desc="Processing rows"):
    print("------------------Row------------------")
    print_row_information(row)
    completions.append(get_row_completion(row))
    print("------------------End of Row------------------")

data["completion"] = completions

data.to_csv("datasets/perturbed_solutions_0_completions_command_r.csv", index=False)
