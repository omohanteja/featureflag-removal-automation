import ollama
import os
import re

def remove_flag_condition(code_snippet, flag_key):
    prompt = f"""
    Strictly **remove all instances** of the feature flag '{flag_key}' from the following Java code.
    
    ✅ DELETE the entire `if` condition checking the flag, along with its code block.  
    ✅ Preserve all other logic, including methods, class definitions, and imports.  
    ❌ DO NOT add explanations, summaries, or format the output using markdown (` ```java `).  
    ❌ DO NOT leave empty brackets `{{}}` behind after flag removal.  
    ❌ Return **only the cleaned Java code**, properly formatted.

    Code:
    {code_snippet}
    """

    response = ollama.chat(model="gemma3:1b", messages=[{"role": "user", "content": prompt}])
    cleaned_code = response["message"]["content"]

    # Ensure Ollama doesn't add markdown formatting
    cleaned_code = cleaned_code.replace("```java", "").replace("```", "").strip()

    return cleaned_code

def process_java_files(directory, flag_key):
    if not os.path.exists(directory):
        print(f"Error: Directory '{directory}' does not exist.")
        return
    
    for root, _, files in os.walk(directory):
        for file in files:
            if file.endswith(".java"):
                filepath = os.path.join(root, file)
                with open(filepath, "r") as f:
                    code = f.read()

                modified_code = remove_flag_condition(code, flag_key)

                # Clean up stray empty brackets `{}` left behind
                modified_code = re.sub(r"\s*\{\s*\}\s*", "", modified_code)

                with open(filepath, "w") as f:
                    f.write(modified_code)

                print(f"✅ Feature flag '{flag_key}' successfully removed from: {filepath}")


# Get feature flag key and project path dynamically from user input
project_path = input("Enter the path to your Java project directory: ").strip()
flag_key = input("Enter the feature flag key to remove: ").strip()

process_java_files(project_path, flag_key)
