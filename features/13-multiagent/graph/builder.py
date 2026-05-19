# graph/builder.py
#
# This is where you DECLARE the graph structure.
# Think of it as your architecture diagram turned into code.
#
# Flow:
#
#   START
#     │
#     ▼
#  orchestrator  ──── query_type == "complex" ──▶  researcher ──▶  writer ──▶ END
#     │
#     └─────────────── query_type == "simple"  ──────────────────▶  writer ──▶ END
#
# The conditional edge is the key LangGraph concept here.
# The routing function reads state and returns a NODE NAME (as a string).
# LangGraph uses the mapping dict to resolve that string to the actual node.

from langgraph.graph import END, START, StateGraph

from .nodes import orchestrator_node, research_node, writer_node
from .state import AgentState


def _route_after_orchestrator(state: AgentState) -> str:
    """
    Conditional edge function.
    Returns the NAME of the next node based on state.
    This is called automatically by LangGraph after orchestrator_node runs.
    """
    if state["query_type"] == "complex":
        return "needs_research"
    return "skip_research"


def build_graph():
    """
    Compiles and returns the runnable LangGraph graph.
    Call this once at startup and reuse the compiled graph.
    """
    builder = StateGraph(AgentState)

    # ── Register nodes ─────────────────────────────
    # First arg is the NAME you use when referencing this node in edges.
    # Second arg is the function to call.
    builder.add_node("orchestrator", orchestrator_node)
    builder.add_node("researcher", research_node)
    builder.add_node("writer", writer_node)

    # ── Wire edges ──────────────────────────────────
    # Fixed edge: graph always starts at orchestrator
    builder.add_edge(START, "orchestrator")

    # Conditional edge: after orchestrator, call _route_after_orchestrator
    # to decide where to go. The dict maps return values → node names.
    builder.add_conditional_edges(
        "orchestrator",
        _route_after_orchestrator,
        {
             "needs_research": "researcher",  # label → actual node name
             "skip_research":  "writer",      # label → actual node name
        },
    )

    # Fixed edge: researcher always hands off to writer
    builder.add_edge("researcher", "writer")

    # Fixed edge: writer is always the last stop
    builder.add_edge("writer", END)

    # compile() validates the graph (checks for orphan nodes, missing edges, etc.)
    # and returns a Runnable you can call with .invoke() or .ainvoke()
    return builder.compile()