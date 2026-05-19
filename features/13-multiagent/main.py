# main.py
#
# Run from inside features/13-multiagent/:
#   uvicorn main:app --reload --port 8013

import logging
import os

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException

from graph.builder import build_graph
from graph.state import AgentState
from schemas import ResearchRequest, ResearchResponse

load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Feature 13 — Multi-Agent Research Assistant",
    description="LangGraph orchestrator → researcher → writer pipeline",
)

# Compile the graph once at startup.
# This is like building a compiled query plan — do it once, reuse everywhere.
graph = build_graph()


@app.post("/research", response_model=ResearchResponse)
async def research(request: ResearchRequest):
    """
    Runs the full multi-agent pipeline for a given query.

    The graph decides internally whether to invoke the researcher node
    or route directly to the writer. The response always includes query_type
    so the frontend can show which path was taken.
    """
    logger.info("Received query: %s", request.query)

    initial_state: AgentState = {
        "user_query": request.query,
        "query_type": "",
        "sub_questions": [],
        "research_findings": [],
        "final_answer": "",
    }

    try:
        result = await graph.ainvoke(initial_state)
    except Exception as e:
        logger.exception("Graph execution failed")
        raise HTTPException(status_code=500, detail=str(e))

    return ResearchResponse(
        query=result["user_query"],
        query_type=result["query_type"],
        sub_questions=result.get("sub_questions", []),
        final_answer=result["final_answer"],
    )


@app.get("/health")
async def health():
    return {"status": "ok", "feature": "13-multiagent"}