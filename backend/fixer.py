import os
import re
import subprocess

from openai import OpenAI

# ==================================================
# Helper Functions
# ==================================================
def read_file(file_path):
    with open(file_path, "r", encoding="utf-8") as f:
        return f.readlines()


def write_file(file_path, lines):
    with open(file_path, "w", encoding="utf-8") as f:
        f.writelines(lines)


# ==================================================
# ---------------- DETERMINISTIC FIXES ------------
# ==================================================
def fix_linting(file_path, line_number):
    lines = read_file(file_path)
    if line_number and 0 < line_number <= len(lines):
        lines.pop(line_number - 1)
        write_file(file_path, lines)
        return True
    return False


def fix_syntax(file_path, line_number):
    lines = read_file(file_path)
    if line_number and 0 < line_number <= len(lines):
        if not lines[line_number - 1].strip().endswith(":"):
            lines[line_number - 1] = lines[line_number - 1].rstrip() + ":\n"
            write_file(file_path, lines)
            return True
    return False


def fix_indentation(file_path):
    try:
        process = subprocess.run(
            ["autopep8", "--in-place", file_path],
            capture_output=True,
            text=True,
            check=False,
        )
        return process.returncode == 0
    except FileNotFoundError:
        return False


def fix_import(file_path, message):
    if message and "No module named" in message:
        try:
            module_name = message.split("'")[1]
        except IndexError:
            return

        lines = read_file(file_path)
        import_statement = f"import {module_name}\n"

        if import_statement not in lines:
            lines.insert(0, import_statement)
            write_file(file_path, lines)
            return True
    return False


def _extract_code_block(text):
    if not text:
        return ""
    code_block = re.search(r"```(?:python)?\n(.*?)```", text, re.DOTALL)
    if code_block:
        return code_block.group(1).strip() + "\n"
    return text.strip() + "\n"


def fix_logic_with_llm(file_path, line_number, message):
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        return False

    lines = read_file(file_path)
    idx = (line_number - 1) if line_number and line_number > 0 else 0
    start = max(0, idx - 10)
    end = min(len(lines), idx + 10)
    context = "".join(lines[start:end])

    prompt = (
        "You are a code repair agent.\n\n"
        "Fix ONLY this bug:\n\n"
        f"File: {os.path.basename(file_path)}\n"
        f"Line: {line_number}\n"
        f"Error: {message}\n"
        "Code context:\n"
        f"{context}\n\n"
        "Return ONLY corrected code.\n"
        "No explanation."
    )

    try:
        client = OpenAI(api_key=api_key)
        response = client.responses.create(
            model=os.getenv("OPENAI_MODEL", "gpt-4.1-mini"),
            input=prompt,
        )
        output = getattr(response, "output_text", "")
        fixed_code = _extract_code_block(output)
        if not fixed_code.strip():
            return False
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(fixed_code)
        return True
    except Exception:
        return False


def apply_deterministic_fix(repo_path, failure_details):
    file_name = failure_details.get("file")
    line = failure_details.get("line")
    bug_type = failure_details.get("bug_type")
    message = failure_details.get("message")

    if not file_name:
        return False

    file_path = os.path.join(repo_path, file_name)

    if not os.path.exists(file_path):
        return False

    if bug_type == "LINTING":
        return fix_linting(file_path, line)

    elif bug_type == "SYNTAX":
        return fix_syntax(file_path, line)

    elif bug_type == "INDENTATION":
        return fix_indentation(file_path)

    elif bug_type == "IMPORT":
        return fix_import(file_path, message)

    else:
        return False


# ==================================================
# Master Fix Controller
# ==================================================
def apply_fix(repo_path, failure_details):

    bug_type = failure_details.get("bug_type")

    # 1) Deterministic fixes
    if bug_type in ["LINTING", "SYNTAX", "INDENTATION", "IMPORT"]:
        return apply_deterministic_fix(repo_path, failure_details)

    # 2) LLM-backed fix for logic errors
    if bug_type == "LOGIC":
        file_name = failure_details.get("file")
        line = failure_details.get("line")
        message = failure_details.get("message", "")
        if not file_name:
            return False
        file_path = os.path.join(repo_path, file_name)
        if not os.path.exists(file_path):
            return False
        return fix_logic_with_llm(file_path, line, message)

    return False
