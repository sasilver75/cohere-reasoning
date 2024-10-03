import asyncio
import os
import re
from typing import Optional

import cohere
import pandas as pd
import prompts
from dotenv import load_dotenv
from tqdm.asyncio import tqdm as atqdm

# Retrieve API key and create a Cohere client
load_dotenv()
co = cohere.AsyncClientV2(os.getenv("COHERE_API_KEY"))
model_name = "command-r-plus-08-2024"  # Latest release of Command-R Plus


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


def postprocess(output: str) -> dict[str, Optional[str | int]]:
    """
    Given the string response from the perturb-and-truncate step, extract useful information
    """
    # Extract the steps from the perturbed chain
    steps_match = re.search(r"<perturbed_chain>(.*?)</perturbed_chain>", output, re.DOTALL)
    steps = steps_match.group(1).strip() if steps_match else None
    if steps is not None:
        steps = re.sub(r"\s+", " ", steps)  # Replace multiple spaces with a single space

    # Extract the selected step number
    step_match = re.search(r"<selected_step>(.*?)</selected_step>", output, re.DOTALL)
    perturbation_step = int(step_match.group(1).strip()) if step_match else None

    # Extract the perturbation type
    type_match = re.search(r"<perturbation_type>(.*?)</perturbation_type>", output, re.DOTALL)
    perturbation_type = type_match.group(1).strip() if type_match else None

    # Extract the description
    description_match = re.search(r"<description>(.*?)</description>", output, re.DOTALL)
    perturbation_trace = description_match.group(1).strip() if description_match else None

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
    id = int(row["index"])
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
            print(f"Exception occurred processing row {index}: {type(e)}: {e}")
            return None

    if any(val == None for val in postprocessed.values()):
        missing = [k for k, v in postprocessed.items() if v is None]
        print(f"Row {index} was not postprocessed successfully; failure to extract {missing}")
        return None

    # Package the results
    result = {
        "id": id,
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

    n_fails = len(results) - len(filtered)
    print(
        f"Of {len(results)} rows in batch {batch_number}, {len(filtered)} were processed successfully ({n_fails} failed)"
    )

    return filtered, n_fails


async def process_data(df: pd.DataFrame, n: int, batch_size: int = 50, temperature: float = 0.3) -> list[dict]:
    """
    Processes n rows from the cn_k12 dataset CSV file, using batch sizes of size bs when invoking Cohere APIs.
    """
    print("Processing data")

    all_results = []
    total_failed = 0
    # Generate a list of indices for each batch
    for i in range(0, n, batch_size):
        batch_number = i // batch_size + 1
        batch = list(range(i, min(i + batch_size, n)))
        print(f"Processing batch for indices {batch}")
        # Give the data, the batch ids, and a the sempaphore that limits concurrency
        results, n_fail = await process_batch(df, batch, batch_number, temperature)
        all_results.extend(results)
        total_failed += n_fail
        print(
            f"Processed batch {i//batch_size + 1}/{(n + batch_size - 1)//batch_size}, total results: {len(all_results)}"
        )

    print(f"Finished processing all data, with {total_failed} failures out of {min(len(df), n)} records")
    return all_results


async def main():
    # TODO: Right now, batching is just a cosmetic thing, since the concurrency is limited to 15 by the asyncio.semaphore anyways.

    # Process up to the n'th row from the dataframe. Works just fine if n//bs!=0, or if bs>=n
    input_filename = "datasets/cn_k12_math_problems.csv"
    n = 50
    bs = 50
    for temperature, label in [
        (0, "0"),
        # (0.3, "3"),
        # (0.6, "6"),
    ]:
        # Load cn_k12 subset from file
        df = pd.read_csv(input_filename, nrows=500)

        # Processs and perturb data
        processed = await process_data(df, n, batch_size=bs, temperature=temperature)

        # Save results to CSV
        output_filename = f"datasets/perturbed_solutions_{label}.csv"
        print(f"Finished processing rows; saving {len(processed)} rows to {output_filename}")
        pd.DataFrame(processed).sort_values(by="id").to_csv(output_filename, index=False)


if __name__ == "__main__":
    asyncio.run(main())
