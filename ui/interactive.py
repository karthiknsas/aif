# ui/interactive.py

import logging
from agents.chat_agent import build_chat_agent
from agents.tool_agent import build_tool_agent
from models.model_loader import load_model
from config import settings
from config.logging_config import setup_logging, with_context
from routings.router import route_message
from services.guardrails import check_input


class AgentRuntime:

    def __init__(self, model_name, base_url, tools):
        base_logger = setup_logging(settings.app)
        # No explicit session/user here; downstream can wrap with more context.
        self.user = "Guest"
        self.session_id = None
        self.logger = with_context(base_logger, component="AgentRuntime", user=self.user)
        self.llm = load_model(model_name, base_url)
        self.tools = tools
        self.agent = build_tool_agent(self.llm, tools)
        self.chat = build_chat_agent(self.llm)

    def run(self, user_input: str) -> str:
        allowed, reason = check_input(user_input)
        if not allowed:
            self.logger.info("Guardrail blocked input", extra={"reason": reason})
            return "I need clarification or approval before proceeding with that request."

        mode = route_message(llm=self.llm, user_input=user_input)
        self.logger.info("Routing decision", extra={"mode": mode, "input_preview": user_input[:200]})

        if mode == "AGENT":
            try:
                result = self.agent.invoke({"input": user_input})
                output = result.get("output", "")
                if output:
                    return output
                return (
                    "I couldn't get a clear tool result. Please clarify what you want me to do."
                )
            except Exception:
                return (
                    "I couldn't run the tools reliably. Please clarify or rephrase your request."
                )
        return self.chat(user_input)
