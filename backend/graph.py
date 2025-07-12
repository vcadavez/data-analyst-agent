# backend/graph.py

from langgraph.graph import StateGraph
from langgraph.checkpoint.sqlite import SqliteSaver
import sqlite3
from backend.tools.tool_nodes import execute_tool_node
from backend.llm import llm_with_tools
from backend.tools.tool_list import TOOLS
from langchain_core.messages import HumanMessage

class AgentState(dict):
    pass

def create_graph():
    builder = StateGraph(AgentState)
    builder.add_node(
        "agent",
        lambda state: {**state, "output": llm_with_tools.invoke([HumanMessage(content=state["question"])])}
    )
    builder.add_node("execute_tool", execute_tool_node)
    builder.set_entry_point("agent")
    builder.add_conditional_edges(
        "agent",
        lambda x: x["output"].tool_calls[0]["name"] if hasattr(x["output"], "tool_calls") and x["output"].tool_calls else "__end__",
        {tool.name: "execute_tool" for tool in TOOLS}
    )
    builder.add_edge("execute_tool", "agent")

    conn = sqlite3.connect("agent_memory.db", check_same_thread=False)
    memory = SqliteSaver(conn)
    return builder.compile(checkpointer=memory)
