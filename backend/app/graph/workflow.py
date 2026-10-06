import time
from typing import Dict, Any, List, Optional
from langgraph.graph import StateGraph, END
from app.graph.state import GraphState
from app.graph.nodes import (
    input_guardrail_node,
    thinker_router_node,
    parallel_retrieval_node,
    thinker_synthesis_node,
    comparative_synthesis_node,
    output_guardrail_node,
    session_memory_node
)
from app.rag.schema import QueryResponse

def route_after_input_guardrail(state: GraphState) -> str:
    if not state.get("is_safe", True):
        return "output_guardrail"
    return "thinker_router"

def create_rag_graph():
    builder = StateGraph(GraphState)

    # Add Nodes
    builder.add_node("input_guardrail", input_guardrail_node)
    builder.add_node("thinker_router", thinker_router_node)
    builder.add_node("parallel_retrieval", parallel_retrieval_node)
    builder.add_node("thinker_synthesis", thinker_synthesis_node)
    builder.add_node("comparative_synthesis", comparative_synthesis_node)
    builder.add_node("output_guardrail", output_guardrail_node)
    builder.add_node("session_memory", session_memory_node)

    # Set Entry Point
    builder.set_entry_point("input_guardrail")

    # Add Edges
    builder.add_conditional_edges(
        "input_guardrail",
        route_after_input_guardrail,
        {
            "output_guardrail": "output_guardrail",
            "thinker_router": "thinker_router"
        }
    )
    builder.add_edge("thinker_router", "parallel_retrieval")
    builder.add_edge("parallel_retrieval", "thinker_synthesis")
    builder.add_edge("thinker_synthesis", "comparative_synthesis")
    builder.add_edge("comparative_synthesis", "output_guardrail")
    builder.add_edge("output_guardrail", "session_memory")
    builder.add_edge("session_memory", END)

    return builder.compile()

# Singleton compiled graph
rag_workflow = create_rag_graph()

async def run_query_workflow(question: str, requested_thinkers: Optional[List[str]] = None, session_id: str = "default") -> QueryResponse:
    initial_state: GraphState = {
        "question": question,
        "requested_thinkers": requested_thinkers,
        "session_id": session_id,
        "guardrail_flags": [],
        "is_safe": True,
        "start_time": time.time()
    }

    final_state = rag_workflow.invoke(initial_state)

    sentence_groundedness = final_state.get("sentence_groundedness", [])
    total_sentences = len(sentence_groundedness)
    grounded_count = sum(1 for s in sentence_groundedness if s.grounded)
    flagged_count = sum(1 for s in sentence_groundedness if not s.grounded)

    return QueryResponse(
        answer=final_state.get("final_synthesis", "No synthesis generated."),
        per_thinker_breakdown=final_state.get("per_thinker_breakdown", []),
        citations=final_state.get("citations", []),
        guardrail_flags=final_state.get("guardrail_flags", []),
        faithfulness_score=final_state.get("faithfulness_score", 1.0),
        latency_ms=final_state.get("latency_ms", 0.0),
        selected_thinkers=final_state.get("selected_thinkers", []),
        is_safe=final_state.get("is_safe", True),
        sentence_groundedness=sentence_groundedness,
        regeneration_logs=final_state.get("regeneration_logs", []),
        total_sentences=total_sentences,
        grounded_sentences_count=grounded_count,
        flagged_sentences_count=flagged_count,
        is_weak_match=final_state.get("is_weak_match", False),
        weak_match_warning=final_state.get("weak_match_warning"),
        query_topic=final_state.get("query_topic"),
        topic_alignment_score=final_state.get("topic_alignment_score", 1.0),
        is_invalid_premise=final_state.get("is_invalid_premise", False),
        invalid_premise_details=final_state.get("invalid_premise_details")
    )
