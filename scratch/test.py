import re


def extract_specific_tag_content(text):
    # Define a regex pattern to match content between specific tags
    pattern = r"<(selected_step|perturbation_type|perturbed_chain|description)>(.*?)</\1>"

    # Find all matches in the text
    matches = re.findall(pattern, text, re.DOTALL)

    # Create a dictionary from the matches
    content_dict = {tag: content.strip() for tag, content in matches}

    return content_dict


# Example usage
text = """
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
"""

content = extract_specific_tag_content(text)
print(content)
