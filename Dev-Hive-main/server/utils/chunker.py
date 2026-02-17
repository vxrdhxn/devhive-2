import re

def chunk_text(text, max_tokens=300):
    # Simple sentence/paragraph-based chunking
    chunks = re.split(r'\n{2,}|\.\s+', text)
    result = []
    current = ""
    for chunk in chunks:
        if len(current + chunk) < max_tokens * 4:  # estimate 1 token ≈ 4 characters
            current += chunk + " "
        else:
            result.append(current.strip())
            current = chunk + " "
    if current:
        result.append(current.strip())
    return result
