"""
Stateless chat service wrapping the model runner.

Keeps no history by default; callers can pass message lists explicitly.
"""

from typing import Dict, Iterable, List, Optional

from config import settings
from services.model_runner import ModelRunner


class ChatService:
    def __init__(self):
        self.runner = ModelRunner(settings.model)

    def chat(self, messages: List[Dict[str, str]], params: Optional[Dict[str, object]] = None) -> str:
        return self.runner.generate(messages, params or {})

    def stream_chat(
        self, messages: List[Dict[str, str]], params: Optional[Dict[str, object]] = None
    ) -> Iterable[str]:
        return self.runner.stream_generate(messages, params or {})
