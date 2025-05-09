import os
import re
import ollama

# ========== HELPERS ==========

def strip_code_fences_and_comments(text):
    text = re.sub(r"^```(?:java)?\s*|```$", "", text.strip(), flags=re.MULTILINE).strip()
    lines = text.splitlines()
    return "\n".join(line for line in lines if not line.strip().startswith("//"))

def remove_flag_logic(content: str, flag_path: str, model: str) -> str:
    prompt = f"""
You are a Java code modifier. Strictly Do NOT add any comments and explanations.

The goal is to REMOVE any usage of the feature flag `{flag_path}` from the following code.

🧹 What to do:
- Remove ONLY the condition that checks `{flag_path}`.
- If the entire `if` condition is just `{flag_path}`, KEEP the `if` block and delete the `else` block.
- If the condition is `!{flag_path}`, KEEP the `else` block and delete the `if` block.
- If `{flag_path}` is part of a compound condition, remove it from the condition and preserve the rest.
- Do NOT remove unrelated code.
- Do not change any other code.
- Do NOT change any indentation and formatting.
- Do NOT add any extra lines or headers (e.g., "Here is your cleaned code").
- Do NOT add any comments and explanations.
- Do NOT wrap output in triple backticks or Markdown.

Here is the file:
{content}
"""

    response = ollama.chat(model=model, messages=[{"role": "user", "content": prompt}])
    return strip_code_fences_and_comments(response["message"]["content"])

def remove_flag_constant(content: str, flag_name: str, model: str) -> str:
    prompt = f"""
You are editing a Java constants file. Strictly Do NOT add any comments and explanations.

Delete the constant named `{flag_name}`.

- Only delete the line that declares it (e.g. public static final String ... = ...;).
- Do not change any other code.
- Do NOT change any indentation and formatting.
- DO NOT add any comments and explanations.
- Do NOT add any extra lines or headers (e.g., "Here is your cleaned code").
- Do not add any explanation and formatting.
- Return the cleaned code only — no Markdown or extra text.

Here is the file:
{content}
"""
    response = ollama.chat(model=model, messages=[{"role": "user", "content": prompt}])
    return strip_code_fences_and_comments(response["message"]["content"])

def remove_flag_from_list_reference(content: str, flag_path: str, model: str) -> str:
    prompt = f"""
You are editing a Java utility file. Strictly Do NOT add any comments and explanations.

The feature flag `{flag_path}` is deprecated.

🧹 Task:
- Find any `Arrays.asList(...)` or similar flag lists.
- Remove `{flag_path}` if it's present in the list and Do Not delete any other lines in the file.
- Keep the list declaration itself.
- Do not change any other code.
- Do NOT add any extra lines or headers (e.g., "Here is your cleaned code").
- Do NOT change any indentation and formatting.
- Do not alter unrelated code.
- Do not add any explanation and comments.
- Return only the updated Java code — no comments or Markdown.

Here is the file:
{content}
"""
    response = ollama.chat(model=model, messages=[{"role": "user", "content": prompt}])
    return strip_code_fences_and_comments(response["message"]["content"])

def is_constants_file(path: str) -> bool:
    name = os.path.basename(path)
    return "Constant" in name or "LDConstants" in name

def is_ldutil_file(path: str) -> bool:
    name = os.path.basename(path)
    return "LDUtil" in name

# ========== MAIN PROCESSING ==========

def process_java_file(file_path, flag_name, model):
    flag_path = f"LDConstants.{flag_name}"
    with open(file_path, "r", encoding="utf-8") as f:
        original = f.read()

    if flag_path not in original and flag_name not in original:
        return  # Skip

    print(f"🔧 Processing: {file_path}")

    try:
        if is_ldutil_file(file_path):
            cleaned = remove_flag_from_list_reference(original, flag_path, model)
        if is_constants_file(file_path):
            cleaned = remove_flag_constant(original, flag_name, model)
        else:
            cleaned = remove_flag_logic(original, flag_path, model)

        with open(file_path, "w", encoding="utf-8") as f:
            f.write(cleaned)

        print(f"✅ Updated: {file_path}")

    except Exception as e:
        print(f"❌ Failed to update {file_path}: {e}")

def scan_codebase(root_path, flag_name, model):
    for root, _, files in os.walk(root_path):
        for file in files:
            if file.endswith(".java"):
                full_path = os.path.join(root, file)
                process_java_file(full_path, flag_name, model)

# ========== ENTRY POINT ==========

if __name__ == "__main__":
    flag_name = input("🔍 Enter the feature flag name to remove (e.g., PW_ENABLE_USER_LOGIN_VALIDATION): ").strip()
    codebase_path = input("📁 Enter the root path to your Java codebase: ").strip()
    model = "mistral"

    print(f"\n🚀 Starting cleanup for flag `{flag_name}` in `{codebase_path}` using model `{model}`\n")
    scan_codebase(codebase_path, flag_name, model)
    print("\n🏁 Completed.\n")
