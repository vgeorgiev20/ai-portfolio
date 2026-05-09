import json
import os
from openai import AsyncOpenAI
from langfuse import Langfuse
from dotenv import load_dotenv
from tools import TOOLS, execute_tool

load_dotenv()

langfuse = Langfuse(
    public_key=os.getenv("LANGFUSE_PUBLIC_KEY"),
    secret_key=os.getenv("LANGFUSE_SECRET_KEY"),
    host=os.getenv("LANGFUSE_HOST", "http://localhost:3000"),
)

MAX_ITERATIONS = 5  # safety cap — prevent infinite tool call loops

SYSTEM_PROMPT = """You are a helpful AI assistant with access to tools.

IMPORTANT: Always call get_current_date FIRST before making any web searches.
This ensures your search queries use the correct current date and year.

When answering questions:
- Call get_current_date first — always, before anything else
- Use web_search for any current or time-sensitive information, using the correct date from get_current_date
- Use calculate for any numeric computations — never do math in your head
- Chain multiple tool calls when needed — get date, search, then calculate based on results
- Only respond to the user when you have enough information from your tools

Be concise, accurate, and transparent about where your information comes from."""


async def run_agent(message: str, client: AsyncOpenAI) -> dict:
    """
    Run the agentic loop for a given user message.
    Uses Langfuse v2 SDK for tracing.
    """

    # ── Langfuse trace ────────────────────────────────────────────────────────
    trace = langfuse.trace(name="agent-run", input={"message": message})

    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": message},
    ]

    tool_calls_made = []
    iterations = 0

    while iterations < MAX_ITERATIONS:
        iterations += 1

        llm_span = trace.span(name=f"llm-call-{iterations}")

        completion = await client.chat.completions.create(
            model="gpt-4o-mini",
            messages=messages,
            tools=TOOLS,
            tool_choice="auto",
            temperature=0.2,
        )

        response_message = completion.choices[0].message
        finish_reason = completion.choices[0].finish_reason

        llm_span.end(output={
            "finish_reason": finish_reason,
            "content": response_message.content,
            "usage": {
                "prompt_tokens": completion.usage.prompt_tokens,
                "completion_tokens": completion.usage.completion_tokens,
                "total_tokens": completion.usage.total_tokens,
            }
        })

        if finish_reason == "stop":
            reply = response_message.content or ""
            trace.update(output={"reply": reply, "iterations": iterations})
            langfuse.flush()
            return {
                "reply": reply,
                "tool_calls_made": tool_calls_made,
                "iterations": iterations,
            }

        if finish_reason == "tool_calls" and response_message.tool_calls:

            messages.append({
                "role": "assistant",
                "content": response_message.content,
                "tool_calls": [
                    {
                        "id": tc.id,
                        "type": "function",
                        "function": {
                            "name": tc.function.name,
                            "arguments": tc.function.arguments,
                        }
                    }
                    for tc in response_message.tool_calls
                ]
            })

            for tool_call in response_message.tool_calls:
                name = tool_call.function.name
                arguments = json.loads(tool_call.function.arguments)

                tool_span = trace.span(name=f"tool-{name}", input=arguments)
                result = execute_tool(name, arguments)
                tool_span.end(output=result)

                tool_calls_made.append({
                    "tool": name,
                    "arguments": arguments,
                    "result": result,
                })

                messages.append({
                    "role": "tool",
                    "tool_call_id": tool_call.id,
                    "content": json.dumps(result),
                })

        else:
            break

    reply = "I was unable to complete the task within the allowed number of steps."
    trace.update(output={"reply": reply, "iterations": iterations})
    langfuse.flush()
    return {
        "reply": reply,
        "tool_calls_made": tool_calls_made,
        "iterations": iterations,
    }