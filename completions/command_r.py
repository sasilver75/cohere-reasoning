import os

from cohere import Client
from dotenv import load_dotenv

load_dotenv()
co = Client(os.getenv("COHERE_API_KEY"))
model_name = "command-r-plus-08-2024"  # Latest release of Command-R Plus

p = """<BOS_TOKEN><|START_OF_TURN_TOKEN|><|SYSTEM_TOKEN|><|END_OF_TURN_TOKEN|><|START_OF_TURN_TOKEN|><|USER_TOKEN|>What's your favorite food?<|END_OF_TURN_TOKEN|><|START_OF_TURN_TOKEN|><|CHATBOT_TOKEN|>It's Cake! Let me"""

co.chat(message=p, raw_prompting=True)
