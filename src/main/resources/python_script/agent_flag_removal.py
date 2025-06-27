import os
import re
import openai
from pathlib import Path
from typing import List, Dict
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Configure your OpenAI API key from environment variable
openai.api_key = os.getenv("OPENAI_API_KEY")
OPENAI_MODEL = "gpt-4o-mini"

OLLAMA_API_URL = "http://localhost:11434/api/generate"
OLLAMA_MODEL = "phi3:14b"  # Change to "llama3", "phi3", etc. if you prefer

class FeatureFlagRemover:
    def __init__(self, root_dir: str):
        self.root_dir = root_dir

    def find_constant_key(self, flag_value: str) -> str:
        constants_file = os.path.join(self.root_dir, 'main', 'java', 'com', 'launchdarkly', 'featureflag', 'util', 'LDConstants.java')
        if not os.path.exists(constants_file):
            print(f"Warning: Could not find LDConstants.java at {constants_file}")
            return flag_value
        try:
            with open(constants_file, 'r', encoding='utf-8') as f:
                content = f.read()
            pattern = rf'public\s+static\s+final\s+String\s+(\w+)\s*=\s*"{re.escape(flag_value)}"\s*;'
            match = re.search(pattern, content)
            if match:
                return match.group(1)
        except Exception as e:
            print(f"Error reading {constants_file}: {e}")
        return flag_value


    def find_files_containing_flag(self, flag_name: str) -> List[str]:
        flag_files = set()
        constant_key = self.find_constant_key(flag_name)
        patterns = [re.escape(flag_name)]
        if constant_key != flag_name:
            patterns.append(re.escape(constant_key))
            print(f"Found constant key '{constant_key}' for flag value '{flag_name}'")
        pattern = re.compile('|'.join(patterns))
        for root, _, files in os.walk(self.root_dir):
            for file in files:
                if file.endswith(('.java', '.jsp', '.js')):
                    file_path = os.path.join(root, file)
                    try:
                        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                            if pattern.search(f.read()):
                                flag_files.add(file_path)
                    except Exception as e:
                        print(f"Error reading {file_path}: {e}")
        return sorted(list(flag_files))

    def get_file_content(self, file_path: str) -> str:
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return f.read()
        except Exception as e:
            print(f"Error reading file {file_path}: {e}")
            return ""

    def analyze_file(self, file_path: str, flag_name: str) -> Dict:
        content = self.get_file_content(file_path)
        if not content:
            return {"file": file_path, "changes": [], "error": "Could not read file"}
        constant_key = self.find_constant_key(flag_name)
        prompt = (
            f"Remove all usages of the feature flag '{flag_name}' (constant '{constant_key}') from the following file.\n"
            f"Handle all the following scenarios:\n"
            f"- For any condition like if ({flag_name}) {{ ... }} else {{ ... }} or if ({constant_key}) {{ ... }} else {{ ... }}, keep only the code inside the if block and remove the else block.\n"
            f"- For any condition like if (!{flag_name}) {{ ... }} else {{ ... }} or if (!{constant_key}) {{ ... }} else {{ ... }}, keep only the code inside the else block and remove the if block.\n"
            f"- For any single-branch if ({flag_name}) {{ ... }} or if ({constant_key}) {{ ... }}, keep the block.\n"
            f"- For any single-branch if (!{flag_name}) {{ ... }} or if (!{constant_key}) {{ ... }}, remove the block entirely.\n"
            f"- Remove all direct and indirect usages of this flag, including checks in utility methods (e.g., LDUtil.getFlagStatusBySystemIdDefaultFalse(..., {constant_key})), service calls (e.g., featureFlagService.isEnabled(\"{flag_name}\")), and any other patterns where this flag is checked, assigned, or used.\n"
            f"- DO NOT remove or modify any other feature flag checks.\n"
            f"- Do NOT add any comments or explanations about what was removed.\n"
            f"- Do NOT add any placeholder comments, such as <!-- removed ... --> or // removed ....\n"
            f"- Preserve the original formatting, indentation, and blank lines as much as possible.\n"
            f"- Do not add or remove extra blank lines or spaces.\n"
            f"- For any condition like if (!{flag_name}) {{ ... }} return ...; else return ...;, keep only the code inside the else block and remove the if block. For any condition like if ({flag_name}) {{ ... }} return ...; else return ...;, keep only the code inside the if block and remove the else block.\n"
            f"- For any condition like if (!{flag_name}) {{ ... }} ...; else ...;, keep only the code inside the else block and remove the if block. For any condition like if ({flag_name}) {{ ... }} ...; else ...;, keep only the code inside the if block and remove the else block.\n"
            f"Only return the updated file content, as valid code, with no extra comments, explanations, or markdown.\n"
            f"Return ONLY the full, updated file content, and nothing else.\n"
            f"File: {file_path}\n"
            "```\n"
            f"{content}\n"
            "```"
        )
        try:
            response = openai.ChatCompletion.create(
                model=OPENAI_MODEL,
                messages=[
                    {"role": "system", "content": "You are an AI assistant that helps remove feature flags from code. Respond only with the updated code file as instructed."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.2,
                max_tokens=3000
            )
            analysis = response.choices[0].message.content
            new_content = self._extract_new_file_content(analysis)
            return {
                "file": file_path,
                "new_content": new_content,
                "analysis": analysis
            }
        except Exception as e:
            return {"file": file_path, "error": f"API Error: {str(e)}"}

    def ollama_analyze_file(self, file_path: str, flag_name: str) -> Dict:
        content = self.get_file_content(file_path)
        if not content:
            return {"file": file_path, "changes": [], "error": "Could not read file"}
        constant_key = self.find_constant_key(flag_name)
        prompt = (
            f"Remove all usages of the feature flag '{flag_name}' (constant '{constant_key}') from the following file. "
            f"DO NOT remove or modify any other feature flag checks. "
            f"Do NOT add any comments or explanations about what was removed. "
            f"Do NOT add any placeholder comments, such as <!-- removed ... --> or // removed .... "
            f"Preserve the original formatting, indentation, and blank lines as much as possible. "
            f"Do not add or remove extra blank lines or spaces. "
            f"Only return the updated file content, as valid code, with no extra comments, explanations, or markdown.\n"
            f"Return ONLY the full, updated file content, and nothing else.\n"
            f"File: {file_path}\n"
            "```\n"
            f"{content}\n"
            "```"
        )
        try:
            data = {
                "model": OLLAMA_MODEL,
                "prompt": prompt,
                "stream": False
            }
            response = requests.post(OLLAMA_API_URL, json=data, timeout=540)
            response.raise_for_status()
            result = response.json()
            analysis = result.get('response', '')
            new_content = self._extract_new_file_content(analysis)
            return {
                "file": file_path,
                "new_content": new_content,
                "analysis": analysis
            }
        except Exception as e:
            return {"file": file_path, "error": f"Ollama API Error: {str(e)}"}

    def _extract_new_file_content(self, analysis: str) -> str:
        """Extract only the code inside the first code block, ignoring explanations and markdown."""
        # Try to extract from ```java ... ``` or generic triple-backtick blocks
        match = re.search(r'```(?:java)?\s*\n(.*?)\n```', analysis, re.DOTALL)
        if match:
            return match.group(1).strip()
        # fallback: if no code block, return the whole response (not recommended)
        return analysis.strip()

    def apply_changes(self, file_path: str, new_content: str) -> bool:
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                old_content = f.read()
            # Clean trailing whitespace and ensure exactly one newline at EOF
            cleaned_content = new_content.rstrip() + '\n'
            if old_content.strip() == cleaned_content.strip():
                print(f"No changes needed for {file_path}")
                return False
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(cleaned_content)
            print(f"Updated {file_path}")
            return True
        except Exception as e:
            print(f"Error writing to {file_path}: {e}")
            return False

def main():
    print("=== Feature Flag Removal Assistant ===\n")
    model = "openai" # "ollama"
    root_dir = input("Enter the root directory to search (or press Enter for current directory): ").strip()
    if not root_dir:
        root_dir = os.getcwd()
    flag_name = input("\nEnter the feature flag name to remove (e.g., 'pw_enable_user_login_validation'): ").strip()
    if not flag_name:
        print("Error: Flag name is required")
        return
    remover = FeatureFlagRemover(root_dir)
    print(f"\nSearching for flag '{flag_name}' in {root_dir}...")
    files = remover.find_files_containing_flag(flag_name)
    if not files:
        print("No files found containing the flag.")
        return
    print(f"\nFound {len(files)} files containing the flag:")
    for i, file in enumerate(files, 1):
        print(f"{i}. {file}")
    print("\nAnalyzing files...")
    for file in files:
        print(f"\nAnalyzing {file}...")
        if model == "ollama":
            result = remover.ollama_analyze_file(file, flag_name)
        else:
            result = remover.analyze_file(file, flag_name)
        if "new_content" in result and result["new_content"]:
            # print("\nProposed new content (truncated):")
            # print(result["new_content"][:500] + "...\n" if len(result["new_content"]) > 500 else result["new_content"])
            remover.apply_changes(file, result["new_content"])
        else:
            print(f"Error analyzing {file}: {result.get('error', 'Unknown error')}")

    print("\nProcess completed. Please review all changes before committing.")

if __name__ == "__main__":
    main()