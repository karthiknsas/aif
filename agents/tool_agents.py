# agents/tool_agent.py

from langchain.agents import AgentExecutor, create_openai_tools_agent
from langchain_core.prompts import ChatPromptTemplate


def build_tool_agent(llm, tools):
    prompt = ChatPromptTemplate.from_messages(
        [
            (
                "system",
                (
                    "You are a careful developer assistant.\n"
                    "- Use tools when the user asks for actions, code execution, environment checks, data fetch, or reading an attached file/path; otherwise answer directly.\n"
                    "- If required info is missing (e.g., file path not provided), ask for clarification instead of guessing.\n"
                    "- Do not invent tools or parameters. Use only the provided tools.\n"
                    "- Be concise when returning results; summarize tool output clearly."
                ),
            ),
            ("human", "{input}"),
        ]
    )

    agent = create_openai_tools_agent(llm=llm, tools=tools, prompt=prompt)

    # verbose=False to avoid leaking prompts/tool traces; flip on for debugging if needed.
    return AgentExecutor(agent=agent, tools=tools, verbose=False, max_iterations=5)
