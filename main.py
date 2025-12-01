import argparse

from tools import get_all_tools
from ui.interactive import AgentRuntime


def main():
    model_name = "qwen2.5-coder-7b"
    base_url = "http://localhost:8000/v1"

    parser = argparse.ArgumentParser(description="Personal Dev Assistant")
    parser.add_argument("--user", "-u", default="default", help="User ID")

    tools = get_all_tools()

    runtime = AgentRuntime(model_name, base_url, tools)

    print("\n=== Developer Assistant ===\n")

    while True:
        user_input = input("You: ")

        if user_input.strip().lower() in ("exit", "quit"):
            print("Goodbye!")
            break

        output = runtime.run(user_input)
        print("\nAssistant:", output, "\n")


if __name__ == "__main__":
    main()
