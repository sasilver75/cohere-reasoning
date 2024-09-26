import os

import pandas as pd
from datasets import load_dataset
import cohere
from dotenv import load_dotenv

# Retrieve your API key from environment variables, and create a Cohere client
load_dotenv()
key = os.getenv("COHERE_API_KEY")
co = cohere.Client(key)
print("API Key Valid" if co.chat(message="Hello, world!").text else "API Key Invalid")

# Let's load our dataframe
file_path = "datasets/cn_k12_math_problems.csv"
if os.path.exists(file_path):
    print("Loading cn_k12 from local file...")
    df = pd.read_csv(file_path)
else:
    print("Downloading cn_k12 from Hugging Face, processing, and saving locally...")
    # Download the 859594-record (859494 train, 100 test) NuminaMath-CoT Dataset from HF
    # This dataset contains math problems with solutiosn formulated in a CoT fashion
    # Sources range from Chinese high-school math to IMO problems
    # The "cn_k12" Chinese high-school subset contains the 276591 records we'll use

    dataset_name = "AI-MO/NuminaMath-CoT"
    dataset = load_dataset(dataset_name)

    # Combine the train/test splits, with a new column indicating original split
    train_df = pd.DataFrame(dataset["train"])
    test_df = pd.DataFrame(dataset["test"])
    train_df["set"] = "train"
    test_df["set"] = "test"
    df = pd.concat([train_df, test_df])
    df = df[df["source"] == "cn_k12"]

    # Now that we've downloaded and formatted the datset, let's save it locally.
    df.to_csv(file_path, index=False)
print("Loaded cn_k12 dataset")


# Filter to only the cn_k12 subset
questions = df["problem"]
print(questions.head())
