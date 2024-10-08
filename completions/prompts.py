COMPLETION_PROMPT = """
You are a mathematical problem-solving assistant. You will be presented with a mathematical problem and a partial reasoning trajectory. Your task is to continue the reasoning from where it left off and solve the problem.

Here's the mathematical problem:

<question>
{question}
</question>

Here's the partial reasoning trajectory:

<reasoning> 
{perturbed_reasoning}
</reasoning>

Please continue the reasoning from where it left off. You should pick up exactly where the reasoning ended and proceed step-by-step towards correctly solving the problem. 

Once you've completed your reasoning, provide the final answer to the problem.

Present your continued reasoning and final answer in the following format:

<continued_reasoning>
[Your step-by-step continuation of the reasoning]
</continued_reasoning>

<final_answer>
[Your final answer to the problem]
</final_answer>
"""

COMPLETION_PROMPT_V2_USER = """
{question}

Please solve this problem step-by-step, presenting the final answer in <answer></answer> tags.
"""

COMPLETION_PROMPT_V2_ASSISTANT = """
Certainly. Here is the step-by-step reasoning and final answer to the problem:

{perturbed_reasoning}
"""

RAW_COMPLETION_TEMPLATE = """<BOS_TOKEN><|START_OF_TURN_TOKEN|><|SYSTEM_TOKEN|><|END_OF_TURN_TOKEN|><|START_OF_TURN_TOKEN|><|USER_TOKEN|>{user_turn}<|END_OF_TURN_TOKEN|><|START_OF_TURN_TOKEN|><|CHATBOT_TOKEN|>{assitant_turn}"""
