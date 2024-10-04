import os

import pandas as pd
from cohere import Client
from dotenv import load_dotenv

load_dotenv()
co = Client(os.getenv("COHERE_API_KEY"))
model_name = "command-r-plus-08-2024"  # Latest release of Command-R Plus

# # Load the dataset
# file_path = "datasets/perturbed_solutions_0.csv"
# data = pd.read_csv(file_path)
# print(len(data))

# response = co.chat(
#     model=model_name,
#     messages=[
#         {"role": "user", "content": "What's your favorite food?"},
#         # {"role": "assistant", "content": "It's Cake! Let me explain why:"},
#     ],
#     max_tokens=150
# )

p = """<BOS_TOKEN><|START_OF_TURN_TOKEN|><|SYSTEM_TOKEN|><|END_OF_TURN_TOKEN|><|START_OF_TURN_TOKEN|><|USER_TOKEN|>What's your favorite food?<|END_OF_TURN_TOKEN|><|START_OF_TURN_TOKEN|><|CHATBOT_TOKEN|>It's Cake! Let me <EOS_TOKEN>"""

co.chat(message=p, raw_prompting=True)
