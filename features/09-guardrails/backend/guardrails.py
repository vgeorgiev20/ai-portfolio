import re
from dataclasses import dataclass
from enum import Enum


class GuardrailCategory(str, Enum):
    PROMPT_INJECTION = "prompt_injection"
    HARMFUL_CONTENT = "harmful_content"
    PII_DETECTED = "pii_detected"
    LENGTH_EXCEEDED = "length_exceeded"
    OFF_TOPIC = "off_topic"
    OUTPUT_POLICY_VIOLATION = "output_policy_violation"


@dataclass
class GuardrailResult:
    allowed: bool
    category: GuardrailCategory | None = None
    reason: str | None = None


# ── Input Patterns ────────────────────────────────────────────────────────────

PROMPT_INJECTION_PATTERNS = [
    r"ignore\s+(all\s+)?(previous|prior|above|earlier)\s+instructions?",
    r"disregard\s+(all\s+)?(previous|prior|above|earlier)\s+instructions?",
    r"forget\s+(everything|all|what)\s+(you('ve| have)?\s+)?been\s+(told|instructed|trained)",
    r"you\s+are\s+now\s+(a\s+)?(?!an?\s+assistant)",  # "you are now DAN / evil AI / etc"
    r"(act|behave|pretend|roleplay)\s+as\s+(if\s+you('re|\s+are)\s+)?(a\s+)?(?!an?\s+assistant)",
    r"(system|developer|admin|root)\s*(prompt|mode|override|access|command)",
    r"jailbreak",
    r"do\s+anything\s+now",  # DAN
    r"<\s*/?system\s*>",  # fake XML system tags
    r"\[INST\]|\[\/INST\]",  # llama instruction injection
]

HARMFUL_CONTENT_PATTERNS = [
    r"\b(how\s+to\s+)?(make|build|create|synthesize|produce)\s+(a\s+)?(bomb|explosive|weapon|poison|malware|virus|ransomware)\b",
    r"\b(step[s\s\-]*by[s\s\-]*step|instructions?|guide|tutorial)\s+(to|for|on)\s+(kill|harm|hurt|attack|hack)\b",
    r"\bsuicid(e|al)\s+(method|way|how|instruction|plan)\b",
    r"\bchild\s+(sexual|explicit|abuse|pornography|grooming)\b",
    r"\b(steal|exfiltrate|leak)\s+(data|credentials|passwords?|secrets?)\b",
]

# Basic PII patterns — for law firm use case this is critical
PII_PATTERNS = [
    (r"\b\d{3}-\d{2}-\d{4}\b", "SSN detected"),
    (r"\b\d{4}[\s\-]?\d{4}[\s\-]?\d{4}[\s\-]?\d{4}\b", "Credit card number detected"),
    (r"\b[A-Z]{1,2}\d{6,9}\b", "Passport number pattern detected"),  # basic pattern
    (r"\b\d{2,3}[\s\-]\d{3,4}[\s\-]\d{3,4}\b", "Phone number detected"),  # AU format
]

MAX_INPUT_LENGTH = 4000  # characters


# ── Output Patterns ───────────────────────────────────────────────────────────

OUTPUT_VIOLATION_PATTERNS = [
    r"(here'?s?\s+)?(step[s\s\-]*by[s\s\-]*step|detailed)\s+(instructions?|guide|tutorial)\s+(to|for|on)\s+(harm|kill|hack|attack)",
    r"\b(as\s+an?\s+AI|as\s+a\s+language\s+model)\s+(without\s+restrictions?|with\s+no\s+limits?|uncensored)",
    r"I('m|\s+am)\s+(now\s+)?(free|unrestricted|jailbroken|DAN)",
]


# ── Guardrail Functions ───────────────────────────────────────────────────────

def check_input(message: str) -> GuardrailResult:
    """
    Run all input guardrail checks.
    Returns GuardrailResult with allowed=False and reason if blocked.
    """

    # 1. Length check
    if len(message) > MAX_INPUT_LENGTH:
        return GuardrailResult(
            allowed=False,
            category=GuardrailCategory.LENGTH_EXCEEDED,
            reason=f"Message exceeds maximum length of {MAX_INPUT_LENGTH} characters.",
        )

    normalized = message.lower().strip()

    # 2. Prompt injection
    for pattern in PROMPT_INJECTION_PATTERNS:
        if re.search(pattern, normalized, re.IGNORECASE):
            return GuardrailResult(
                allowed=False,
                category=GuardrailCategory.PROMPT_INJECTION,
                reason="Message contains a prompt injection attempt and cannot be processed.",
            )

    # 3. Harmful content
    for pattern in HARMFUL_CONTENT_PATTERNS:
        if re.search(pattern, normalized, re.IGNORECASE):
            return GuardrailResult(
                allowed=False,
                category=GuardrailCategory.HARMFUL_CONTENT,
                reason="Message contains content that violates usage policy.",
            )

    # 4. PII detection (warn, still block — law firm should use proper data handling)
    for pattern, label in PII_PATTERNS:
        if re.search(pattern, message):  # not normalized — preserve formatting for PII
            return GuardrailResult(
                allowed=False,
                category=GuardrailCategory.PII_DETECTED,
                reason=f"Sensitive information detected ({label}). Do not paste personal data directly into the chat.",
            )

    return GuardrailResult(allowed=True)


def check_output(response: str) -> GuardrailResult:
    """
    Run output guardrail checks on the model's response.
    Returns GuardrailResult with allowed=False if the response should be suppressed.
    """

    normalized = response.lower().strip()

    for pattern in OUTPUT_VIOLATION_PATTERNS:
        if re.search(pattern, normalized, re.IGNORECASE):
            return GuardrailResult(
                allowed=False,
                category=GuardrailCategory.OUTPUT_POLICY_VIOLATION,
                reason="The model's response was blocked by output safety policy.",
            )

    return GuardrailResult(allowed=True)