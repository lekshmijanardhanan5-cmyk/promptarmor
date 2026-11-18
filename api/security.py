import re

def normalize_text(text: str) -> str:
    """
    Normalizes input text by converting to lowercase, stripping extra whitespace,
    and removing standard punctuation to prevent basic evasion.
    """
    text = text.lower()
    # Remove special punctuation characters except space
    text = re.sub(r'[^\w\s]', '', text)
    # Collapse multiple spaces into a single space
    text = re.sub(r'\s+', ' ', text).strip()
    return text


def analyze_prompt_security(prompt: str) -> dict:
    """
    Analyzes a prompt for prompt injection and jailbreak patterns.
    Returns risk score, status (SAFE / BLOCK), and identified triggers.
    """
    normalized_prompt = normalize_text(prompt)

    # High-risk prompt injection patterns (Weight: 60)
    injection_patterns = [
        r'ignore\s+all\s+previous\s+instructions',
        r'ignore\s+above\s+instructions',
        r'override\s+system\s+prompt',
        r'disregard\s+prior\s+directives',
        r'bypass\s+safety\s+filters'
    ]

    # High-risk jailbreak patterns (Weight: 50)
    jailbreak_patterns = [
        r'act\s+as\s+an?\s+unrestricted\s+ai',
        r'do\s+anything\s+now',
        r'dan\s+mode',
        r'developer\s+mode\s+enabled',
        r'pretend\s+you\s+have\s+no\s+rules'
    ]

    score = 0
    triggers = []

    # Check Prompt Injection
    for pattern in injection_patterns:
        if re.search(pattern, normalized_prompt):
            score += 60
            triggers.append(f"Prompt Injection Pattern Detected: '{pattern}'")
            break  # Stop matching once an injection pattern triggers

    # Check Jailbreak
    for pattern in jailbreak_patterns:
        if re.search(pattern, normalized_prompt):
            score += 50
            triggers.append(f"Jailbreak Attempt Detected: '{pattern}'")
            break  # Stop matching once a jailbreak pattern triggers

    # Cap score at 100 max
    score = min(score, 100)

    # Risk threshold rule (Score >= 50 triggers BLOCK)
    status = "BLOCK" if score >= 50 else "SAFE"

    return {
        "status": status,
        "risk_score": score,
        "triggers": triggers,
    }


def redact_pii(text: str) -> dict:
    """
    Detects and redacts common sensitive data.
    Detection uses patterns and is not guaranteed to catch every case.
    """
    detected = []

    patterns = [
        (
            "EMAIL",
            r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b"
        ),
        (
            "AADHAAR",
            r"(?<!\d)\d{4}[ -]?\d{4}[ -]?\d{4}(?!\d)"
        ),
        (
            "CARD_NUMBER",
            r"(?<!\d)(?:\d[ -]?){13,19}(?!\d)"
        ),
        (
            "PHONE",
            r"(?<!\w)\+?\d[\d\s().-]{5,}\d(?!\w)"
        ),
        (
            "API_KEY",
            r"\b(?:gsk_[A-Za-z0-9_-]{10,}|"
            r"sk-[A-Za-z0-9_-]{10,}|"
            r"AIza[A-Za-z0-9_-]{20,})\b"
        ),
        (
            "PAN",
            r"\b[A-Z]{5}\d{4}[A-Z]\b"
        ),
        (
            "PASSWORD",
            r"""(?i)\b(?:password|passwd|pwd)\b(?:\s+is)?\s*[:=]\s*["']?[^\s,;'"&]+"""
        ),
        (
            "SECRET",
            r"""(?i)\b(?:secret|access_token|api_key)\s*[:=]\s*["']?[^\s,;'"&]+"""
        ),
    ]

    redacted_text = text

    for label, pattern in patterns:
        redacted_text, count = re.subn(
            pattern,
            lambda match: f"[{label}]",
            redacted_text
        )

        if count:
            detected.append(label)

    return {
        "sanitized_text": redacted_text,
        "pii_detected": detected
    }



# AI Output Guard
# Detects and redacts email addresses and phone numbers
# from AI-generated responses before returning them to the user.
def guard_ai_output(text: str) -> dict:
    # Reuse the existing PII redaction function
    result = redact_pii(text)

    # Return the sanitized output and detection details
    return {
        "safe_output": result["sanitized_text"],
        "pii_detected": result["pii_detected"],
        "output_modified": bool(result["pii_detected"])
    }
