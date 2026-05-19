# graph/state.py
#
# This is the SINGLE most important concept in LangGraph.
# Every node receives the full state and returns a PARTIAL update.
# LangGraph merges the update in automatically — nodes never clobber each other.
#
# The `Annotated[list[str], add]` on research_findings is a REDUCER.
# Instead of overwriting the list, each node's return value gets APPENDED.
# This becomes critical when you have parallel nodes writing to the same field.

from typing import Annotated, TypedDict
from operator import add


class AgentState(TypedDict):
    user_query: str
    query_type: str  # "simple" | "complex" — set by orchestrator, read by router

    # Reducer: if two nodes both return research_findings, they get merged (not overwritten)
    research_findings: Annotated[list[str], add]

    sub_questions: list[str]
    final_answer: str