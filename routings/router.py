"""
Routing via LLM function-calling when available; keyword fallback otherwise.
"""

from typing import Optional

from langchain_core.prompts import ChatPromptTemplate
from langchain_core.tools import tool


@tool("route_decision", return_direct=True)
def route_decision(mode: str, reason: str):
    """
    Choose how to handle the user request.
    mode: one of ["CHAT", "AGENT"].
    reason: short justification for the choice.
    """


router_prompt = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            (
                "You are a router. Decide how to handle the request.\n"
                "- Use AGENT when tools, actions, code execution, environment checks, fetching data, or multi-step reasoning with tools are needed.\n"
                "- Use CHAT for general Q&A, explanations, brainstorming, or when no tools are required.\n"
                "Call the function 'route_decision' with mode ('CHAT' or 'AGENT') and a concise reason."
            ),
        ),
        ("human", "{user_input}"),
    ]
)


def _keyword_route(user_input: str) -> str:
    triggers = ["run", "fetch", "execute", "scan", "list", "analyze", "tool", "call"]
    if any(t in user_input.lower() for t in triggers):
        return "AGENT"
    return "CHAT"


def route_message(llm=None, user_input: str = "", session_id: Optional[str] = None) -> str:
    """
    Ask the LLM (function calling) to choose between CHAT and AGENT.
    Falls back to keyword routing on errors or missing tool support.
    """
    if llm:
        try:
            # Some LLM clients may not support bind_tools; guard accordingly.
            if hasattr(llm, "bind_tools"):
                llm_with_tools = llm.bind_tools([route_decision])
                result = llm_with_tools.invoke(router_prompt.format_messages(user_input=user_input))
                tool_calls = getattr(result, "tool_calls", None)
                if tool_calls:
                    for tc in tool_calls:
                        if tc.get("name") == "route_decision":
                            mode = tc.get("args", {}).get("mode", "CHAT")
                            return str(mode).upper()
        except Exception:
            pass

    return _keyword_route(user_input)
