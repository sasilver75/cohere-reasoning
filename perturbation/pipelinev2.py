import asyncio
import os
import random
import re
from typing import Any

import cohere
import httpx
import pandas as pd
import prompts
from dotenv import load_dotenv
from tqdm.asyncio import tqdm as atqdm
from tqdm.auto import tqdm

# Retrieve API key and create a Cohere client
load_dotenv()
co = cohere.AsyncClientV2(os.getenv("COHERE_API_KEY"))
model_name = "command-r-plus-08-2024"  # Latest release of Command-R Plus

# Test the API
# print(co.chat(model=model_name, messages=[{"role": "user", "content": "Hello, world!"}]))


async def stepify(solution: str, index: int) -> str:
    """
    Given a solution from the NuminaMath dataset, stepify it using Cohere's API.
    Using a timeout, because it seems like 5% of the time I get httpx ReadErrors after minutes of waiting.
    """
    try:
        step_response = await asyncio.wait_for(
            co.chat(
                model=model_name,
                messages=[{"role": "user", "content": prompts.STEPIFY_PROMPT.format(solution=solution)}],
                temperature=0,
            ),
            timeout=45,
        )
    except asyncio.TimeoutError as e:
        print(f"Timeout occurred while stepifying row {index}: {e}")
        raise e
    return step_response.message.content[0].text


async def perturb_and_truncate(steps: str, question: str, temperature: float, index: int) -> str:
    """
    Given a stepified solution from a previous step and a question,
    select a location in the stepified solution to perturb, a perturbation type, and apply the pertrubation, truncating the remaining solution.
    """
    try:
        perturbed_response = await asyncio.wait_for(
            co.chat(
                model=model_name,
                messages=[{"role": "user", "content": prompts.PERTURB_PROMPT.format(steps=steps, question=question)}],
                temperature=temperature,
            ),
            timeout=45,
        )
    except asyncio.TimeoutError as e:
        print(f"Timeout occurred while perturbing and truncating row {index}: {e}")
        raise e
    return perturbed_response.message.content[0].text


def postprocess(output: str) -> dict:
    """
    Given the string response from the perturb-and-truncate step, extract useful information
    TODO: With the changes to output format, is this still going to extract what I want?
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


async def process_row(df: pd.DataFrame, index: int, temperature: float, semaphore: asyncio.Semaphore) -> dict | None:
    """
    Given a dataframe and a row_id `index` to process
    Acquire semaphore access to limit concurrency, then process the row by stepifying and perturbing, with postprocessing.
    """

    row = df.iloc[index]
    question = row["problem"]
    solution = row["solution"]

    # Process: No error handling for now
    # Note that temperature defaults to 0.3
    # Acquire semaphore access (releasing when context manager exits)
    async with semaphore:
        print(f"Processing row {index}; semaphore: {semaphore._value}")
        try:
            steps = await stepify(solution, index)
            print(f"Stepped solution for row {index}")
            perturbed_and_truncated = await perturb_and_truncate(steps, question, temperature, index)
            print(f"Perturbed and truncated for row {index}")
            postprocessed = postprocess(perturbed_and_truncated)
            print(f"Postprocessed for row {index}")
        except Exception as e:
            print(f"Exception occurred processing row {index}: {e}")
            return None

    # Package the results
    result = {
        "id": index,
        "question": question,
        "solution": solution,
        "stepped": steps,
        "perturbed": postprocessed["steps"],
        "step": postprocessed["perturbation_step"],
        "type": postprocessed["perturbation_type"],
        "trace": postprocessed["perturbation_trace"],
    }
    print(f"Finished processing row {index}")
    return result


async def process_batch(df: pd.DataFrame, batch: list[int], batch_number: int, temperature: float) -> list:
    """
    Given a dataframe a list of ids that constitute a batch, process each row in the batch concurrently (limited by semaphore concurrency).
    """

    # Limit concurrency of processing to 15 tasks at a time
    semaphore = asyncio.Semaphore(15)

    # Create tasks for the asynchronous process each row
    tasks = [process_row(df, id, temperature, semaphore) for id in batch]

    results = []
    # Using tqdm.asyncio.tqdm to get a progress bar for each batch.
    for task in atqdm(asyncio.as_completed(tasks), total=len(tasks), desc=f"Batch {batch_number}"):
        # In the context of using asyncio.as_completed above, the tasks still run concurrenty, and this loop processes them as they complete.
        result = await task
        results.append(result)

    filtered = [result for result in results if result is not None]

    print(
        f"Of {len(results)} rows, {len(filtered)} were processed successfully ({len(results) - len(filtered)} failed)"
    )

    return filtered


async def process_data(
    df: pd.DataFrame, n: int, batch_size: int = 50, temperature: float = 0.3, max_concurrency: int = 20, timeout=45
) -> list:
    """
    Processes n rows from the cn_k12 dataset CSV file, using batch sizes of size bs when invoking Cohere APIs.
    """
    print("Processing data")

    all_results = []
    # Generate a list of indices for each batch
    for i in range(0, n, batch_size):
        batch_number = i // batch_size + 1
        batch = list(range(i, min(i + batch_size, n)))
        print(f"Processing batch for indices {batch}")
        # Give the data, the batch ids, and a the sempaphore that limits concurrency
        results = await process_batch(df, batch, batch_number, temperature)
        all_results.extend(results)
        print(
            f"Processed batch {i//batch_size + 1}/{(n + batch_size - 1)//batch_size}, total results: {len(all_results)}"
        )

    print("Finished processing all data")
    return all_results


async def main():
    # Load cn_k12 subset from file
    df = pd.read_csv("datasets/cn_k12_math_problems.csv", nrows=500)

    # Process up to the n'th row from the dataframe
    n = 100
    bs = 30
    max_concurrency = 20
    temperature = 0.3
    results = await process_data(df, n, batch_size=bs, temperature=temperature, max_concurrency=max_concurrency)

    print("Finished processing rows")
    return results


if __name__ == "__main__":
    asyncio.run(main())
