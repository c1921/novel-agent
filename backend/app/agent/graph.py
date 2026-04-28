from __future__ import annotations

from sqlalchemy.orm import Session

from langgraph.graph import END, START, StateGraph

from app.agent import nodes
from app.agent.state import NovelAgentState


def _compile_question_graph(db: Session):
    graph = StateGraph(NovelAgentState)
    graph.add_node("load_project_context", lambda state: nodes.load_project_context(state, db))
    graph.add_node("retrieve_relevant_knowledge", lambda state: nodes.retrieve_relevant_knowledge(state, db))
    graph.add_node("generate_plot_questions", lambda state: nodes.generate_plot_questions(state, db))
    graph.add_edge(START, "load_project_context")
    graph.add_edge("load_project_context", "retrieve_relevant_knowledge")
    graph.add_edge("retrieve_relevant_knowledge", "generate_plot_questions")
    graph.add_edge("generate_plot_questions", END)
    return graph.compile()


def _compile_outline_graph(db: Session):
    graph = StateGraph(NovelAgentState)
    graph.add_node("generate_chapter_outline", lambda state: nodes.generate_chapter_outline(state, db))
    graph.add_edge(START, "generate_chapter_outline")
    graph.add_edge("generate_chapter_outline", END)
    return graph.compile()


def _compile_draft_graph(db: Session):
    graph = StateGraph(NovelAgentState)
    graph.add_node("generate_draft", lambda state: nodes.generate_draft(state, db))
    graph.add_node("polish_draft", lambda state: nodes.polish_draft(state, db))
    graph.add_node("consistency_check", lambda state: nodes.consistency_check(state, db))
    graph.add_edge(START, "generate_draft")
    graph.add_edge("generate_draft", "polish_draft")
    graph.add_edge("polish_draft", "consistency_check")
    graph.add_edge("consistency_check", END)
    return graph.compile()


def run_question_phase(state: NovelAgentState, db: Session) -> NovelAgentState:
    return _compile_question_graph(db).invoke(state)


def run_outline_phase(state: NovelAgentState, db: Session) -> NovelAgentState:
    return _compile_outline_graph(db).invoke(state)


def run_draft_phase(state: NovelAgentState, db: Session) -> NovelAgentState:
    return _compile_draft_graph(db).invoke(state)
