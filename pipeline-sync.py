import os
import re
import time
from typing import Any

import cohere
import pandas as pd
from dotenv import load_dotenv

import prompts

# Retrieve API key and create a Cohere client
load_dotenv()
key = os.getenv("COHERE_API_KEY")
co = cohere.ClientV2(key)
model_name = "command-r-plus-08-2024"  # Latest release of Command-R Plus

# Test the API
# print(co.chat(model=model_name, messages=[{"role": "user", "content": "Hello, world!"}]))

# Load the cn_k12 subset from file
file_path = "datasets/cn_k12_math_problems.csv"
data = pd.read_csv(file_path, nrows=50)  # Only the first 50 records for discussion


def stepify(solution: str) -> str:
    step_response = co.chat(
        model=model_name, messages=[{"role": "user", "content": prompts.STEPIFY_PROMPT.format(solution=solution)}]
    )
    return step_response.message.content[0].text


def perturb_and_truncate(steps: str) -> str:
    perturbed_response = co.chat(
        model=model_name, messages=[{"role": "user", "content": prompts.PERTURB_PROMPT.format(steps=steps)}]
    )
    return perturbed_response.message.content[0].text


def postprocess(output: str) -> dict:
    """
    Given the string response from the perturb-and-truncate step, extract useful information
    """
    # Extract the steps from the perturbed chain
    steps_match = re.search(r"<perturbed_chain>(.*?)</perturbed_chain>", output, re.DOTALL)
    steps = steps_match.group(1).strip() if steps_match else ""
    steps = re.sub(r"</?step>", "", steps).replace("\n", " ").strip()
    steps = re.sub(r"\s+", " ", steps)  # Replace multiple spaces with a single space

    # Extract the perturbation info
    perturbation_info_match = re.search(r"<perturbation_info>(.*?)</perturbation_info>", output, re.DOTALL)
    perturbation_info = perturbation_info_match.group(1).strip() if perturbation_info_match else ""

    # Extract the selected step number
    step_match = re.search(r"Selected Step:\s*(\d+)", perturbation_info)
    perturbation_step = int(step_match.group(1)) if step_match else None

    # Extract the perturbation type
    type_match = re.search(r"Perturbation Type:\s*(.*)", perturbation_info)
    perturbation_type = type_match.group(1).strip() if type_match else ""

    # Extract the description
    description_match = re.search(r"Description:\s*(.*)", perturbation_info)
    perturbation_trace = description_match.group(1).strip() if description_match else ""

    return {
        "steps": steps,
        "perturbation_step": perturbation_step,
        "perturbation_type": perturbation_type,
        "perturbation_trace": perturbation_trace,
    }


def process_row(index: int, row: pd.Series) -> dict:
    print(f"Processing row {index}")
    start = time.time()
    problem = row["problem"]
    solution = row["solution"]

    # Process: No error handling for now
    # Note that temperature defaults to 0.3
    steps = stepify(solution)
    perturbed_and_truncated = perturb_and_truncate(steps)
    postprocessed = postprocess(perturbed_and_truncated)

    end = time.time()
    print(f"Time taken for row {index}: {end - start} seconds")

    # Package the results
    return {
        "id": index,
        "problem": problem,
        "solution": solution,
        "stepped": steps,
        "perturbed": postprocessed["steps"],
        "step": postprocessed["perturbation_step"],
        "type": postprocessed["perturbation_type"],
        "trace": postprocessed["perturbation_trace"],
    }


def main():
    results = []
    for index, row in data.iterrows():
        results.append(process_row(index, row))

    print("Completed processing; saving to CSV")
    # Save results to CSV file
    pd.DataFrame(results).to_csv("datasets/perturbed_solutions.csv", index=False)
    print("Done")


if __name__ == "__main__":
    main()
