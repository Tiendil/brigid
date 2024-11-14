def capitalize_first(text: str) -> str:
    if not text:
        return text

    return text[0].capitalize() + text[1:]
