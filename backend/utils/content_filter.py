import re
from typing import Tuple


# Hindi/English harmful patterns
HARM_PATTERNS = [
    r"\b(chutiya|madarchod|randi|saali|kutiya)\b",
    r"b(c|bcchd|mc|mcchd)\b",
    r"\b(gandu|behenchod|lund|jhaat|chut)\b",
    r"\b(bastard|whore|slut)\b",
    r"\b(kill|murder|rape)\s+(all|every)\b",
    r"(usne|she)\s+(galti|fault)\s+(ki|kar)\b",  # Victim blaming
]

GRAPHIC_PATTERNS = [
    r"\b(chopped|gutted|ripped|decapitated)\b",
    r"\b(लटका|काट)\s+(दिया|कर)\b",
]


def is_content_safe(text: str) -> Tuple[bool, str]:
    text_lower = text.lower()
    
    for pattern in HARM_PATTERNS + GRAPHIC_PATTERNS:
        if re.search(pattern, text_lower):
            return False, "Contains harmful/inappropriate content"
    
    if len(text.strip()) < 10:
        return False, "Content too short"
    
    return True, ""
