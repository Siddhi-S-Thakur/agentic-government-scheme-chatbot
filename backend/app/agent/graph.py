from typing import Literal
from langgraph.graph import StateGraph, START, END
from app.agent.state import AgentState
from app.agent.nodes.handlers import AgentNodeHandlers
from app.rag.retriever.hybrid_retriever import HybridRetriever
from app.schemas.scheme_schema import SchemeRecord

def route_after_sufficiency(state: AgentState) -> Literal["ask_clarification", "retrieve_rag"]:
    """
    Conditional router based on profile completeness and intent.
    """
    if state.get("needs_clarification", False):
        return "ask_clarification"
    return "retrieve_rag"

def create_orchestrator_graph(
    retriever: HybridRetriever,
    schemes_catalog: dict[str, SchemeRecord]
):
    """
    Constructs and compiles the LangGraph single AI orchestrator agent.
    
    Graph Topology:
      START
        ↓
      understand_and_extract
        ↓
      check_sufficiency
        ↓ (conditional)
        ├── [needs_clarification = True]  → ask_clarification → END
        └── [needs_clarification = False] → retrieve_rag → evaluate_eligibility → generate_explanation → END
    """
    builder = StateGraph(AgentState)

    # 1. Register nodes
    builder.add_node("understand_and_extract", AgentNodeHandlers.understand_and_extract_node)
    builder.add_node("check_sufficiency", AgentNodeHandlers.check_sufficiency_node)
    builder.add_node("ask_clarification", AgentNodeHandlers.ask_clarification_node)
    builder.add_node("retrieve_rag", AgentNodeHandlers.make_retrieve_rag_node(retriever))
    builder.add_node("evaluate_eligibility", AgentNodeHandlers.make_evaluate_eligibility_node(schemes_catalog))
    builder.add_node("generate_explanation", AgentNodeHandlers.generate_explanation_node)

    # 2. Add edges
    builder.add_edge(START, "understand_and_extract")
    builder.add_edge("understand_and_extract", "check_sufficiency")

    builder.add_conditional_edges(
        "check_sufficiency",
        route_after_sufficiency,
        {
            "ask_clarification": "ask_clarification",
            "retrieve_rag": "retrieve_rag"
        }
    )

    builder.add_edge("ask_clarification", END)
    builder.add_edge("retrieve_rag", "evaluate_eligibility")
    builder.add_edge("evaluate_eligibility", "generate_explanation")
    builder.add_edge("generate_explanation", END)

    return builder.compile()
