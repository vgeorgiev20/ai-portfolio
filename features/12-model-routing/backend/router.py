from pydantic import BaseModel
from typing import Optional
import re


# ── Models ────────────────────────────────────────────────────────────────────

class RoutingDecision(BaseModel):
    model: str
    tier: str           # "fast" | "smart"
    reason: str         # why this model was chosen
    estimated_cost: str # "low" | "medium" | "high"


# ── Model Tiers ───────────────────────────────────────────────────────────────

FAST_MODEL = "gpt-4.1-mini"    # cheap, fast, good for simple tasks
SMART_MODEL = "gpt-4.1"        # expensive, better reasoning for complex tasks


# ── Complexity Signals ────────────────────────────────────────────────────────

# Keywords that indicate a complex request needing the smart model
COMPLEX_SIGNALS = [
    # reasoning and analysis
    r"\b(explain|analyse|analyze|evaluate|compare|contrast|critique|assess)\b",
    r"\b(why|how does|what causes|what is the impact|what are the implications)\b",
    r"\b(pros and cons|trade.?offs?|advantages and disadvantages)\b",

    # code complexity
    r"\b(refactor|architect|design pattern|optimise|optimize|performance|scalability)\b",
    r"\b(debug|fix this|what is wrong|why (is|does) this (fail|break|not work))\b",

    # legal domain specific (law firm product)
    r"\b(summarise|summarize|draft|review|interpret|clause|liability|obligation|breach)\b",
    r"\b(contract|agreement|legal|law|regulation|compliance|jurisdiction)\b",

    # length signal — long messages are usually complex
]

# Keywords that indicate a simple request fine for the fast model
SIMPLE_SIGNALS = [
    r"\b(what is|what are|define|list|name|when|who)\b",
    r"\b(hello|hi|hey|thanks|thank you)\b",
    r"\b(yes|no|correct|wrong)\b",
]

# Code detection — always route to smart model
CODE_PATTERNS = [
    r"```[\w]*\n",          # fenced code block
    r"def |class |import |from \w+ import",  # Python
    r"public |private |void |static ",       # C#/Java
    r"function |const |let |var ",           # JavaScript
    r"SELECT |INSERT |UPDATE |DELETE ",      # SQL
]

COMPLEX_THRESHOLD = 150     # chars — messages longer than this lean complex
SMART_SCORE_THRESHOLD = 2   # how many complex signals needed to trigger smart model


# ── Router ────────────────────────────────────────────────────────────────────

def route(message: str, force_model: Optional[str] = None) -> RoutingDecision:
    """
    Analyse the message and decide which model to use.
    force_model: optional override — "fast" or "smart"
    """

    # Manual override
    if force_model == "smart":
        return RoutingDecision(
            model=SMART_MODEL,
            tier="smart",
            reason="Manually overridden to smart model.",
            estimated_cost="high",
        )
    if force_model == "fast":
        return RoutingDecision(
            model=FAST_MODEL,
            tier="fast",
            reason="Manually overridden to fast model.",
            estimated_cost="low",
        )

    normalized = message.lower().strip()
    score = 0
    reasons = []

    # 1. Code detection — always smart
    for pattern in CODE_PATTERNS:
        if re.search(pattern, message, re.IGNORECASE):
            return RoutingDecision(
                model=SMART_MODEL,
                tier="smart",
                reason="Code detected — routing to smart model for better reasoning.",
                estimated_cost="high",
            )

    # 2. Length signal
    if len(message) > COMPLEX_THRESHOLD:
        score += 1
        reasons.append("long message")

    # 3. Complex keyword signals
    for pattern in COMPLEX_SIGNALS:
        if re.search(pattern, normalized, re.IGNORECASE):
            score += 1
            reasons.append(f"complex keyword matched: {pattern}")
            break  # one match is enough to increment once

    # 4. Multiple complex signals
    complex_matches = sum(
        1 for p in COMPLEX_SIGNALS
        if re.search(p, normalized, re.IGNORECASE)
    )
    if complex_matches >= 2:
        score += 1
        reasons.append(f"{complex_matches} complexity signals detected")

    # 5. Simple signals reduce score
    for pattern in SIMPLE_SIGNALS:
        if re.search(pattern, normalized, re.IGNORECASE):
            score -= 1
            break

    # ── Decision ──────────────────────────────────────────────────────────────
    if score >= SMART_SCORE_THRESHOLD:
        return RoutingDecision(
            model=SMART_MODEL,
            tier="smart",
            reason=f"Complex request detected ({', '.join(reasons)}).",
            estimated_cost="high",
        )

    return RoutingDecision(
        model=FAST_MODEL,
        tier="fast",
        reason="Simple request — fast model is sufficient.",
        estimated_cost="low",
    )