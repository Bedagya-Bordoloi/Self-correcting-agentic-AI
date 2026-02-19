def clean_json_string(s: str) -> str:
    """Helper to clean Markdown code blocks from JSON strings."""
    if "```json" in s:
        s = s.split("```json")[1].split("```")[0]
    elif "```" in s:
        s = s.split("```")[1].split("```")[0]
    return s.strip()