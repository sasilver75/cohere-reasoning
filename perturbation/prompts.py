STEPIFY_PROMPT = """
You will be given a solution to a high school math problem. Your task is to rephrase/rewrite this solution into a consistent, step-by-step format without adding or removing any meaningful information.

Here is the solution:

<solution>
{solution}
</solution>

Guidelines for rephrasing:
1. Split the solution into logical steps.
2. Each step should be prefixed with a "Step X: " prefix, with X being the step number.
3. DO NOT add any new information or mathematical knowledge not present in the original solution.
4. DO NOT remove any meaningful information from the original solution.
5. Maintain the original level of detail in each step.
6. If a single sentence contains multiple distinct steps, split it into separate steps.
7. If multiple sentences describe a single logical step, keep them together in one step.

Your output should consist only of the rephrased solution, with each prefixed with a "Step X: " prefix, with X being the step number.
Do not include any additional text or explanations outside of these tags.

Here are 3 examples of good outputs:

<example>
Step 1: First, unwrap the bread from the packaging. It's important to make sure that no plastic is left on the bread.

Step 2:Then, apply some butter to a piece of bread.
</example>

<example>
Step 1:Remove a piece of bread from the packaging

Step 2: Apply a thick smear of butter to the top side of the piece of bread.

Step 3: Enjoy your delicious open-face butter sandwich!
</example>

<example>
Step 1:Remove the bread from the pack and put butter on it.
</example>

Now, rephrase the given solution into a consistent, step-by-step format following the guidelines provided. Output only the rephrased solution with each step prefixed by "Step X: ", with X being the step number.
It is ESSENTIAL that you do not rephrase the given solution, but only discretize it into logical steps, preserving the EXACT original wording of the solution. 
"""

PERTURB_PROMPT = """
Given the following question:
<question>
{question}
</question>

You are tasked with perturbing a mathematical reasoning chain and truncating it after the point of perturbation. Here's the reasoning chain you'll be working with:

<reasoning_chain>
{steps}
</reasoning_chain>

Your task is to:
1. Select a random step from the reasoning chain.
2. Apply an appropriate perturbation to that step.
3. Truncate the reasoning chain after the perturbed step.

Here are the possible perturbation types you can apply:

1. Numerical error: Incorrect calculation while maintaining correct logic
2. Misapplied formula: Using the right formula in the wrong context
3. Unit conversion mistake: Failing to convert units properly
4. Dropped negative sign: Forgetting to carry a negative sign through calculations
5. Confusing variables: Mixing up different variables in the problem
6. Arithmetic sign error: Using the wrong operation (e.g., + instead of ×)
7. Misused mathematical property: Incorrectly applying distributive/associative properties
8. Incorrect order of operations: Not following PEMDAS correctly
9. Algebraic manipulation error: Mistakes when rearranging or factoring equations
10. Geometric misconception: Misunderstanding relationships between shapes or angles


Instructions:
1. Randomly select a step from the reasoning chain.
2. Choose an appropriate perturbation type from the list above that fits the selected step.
3a. Apply the perturbation to the selected step, ensuring that the error is introduced in a way that seems plausible but is incorrect. DO NOT include the type of perturbation you applied. DO NOT include any inline description of what changed when you applied the perturbation.
3b. Truncate the reasoning chain immediately after the perturbed step, removing all subsequent steps.
4. Provide a description for the perturbation applied, explicitly noting what was changed.

Provide your output in the following format:

<output>

<selected_step>
[Randomly select an available step, and output the step number. Do not select the last available step. Instead, select an earlier step, preferring step 2 or 3 if they aren't terminal steps. Do not use newline characters.]
</selected_step>

<perturbation_type>
[Select a perturbation type from the list above that is appropriate for the selected step and the problem. Do not use newline characters.]
</perturbation_type>

<perturbed_chain>
[Include all steps up to and including the perturbed step. Wrap the collection of steps in <perturbed_chain></perturbed_chain> tags.]
</perturbed_chain>

<description>
[Description how the application was applied, explicitly noting what was changed. Do not use newline characters.]
</description>

</output>

Ensure that you remember to close your tags (eg </selected_step>, </perturbation_type>, </perturbed_chain>, </description>).
Ensure that you only perturb a single and that the chain is truncated immediately after that step.
Perturbation should be applied an early reasoning step (e.g. 2 or 3), and NOT a step that outputs the answer to the problem or one of its explicit subproblems.
"""
