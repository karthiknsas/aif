# agents/chat_agent.py


def build_chat_agent(llm, callbacks=None):
    def chat(message: str) -> str:
        resp = llm.invoke(message, callbacks=callbacks)
        return resp.content

    return chat
