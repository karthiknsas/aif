"""
LangChain ChatModel adapter for the ONNX model runner.

Implements the ChatModel interface so LangChain agents/tools can use the local
runner. Actual generation is deferred until the ONNX pipeline is wired.
"""

from typing import Any, Dict, Iterable, List, Optional

from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.messages import AIMessage, BaseMessage, HumanMessage, SystemMessage
from langchain_core.outputs import ChatResult, ChatGeneration

from services.chat_service import ChatService


class LocalONNXChatModel(BaseChatModel):
    def __init__(self):
        super().__init__()
        self.chat_service = ChatService()
        self._bound_tools = None

    @property
    def _llm_type(self) -> str:
        return "local_onnx_chat_model"

    # Minimal bind_tools to satisfy router/tool expectations; local runner
    # does not produce real tool calls.
    def bind_tools(self, tools):
        self._bound_tools = tools
        return self

    def _convert_messages(self, messages: List[BaseMessage]) -> List[Dict[str, str]]:
        converted = []
        for m in messages:
            if isinstance(m, HumanMessage):
                role = "user"
            elif isinstance(m, SystemMessage):
                role = "system"
            elif isinstance(m, AIMessage):
                role = "assistant"
            else:
                role = "user"
            converted.append({"role": role, "content": m.content})
        return converted

    def _generate(
        self,
        messages: List[BaseMessage],
        stop: Optional[List[str]] = None,
        run_manager: Optional[Any] = None,
        **kwargs: Any,
    ) -> ChatResult:
        params: Dict[str, Any] = {}
        if stop:
            params["stop"] = stop
        params.update(kwargs)
        payload = self._convert_messages(messages)
        text = self.chat_service.chat(payload, params)
        generation = ChatGeneration(message=AIMessage(content=text))
        return ChatResult(generations=[generation])

    def _stream(
        self,
        messages: List[BaseMessage],
        stop: Optional[List[str]] = None,
        run_manager: Optional[Any] = None,
        **kwargs: Any,
    ) -> Iterable[ChatGeneration]:
        params: Dict[str, Any] = {}
        if stop:
            params["stop"] = stop
        params.update(kwargs)
        payload = self._convert_messages(messages)
        for token in self.chat_service.stream_chat(payload, params):
            yield ChatGeneration(message=AIMessage(content=token))
