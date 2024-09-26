import os
import re
from typing import Any

import cohere
import pandas as pd
from dotenv import load_dotenv

import datasets
import prompts

# Retrieve API key and create a Cohere client
load_dotenv()
key = os.getenv("COHERE_API_KEY")
co = cohere.ClientV2(key)
model_name = "command-r-plus-08-2024"

# Test the API
print(co.chat(model=model_name, messages=[{"role": "user", "content": "Hello, world!"}]))
