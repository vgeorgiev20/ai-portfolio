# graph/nodes.py
#
# Each node is just a Python function:
#   - receives the full AgentState
#   - does its work (LLM call, tool call, logic)
#   - returns a DICT with only the fields it wants to update
#
# LangGraph calls these for you at the right time.
# You never call them directly.

import os
from dotenv import load_dotenv
load_dotenv()

import json
import logging

from langchain_core.messages import HumanMessage, SystemMessage
from langchain_openai import ChatOpenAI

from .state import AgentState

logger = logging.getLogger(__name__)

# One shared LLM instance — all nodes use the same model.
# You could give different nodes different models (e.g. orchestrator uses
# a cheap fast model, writer uses a smarter one). That's model-routing, feature 12.
llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)


# ─────────────────────────────────────────────
# NODE 1: Orchestrator
# Decides whether the query needs deep research or can be answered directly.
# Sets query_type, which the conditional edge reads to decide routing.
# ─────────────────────────────────────────────
def orchestrator_node(state: AgentState) -> dict:
    logger.info("[orchestrator] classifying query: %s", state["user_query"])

    system = SystemMessage(content="""You are a query classifier for a research assistant.
Analyse the user query and respond with ONLY a JSON object — no markdown, no explanation:
{
  "query_type": "simple" | "complex",
  "reasoning": "one sentence"
}

Rules:
- "simple": a direct factual question answerable in one or two sentences
- "complex": requires multiple angles, comparisons, recent context, or multi-step reasoning
""")

    human = HumanMessage(content=f"Classify this query: {state['user_query']}")
    response = llm.invoke([system, human])

    try:
        data = json.loads(response.content)
        query_type = data.get("query_type", "simple")
        logger.info("[orchestrator] classified as: %s — %s", query_type, data.get("reasoning"))
    except json.JSONDecodeError:
        logger.warning("[orchestrator] failed to parse JSON, defaulting to simple")
        query_type = "simple"

    return {"query_type": query_type}


# ─────────────────────────────────────────────
# NODE 2: Researcher
# Only reached for "complex" queries.
# Breaks the query into sub-questions, then answers each one separately.
# This is the "fan out" pattern at the LLM level — each sub-question is its own call.
# ─────────────────────────────────────────────
def research_node(state: AgentState) -> dict:
    logger.info("[researcher] breaking down query into sub-questions")

    # Step 1 — generate sub-questions
    decompose_system = SystemMessage(content="""You are a research planner.
Break the user query into 2-3 focused sub-questions that together fully answer it.
Respond with ONLY a JSON object — no markdown, no explanation:
{"sub_questions": ["question 1", "question 2", "question 3"]}
""")

    decompose_response = llm.invoke([
        decompose_system,
        HumanMessage(content=state["user_query"])
    ])

    try:
        data = json.loads(decompose_response.content)
        sub_questions = data.get("sub_questions", [state["user_query"]])
    except json.JSONDecodeError:
        logger.warning("[researcher] failed to parse sub-questions, using original query")
        sub_questions = [state["user_query"]]

    logger.info("[researcher] sub-questions: %s", sub_questions)

    # Step 2 — answer each sub-question individually
    # Each answer becomes a "finding" that the writer node will synthesise.
    findings = []
    for i, question in enumerate(sub_questions):
        logger.info("[researcher] researching sub-question %d/%d", i + 1, len(sub_questions))
        answer = llm.invoke([
            SystemMessage(content="You are a specialist researcher. Answer the question accurately and concisely."),
            HumanMessage(content=question)
        ])
        findings.append(f"Sub-question: {question}\nFindings: {answer.content}")

    return {
        "sub_questions": sub_questions,
        "research_findings": findings,  # reducer will append these to state
    }


# ─────────────────────────────────────────────
# NODE 3: Writer
# Always the final node.
# If research was done, synthesises findings into a coherent answer.
# If query was simple, answers directly without context.
# ─────────────────────────────────────────────
def writer_node(state: AgentState) -> dict:
    logger.info("[writer] generating final answer (has research: %s)", bool(state.get("research_findings")))

    if state.get("research_findings"):
        # Complex path — synthesise research findings
        findings_text = "\n\n".join(state["research_findings"])
        system = SystemMessage(content=f"""You are a synthesis specialist.
Using the research findings below, write a comprehensive, well-structured answer to the original query.
Be clear and direct. Use plain paragraphs — no bullet points unless the content genuinely suits them.

Research findings:
{findings_text}
""")
    else:
        # Simple path — answer directly
        system = SystemMessage(content="You are a helpful assistant. Answer the query clearly and concisely.")

    response = llm.invoke([
        system,
        HumanMessage(content=state["user_query"])
    ])

    return {"final_answer": response.content}