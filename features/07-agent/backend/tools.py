import math
import re
from datetime import datetime, timezone
import time
from duckduckgo_search import DDGS
from typing import Any


# ── Tool Definitions (OpenAI function calling schema) ─────────────────────────

TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "web_search",
            "description": "Search the web for current information. Use this when you need up-to-date facts, news, prices, or any information that may have changed recently.",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "The search query. Be specific and concise."
                    }
                },
                "required": ["query"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "calculate",
            "description": "Evaluate a mathematical expression. Use this for any numeric calculations — interest rates, loan repayments, percentages, currency conversions.",
            "parameters": {
                "type": "object",
                "properties": {
                    "expression": {
                        "type": "string",
                        "description": "A safe mathematical expression to evaluate. Examples: '500000 * 0.0435 / 12', '(1500 * 12) / 100', '250 * 1.1'"
                    }
                },
                "required": ["expression"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_current_date",
            "description": "Get the current date and time. Use this when the user asks about today's date, deadlines, or anything time-sensitive.",
            "parameters": {
                "type": "object",
                "properties": {},
                "required": []
            }
        }
    }
]


# ── Tool Implementations ───────────────────────────────────────────────────────

def web_search(query: str, max_results: int = 5) -> list[dict]:
    """Search DuckDuckGo and return top results."""
    try:
        time.sleep(1)
        results = DDGS().text(query, max_results=max_results)
        return [
            {
                "title": r.get("title", ""),
                "snippet": r.get("body", ""),
                "url": r.get("href", "")
            }
            for r in results
        ]
    except Exception as e:
        return [{"error": f"Search failed: {str(e)}"}]


def calculate(expression: str) -> dict:
    """
    Safely evaluate a mathematical expression.
    Only allows numbers and basic math operators — no arbitrary code execution.
    """
    # Whitelist: digits, operators, parentheses, decimal points, spaces
    if not re.match(r'^[\d\s\+\-\*\/\.\(\)\%\^]+$', expression):
        return {"error": "Invalid expression — only basic math operators allowed."}

    try:
        # Replace ^ with ** for power operations
        expression = expression.replace('^', '**')
        result = eval(expression, {"__builtins__": {}}, {"math": math})
        return {"expression": expression, "result": round(float(result), 6)}
    except ZeroDivisionError:
        return {"error": "Division by zero."}
    except Exception as e:
        return {"error": f"Calculation failed: {str(e)}"}


def get_current_date() -> dict:
    """Return current date and time in UTC and local-friendly format."""
    now = datetime.now(timezone.utc)
    return {
        "utc": now.isoformat(),
        "date": now.strftime("%A, %d %B %Y"),
        "time": now.strftime("%H:%M UTC"),
    }


# ── Tool Dispatcher ───────────────────────────────────────────────────────────

def execute_tool(name: str, arguments: dict) -> Any:
    """
    Dispatch a tool call by name.
    Returns the result as a string for injection back into the agent loop.
    """
    if name == "web_search":
        return web_search(**arguments)
    elif name == "calculate":
        return calculate(**arguments)
    elif name == "get_current_date":
        return get_current_date()
    else:
        return {"error": f"Unknown tool: {name}"}