# models/model_loader.py
from langchain_openai import ChatOpenAI

def load_model(model_name: str, base_url: str):
    return ChatOpenAI(
        model=model_name,
        base_url=base_url,
        api_key="not-needed",
        temperature=0.2,
        max_tokens=4096
    )
