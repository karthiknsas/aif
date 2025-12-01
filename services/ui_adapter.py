"""
UI adapter for Open WebUI or in-process consumers.

Provides helpers to expose safe config and to route chat/agent calls. If/when
an HTTP shim is added, handlers can wrap these functions.
"""

from typing import Any, Dict, Iterable, List, Optional

from config import settings
from services.agent_service import AgentService
from services.llm_adapter import LocalONNXChatModel


class UIAdapter:
    def __init__(self, tools: Optional[List[Any]] = None):
        # Use LangChain-compatible adapter over the local ONNX runner.
        llm = LocalONNXChatModel()
        self.agent_service = AgentService(llm=llm, tools=tools or [])
        self.llm = llm

    def config_view(self) -> Dict[str, object]:
        return settings.ui_safe_view()

    def chat(self, messages: List[Dict[str, str]], params: Optional[Dict[str, object]] = None) -> str:
        # Single-turn chat; caller supplies messages explicitly (no implicit history).
        # Convert role/content dicts to LangChain messages for the adapter.
        from langchain_core.messages import HumanMessage, SystemMessage, AIMessage

        lc_messages = []
        for m in messages:
            role = m.get("role", "user")
            content = m.get("content", "")
            if role == "system":
                lc_messages.append(SystemMessage(content=content))
            elif role == "assistant":
                lc_messages.append(AIMessage(content=content))
            else:
                lc_messages.append(HumanMessage(content=content))

        return self.llm.invoke(lc_messages, **(params or {})).content

    def agent_invoke(self, user_input: str, extra: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        return self.agent_service.invoke(user_input, extra)

    def agent_stream(self, user_input: str, extra: Optional[Dict[str, Any]] = None) -> Iterable[Dict[str, Any]]:
        return self.agent_service.stream(user_input, extra)
