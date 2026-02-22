import re


# ==================================================
# Bug Pattern Mapping
# ==================================================
BUG_PATTERNS = {
    r"unused import": "LINTING",
    r"SyntaxError": "SYNTAX",
    r"IndentationError": "INDENTATION",
    r"ModuleNotFoundError": "IMPORT",
    r"TypeError": "TYPE_ERROR",
    r"AssertionError": "LOGIC"
}


# ==================================================
# Extract File, Line, Message
# ==================================================
def extract_error_details(log_output):
    """
    Extract file name, line number, and error message
    from pytest output.
    """

    # --------------------------------------------------
    # 1️⃣ Handle pytest failure style:
    # test_sample.py:2: AssertionError
    # --------------------------------------------------
    pytest_pattern = r'([\w\/\.\-]+\.py):(\d+):\s*(AssertionError|SyntaxError|IndentationError|ModuleNotFoundError|TypeError)'

    match = re.search(pytest_pattern, log_output)
    if match:
        file_name = match.group(1)
        line_number = int(match.group(2))
        error_message = match.group(3)
        return file_name, line_number, error_message

    # --------------------------------------------------
    # 2️⃣ Handle SyntaxError during collection:
    # File "/app/test_sample.py", line 1
    # --------------------------------------------------
    syntax_pattern = r'File\s+"(.+?\.py)",\s+line\s+(\d+)'

    match = re.search(syntax_pattern, log_output)
    if match:
        file_path = match.group(1)
        file_name = file_path.replace("\\", "/").split("/")[-1]
        line_number = int(match.group(2))

        # Extract actual SyntaxError message
        error_match = re.search(r'SyntaxError:\s*(.+)', log_output)
        error_message = error_match.group(1) if error_match else "SyntaxError"

        return file_name, line_number, error_message

    # --------------------------------------------------
    # If nothing matched
    # --------------------------------------------------
    generic_file = re.search(r'([\w\/\.\-]+\.py)', log_output)
    if generic_file:
        return generic_file.group(1), None, "Unknown error"

    return None, None, None


# ==================================================
# Classify Bug Type
# ==================================================
def classify_bug(log_output):
    for pattern, bug_type in BUG_PATTERNS.items():
        if re.search(pattern, log_output, re.IGNORECASE):
            return bug_type
    return "UNKNOWN"


# ==================================================
# Main Parser Function
# ==================================================
def parse_failure(log_output):
    file_name, line_number, error_message = extract_error_details(log_output)
    bug_type = classify_bug(log_output)

    return {
        "file": file_name,
        "line": line_number,
        "bug_type": bug_type,
        "message": error_message
    }
