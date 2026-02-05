
import re

def parse_custom_format(llm_output):
    # Regex to capture content between blocks
    # We use non-greedy matching .*? with DOTALL (s) to capture newlines

    target_pattern = r"<<<TARGET>>>\s*(.*?)\s*<<<DESCRIPTION>>>"
    desc_pattern = r"<<<DESCRIPTION>>>\s*(.*?)\s*<<<JAVASCRIPT>>>"
    js_pattern = r"<<<JAVASCRIPT>>>\s*(.*?)\s*<<<END>>>"

    target_match = re.search(target_pattern, llm_output, re.DOTALL)
    desc_match = re.search(desc_pattern, llm_output, re.DOTALL)
    js_match = re.search(js_pattern, llm_output, re.DOTALL)

    if target_match and desc_match and js_match:
        return {
            "target_id": target_match.group(1).strip(),
            "chart_description": desc_match.group(1).strip(),
            "javascript": js_match.group(1).strip()
        }
    return None

# Test cases
output1 = """
Here is the result:

<<<TARGET>>>
canvas_1
<<<DESCRIPTION>>>
This is a chart showing revenue.
<<<JAVASCRIPT>>>
const x = `hello world`;
new ApexCharts(document.querySelector("#canvas_1"), options);
<<<END>>>
"""

output2 = """
<<<TARGET>>>
AI_SUMMARY
<<<DESCRIPTION>>>
Summary text
<<<JAVASCRIPT>>>
document.getElementById('AI_SUMMARY').innerHTML = "Done";
<<<END>>>
"""

print("Test 1:", parse_custom_format(output1))
print("Test 2:", parse_custom_format(output2))
