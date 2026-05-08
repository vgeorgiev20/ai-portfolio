from openai import AsyncOpenAI
from pydantic import BaseModel
from typing import Optional
import json
import os

# ── Models ────────────────────────────────────────────────────────────────────

class CodeIssue(BaseModel):
    severity: str           # "high" | "medium" | "low"
    line: Optional[int]     # line number if identifiable
    description: str        # what the issue is
    suggestion: str         # how to fix it


class CodeReviewResult(BaseModel):
    language: str           # detected language
    summary: str            # overall assessment
    score: int              # 1-10 quality score
    issues: list[CodeIssue]
    positives: list[str]    # what the code does well
    refactored_snippet: Optional[str]  # optional improved version of the worst part


# ── Prompt ────────────────────────────────────────────────────────────────────

SYSTEM_PROMPT = """You are a senior software engineer performing a code review.
Analyse the provided code and return a structured JSON review.

You MUST return ONLY valid JSON matching this exact structure, no markdown, no preamble:
{
  "language": "detected programming language",
  "summary": "2-3 sentence overall assessment",
  "score": <integer 1-10>,
  "issues": [
    {
      "severity": "high|medium|low",
      "line": <integer or null>,
      "description": "clear description of the issue",
      "suggestion": "concrete fix or improvement"
    }
  ],
  "positives": ["what the code does well"],
  "refactored_snippet": "optional improved version of the most critical section, or null"
}

Scoring guide:
1-3: Serious problems, not production ready
4-6: Functional but needs significant improvement  
7-8: Good code with minor issues
9-10: Excellent, production ready

Be specific, actionable, and constructive. Focus on:
- Security vulnerabilities
- Performance issues
- Code smells and maintainability
- Missing error handling
- Best practice violations"""


# ── Reviewer ─────────────────────────────────────────────────────────────────

async def review_code(code: str, context: Optional[str], client: AsyncOpenAI) -> CodeReviewResult:
    """
    Send code to the LLM and parse the structured review response.
    context: optional description of what the code is supposed to do
    """


    user_message = f"Review this code:\n\n```\n{code}\n```"
    if context:
        user_message += f"\n\nContext: {context}"

    completion = await client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_message},
        ],
        response_format={"type": "json_object"},  # enforce JSON mode
        temperature=0.2,  # low temperature for consistent structured output
    )

    raw = completion.choices[0].message.content or "{}"

    try:
        data = json.loads(raw)
        return CodeReviewResult(
            language=data.get("language", "unknown"),
            summary=data.get("summary", ""),
            score=int(data.get("score", 5)),
            issues=[CodeIssue(**i) for i in data.get("issues", [])],
            positives=data.get("positives", []),
            refactored_snippet=data.get("refactored_snippet"),
        )
    except (json.JSONDecodeError, KeyError, TypeError) as e:
        raise ValueError(f"Failed to parse LLM review response: {e}\nRaw: {raw}")