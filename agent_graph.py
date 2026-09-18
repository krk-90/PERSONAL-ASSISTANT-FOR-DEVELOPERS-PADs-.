"""LangGraph supervisor and specialist agents for PADs."""

import json
import re
from pathlib import Path
from typing import Literal, TypedDict

from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import END, START, StateGraph

from dev_tools import github_read, repository_from_remote, run_git_read, web_fetch
from llm_call import call

MEMORY_FILE = Path(__file__).resolve().parent / ".pads_memory.json"


class AgentState(TypedDict, total=False):
    query: str
    route: str
    result: str
    memory: list[str]


def load_memory() -> list[str]:
    try:
        return json.loads(MEMORY_FILE.read_text(encoding="utf-8"))
    except (FileNotFoundError, json.JSONDecodeError):
        return []


def save_memory(memory: list[str]) -> None:
    MEMORY_FILE.write_text(json.dumps(memory[-50:], indent=2), encoding="utf-8")


def supervisor(state: AgentState) -> AgentState:
    query = state["query"].lower()
    if any(word in query for word in ("task", "todo", "remind", "milestone")):
        route = "tasks"
    elif any(word in query for word in ("github", "issue", "pull request", "repository", "repo")):
        route = "github"
    elif any(word in query for word in ("git", "branch", "commit", "diff", "status")):
        route = "git"
    elif re.search(r"https?://|web search|browse|crawl|fetch", query):
        route = "web"
    else:
        route = "general"
    return {"route": route, "memory": load_memory()}


def tasks_agent(state: AgentState) -> AgentState:
    memory = state.get("memory", [])
    task = state["query"].strip()
    memory.append(f"Task request: {task}")
    save_memory(memory)
    return {"result": f"Task captured in PADs memory: {task}"}


def git_agent(state: AgentState) -> AgentState:
    query = state["query"].lower()
    operation = "diff" if "diff" in query else "log" if "log" in query or "commit" in query else "remote" if "remote" in query else "status"
    return {"result": f"Git {operation} (read-only):\n{run_git_read(operation)}"}


def github_agent(state: AgentState) -> AgentState:
    query = state["query"].lower()
    resource = "pulls" if "pull" in query or "pr" in query else "issues" if "issue" in query else "repository"
    repository = repository_from_remote()
    match = re.search(r"[\w.-]+/[\w.-]+", state["query"])
    if match:
        repository = match.group(0)
    if not repository:
        return {"result": "Provide a GitHub repository as owner/name."}
    return {"result": f"GitHub {resource} (read-only):\n{github_read(repository, resource)}"}


def web_agent(state: AgentState) -> AgentState:
    match = re.search(r"https?://[^\s]+", state["query"])
    if not match:
        return {"result": "Provide an http:// or https:// URL to fetch."}
    return {"result": web_fetch(match.group(0))}


def general_agent(state: AgentState) -> AgentState:
    memory = state.get("memory", [])
    context = "\n".join(memory[-5:]) or "No stored memory."
    return {"result": call(f"Relevant PADs memory:\n{context}\n\nUser request:\n{state['query']}" )}


def route(state: AgentState) -> Literal["tasks", "git", "github", "web", "general"]:
    return state["route"]


def build_graph():
    graph = StateGraph(AgentState)
    graph.add_node("supervisor", supervisor)
    graph.add_node("tasks", tasks_agent)
    graph.add_node("git", git_agent)
    graph.add_node("github", github_agent)
    graph.add_node("web", web_agent)
    graph.add_node("general", general_agent)
    graph.add_edge(START, "supervisor")
    graph.add_conditional_edges("supervisor", route)
    for node in ("tasks", "git", "github", "web", "general"):
        graph.add_edge(node, END)
    return graph.compile(checkpointer=MemorySaver())


agent = build_graph()


def run_agent(query: str, thread_id: str = "local-session") -> str:
    result = agent.invoke({"query": query}, config={"configurable": {"thread_id": thread_id}})
    return result["result"]
