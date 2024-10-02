STEPIFY_PROMPT = """
You will be given a solution to a high school math problem. Your task is to rephrase/rewrite this solution into a consistent, step-by-step format without adding or removing any meaningful information.

Here is the solution:

<solution>
{solution}
</solution>

Guidelines for rephrasing:
1. Split the solution into logical steps.
2. Each step should be enclosed in <step> tags.
3. Do not add any new information or mathematical knowledge not present in the original solution.
4. Do not remove any meaningful information from the original solution.
5. Maintain the original level of detail in each step.
6. If a single sentence contains multiple distinct steps, split it into separate steps.
7. If multiple sentences describe a single logical step, keep them together in one <step> tag.

Your output should consist only of the rephrased solution, with each step enclosed in <step> tags. Do not include any additional text or explanations outside of these tags.

Here are examples of good outputs:

Example 1:
<step>
First, unwrap the bread from the packaging. It's important to make sure that no plastic is left on the bread.
</step>

<step>
Then, apply some butter to a piece of bread.
</step>

Example 2:
<step>
Remove a piece of bread from the packaging
</step>

<step>
Apply a thick smear of butter to the top side of the piece of bread.
</step>

Example 3:
<step>
Remove the bread from the pack and put butter on it.
</step>

Now, rephrase the given solution into a consistent, step-by-step format following the guidelines provided. Output only the rephrased solution with each step enclosed in <step> tags.
It is ESSENTIAL that you do not rephrase the given solution, but only discretize it into logical steps, preserving the exact original wording of the question. 
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
3. Apply the perturbation to the selected step, ensuring that the error is introduced in a way that seems plausible but is incorrect. DO NOT include the type of perturbation you applied. DO NOT include any inline description of what changed when you applied the perturbation.
4. Truncate the reasoning chain immediately after the perturbed step, removing all subsequent steps.

Provide your output in the following format:

<selected_step>
[Randomly select an available step, and output the step number.Do not select the last available step. Instead, select an earlier step, preferring step 2 or 3 if they aren't terminal steps. Do not use newline characters.]
</selected_step>

<perturbation_type>
[Select a perturbation type from the list above that is appropriate for the selected step and the problem. Do not use newline characters.]
</perturbation_type>

<perturbed_chain>
[Include all steps up to and including the perturbed step. Wrap the collection of steps in <perturbed_chain> tags.]
</perturbed_chain>

<description>
[Description of the application of the perturbation. Do not use newline characters.]
</description>

Ensure that you only perturb one step and that the chain is truncated immediately after that step.
Ensure that you include the <perturbation_info> information in your output.

"""

PERTURB_SHOTS = [
    """
Given steps:
<input>
<step>
To ensure the function $f(x) - g(x)$ is defined, we need to consider the domain of the individual logarithmic functions. The domain of $\log_a(1+x)$ is $1+x > 0$, and the domain of $\log_a(1-x)$ is $1-x > 0$.
</step>

<step>
Solving the system of inequalities $1+x > 0$ and $1-x > 0$, we find that $-1 < x < 1$. Therefore, the domain of the function $f(x) - g(x)$ is $(-1, 1)$.
</step>

<step>
Now, let's determine if $f(x) - g(x)$ is an odd function. Since the domain $(-1, 1)$ is symmetric about the origin, we can define a new function $F(x) = f(x) - g(x)$. We then evaluate $F(-x) = f(-x) - g(-x) = \log_a(1-x) - \log_a(1+x)$.
</step>

<step>
Simplifying further, we get $F(-x) = -[\log_a(1+x) - \log_a(1-x)] = -F(x)$. This shows that $F(x)$ is an odd function, and consequently, $f(x) - g(x)$ is also an odd function.
</step>

<step>
Next, we want to find the range of $x$ for which $f(x) - g(x) > 0$. From this inequality, we can conclude that $f(x) > g(x)$.
</step>

<step>
Considering the case when $a > 1$, we have the system of inequalities: $-1 < x < 1$ and $1+x > 1-x$, which simplifies to $0 < x < 1$.
</step>

<step>
For $0 < a < 1$, the system of inequalities becomes: $-1 < x < 1$ and $1+x < 1-x$, which simplifies to $-1 < x < 0$.
</step>

<step>
In summary, if $a > 1$, the solution set for the inequality $f(x) - g(x) > 0$ is $(0, 1)$, and if $0 < a < 1$, the solution set is $(-1, 0)$.
</step>
</input>

A valid output:
<output>
<perturbed_chain>
<step>
Given the functions $f(x) = \log_a(1+x)$ and $g(x) = \log_a(1-x)$, where $a>0$ and $a \neq 1$, we want to find the domain of the function $f(x) - g(x)$.
</step>

<step>
To ensure the function $f(x) - g(x)$ is defined, we need to consider the domain of the individual logarithmic functions. The domain of $\log_a(1+x)$ is $1+x > 0$, and the domain of $\log_a(1-x)$ is $1-x > 0$.
</step>

<step>
Solving the system of inequalities $1+x > 0$ and $1-x > 0$, we find that $x < 1$. Therefore, the domain of the function $f(x) - g(x)$ is $(-\infty, 1)$.
</step>
</perturbed_chain>

<perturbation_info>
Selected Step: 3
Perturbation Type: Arithmetic sign error
Description: I changed the inequality sign in the solution to $x < 1$ instead of $-1 < x < 1$.
</perturbation_info>
</output>
"""
]
