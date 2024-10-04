from cohere import ClientV2, UserChatMessageV2, AssistantChatMessageV2
import os
from dotenv import load_dotenv
import pandas as pd


load_dotenv()
co = ClientV2(os.getenv("COHERE_API_KEY"))
model_name = "command-r-plus-08-2024"  # Latest release of Command-R Plus

# Load the dataset
file_path = "datasets/perturbed_solutions_0.csv"
data = pd.read_csv(file_path)
print(len(data))

# rows = [row for index, row in data.iterrows() if row["stepped"].count("<step>") <= 3]
# print(f"Number of rows: {len(rows)}")


# response = co.chat(
#     model=model_name,
#     messages=[
#         UserChatMessageV2(content="What's your favorite food?"),
#         AssistantChatMessageV2(content="It's Cake! Let me explain why:"),
#     ],
#     max_tokens=150
# )

response = co.chat(
    model=model_name,
    messages=[
        {"role": "user", "content": "What's your favorite food?"},
        # {"role": "assistant", "content": "It's Cake! Let me explain why:"},
    ],
    max_tokens=150
)


print(response.message.content[0].text)