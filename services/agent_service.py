"""
Agent service using LangChain's tool-calling agents (non-ReAct).

Maintains per-session state externally; this class stays stateless and expects
callers to provide session-specific context/history if needed.
"""

from typing import Any, Dict, Iterable, List, Optional

from langchain.agents import AgentExecutor, create_openai_tools_agent
from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.prompts import ChatPromptTemplate


class AgentService:
    """
    Agent service using LangChain tool-calling agent (non-ReAct).

    Expects a LangChain-compatible ChatModel. When the ONNX runner is wrapped
    with a ChatModel adapter, it can be passed here.
    """

    def __init__(self, llm: BaseChatModel, tools: Optional[List[Any]] = None):
        self.llm = llm
        self.tools = tools or []
        self.agent = self._build_agent(self.llm, self.tools)

    def _build_agent(self, llm: BaseChatModel, tools: List[Any]) -> AgentExecutor:
        # Use simple system+human prompt; callers can extend.
        prompt = ChatPromptTemplate.from_messages(
            [
                ("system", "You are a highly reliable developer assistant."),
                ("human", "{input}"),
            ]
        )
        # LangChain openai-tools agent uses tool-calling style, not ReAct.
        agent = create_openai_tools_agent(llm=llm, tools=tools, prompt=prompt)
        return AgentExecutor(agent=agent, tools=tools, verbose=True, max_iterations=5)

    def invoke(self, user_input: str, extra: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        payload = {"input": user_input}
        if extra:
            payload.update(extra)
        return self.agent.invoke(payload)

    def stream(self, user_input: str, extra: Optional[Dict[str, Any]] = None) -> Iterable[Dict[str, Any]]:
        payload = {"input": user_input}
        if extra:
            payload.update(extra)
        return self.agent.stream(payload)
