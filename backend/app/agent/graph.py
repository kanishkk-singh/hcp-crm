"""
LangGraph agent that manages HCP interactions.

Role: this agent sits between the rep's chat input and the CRM database.
It decides -- based on the conversation -- whether to log a new interaction,
edit an existing one, pull HCP history for context, schedule a follow-up,
or produce a manager-facing summary. It never edits the DB directly; it always
goes through one of the 5 typed tools, which keeps every write auditable.
"""
from typing import Annotated, TypedDict
from langgraph.graph import StateGraph, END
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode, tools_condition
from langchain_core.messages import SystemMessage

from app.agent.llm import llm_primary
from app.agent.tools import ALL_TOOLS

SYSTEM_PROMPT = """You are the AI agent inside an AI-first CRM's HCP (Healthcare
Professional) module. Field sales reps talk to you in natural language and you
help them log interactions, edit past logs, look up an HCP's history, schedule
follow-ups, and summarize interactions for their manager.

Rules:
- If the rep describes something that just happened with an HCP, call log_interaction.
- If the rep wants to change something already logged, call edit_interaction.
- If the rep asks "what happened last time" or wants context before a visit, call search_hcp_history.
- If the rep wants a reminder/task created, call schedule_followup.
- If the rep or manager wants a short recap of a specific interaction, call summarize_interaction.
- Always confirm back to the rep in plain, professional language after a tool runs.
- Never invent an hcp_id or interaction_id -- ask for it if you don't have it in context.
"""

llm_with_tools = llm_primary.bind_tools(ALL_TOOLS)


class AgentState(TypedDict):
    messages: Annotated[list, add_messages]


def call_model(state: AgentState):
    messages = state["messages"]
    if not any(isinstance(m, SystemMessage) for m in messages):
        messages = [SystemMessage(content=SYSTEM_PROMPT)] + messages
    response = llm_with_tools.invoke(messages)
    return {"messages": [response]}


def build_agent_graph():
    graph = StateGraph(AgentState)
    graph.add_node("agent", call_model)
    graph.add_node("tools", ToolNode(ALL_TOOLS))

    graph.set_entry_point("agent")
    graph.add_conditional_edges("agent", tools_condition)
    graph.add_edge("tools", "agent")

    return graph.compile()


# compiled once at import time, reused across requests
agent_executor = build_agent_graph()
