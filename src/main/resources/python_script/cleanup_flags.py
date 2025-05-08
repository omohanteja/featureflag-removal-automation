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
You are editing a Java file.

The feature flag `{flag_path}` is always ENABLED.

🧹 Task:
- Remove the IF condition that checks the flag: `{flag_path}`.
- Delete its ELSE block entirely.
- Keep all code inside the IF block.
- DO NOT modify the package declaration or any unrelated code.
- DO NOT add any comments or explanations.
- Return the cleaned code only — no Markdown or extra text.

Here is the code:
{content}
"""
    response = ollama.chat(model=model, messages=[{"role": "user", "content": prompt}])
    return strip_code_fences_and_comments(response["message"]["content"])

def remove_flag_constant(content: str, flag_name: str, model: str) -> str:
    prompt = f"""
You are editing a Java constants file.

Delete the constant named `{flag_name}`.

- Only delete the line that declares it (e.g. public static final String ... = ...;).
- Do not change any other code.
- Do not add any explanation or formatting.

Here is the file:
{content}
"""
    response = ollama.chat(model=model, messages=[{"role": "user", "content": prompt}])
    return strip_code_fences_and_comments(response["message"]["content"])

def is_constants_file(path: str) -> bool:
    name = os.path.basename(path)
    return "Constant" in name or "LDConstants" in name

# ========== MAIN PROCESSING ==========

def process_java_file(file_path, flag_name, model):
    flag_path = f"LDConstants.{flag_name}"
    with open(file_path, "r", encoding="utf-8") as f:
        original = f.read()

    if flag_path not in original and flag_name not in original:
        return  # Skip

    print(f"🔧 Processing: {file_path}")

    try:
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
    model = "codellama:7b"

    print(f"\n🚀 Starting cleanup for flag `{flag_name}` in `{codebase_path}` using model `{model}`\n")
    scan_codebase(codebase_path, flag_name, model)
    print("\n🏁 Completed.\n")