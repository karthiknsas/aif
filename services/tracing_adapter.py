"""
Tracing adapter placeholder for AI Toolkit or LangChain callbacks.

This keeps tracing optional and off by default; when AI Toolkit tracing
is available, wire it here to collect spans/runs.
"""

from typing import List

from langchain.callbacks.base import BaseCallbackHandler
from langchain.callbacks.tracers.run_collector import RunCollectorCallbackHandler

from config import settings


def get_trace_handlers() -> List[BaseCallbackHandler]:
    if not settings.app.tracing_enabled:
        return []

    # TODO: Replace RunCollector with AI Toolkit-specific tracer when available.
    return [RunCollectorCallbackHandler()]
