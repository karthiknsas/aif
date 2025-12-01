"""
Tools Module - All available tools for the agent

Usage:
    from tools import get_all_tools, get_tool

    tools = get_all_tools()  # Returns LangChain-compatible tools
    tool = get_tool("read_file")
"""

from typing import Dict, List

from langchain_core.tools import Tool

from .analysis_tools import (
    AnalyzeCSVTool,
    SearchVectorDBTool,
    StoreInVectorDBTool,
    SummarizeFileTool,
)
from .chart_tools import GenerateChartCodeTool
from .ui_tools import GenerateUITool, ListUITemplatesTool

# Registry of all tools
TOOL_REGISTRY = {
    # File operations
    # Charts
    "generate_chart": GenerateChartCodeTool,
    # UI
    "generate_ui": GenerateUITool,
    "list_ui_templates": ListUITemplatesTool,
    # Analysis
    "summarize_file": SummarizeFileTool,
    "analyze_csv": AnalyzeCSVTool,
    # Vector DB
    "store_in_vectordb": StoreInVectorDBTool,
    "search_vectordb": SearchVectorDBTool,
}


def get_tool(name: str):
    """Get a single tool instance by name"""
    if name not in TOOL_REGISTRY:
        raise ValueError(
            f"Unknown tool: {name}. Available: {list(TOOL_REGISTRY.keys())}"
        )
    return TOOL_REGISTRY[name]()


def get_all_tools() -> List[Tool]:
    """Get all tools as LangChain Tool objects"""
    tools = []

    for name, tool_class in TOOL_REGISTRY.items():
        instance = tool_class()
        lc_tool = Tool(
            name=instance.name, description=instance.description, func=instance.run
        )
        tools.append(lc_tool)

    return tools


def get_tools_by_category(category: str) -> List[Tool]:
    """Get tools filtered by category"""
    categories = {
        "file": [
            "read_file",
            "write_file",
            "list_files",
            "load_dataset",
            "query_dataframe",
        ],
        "chart": ["generate_chart"],
        "ui": ["generate_ui", "list_ui_templates"],
        "analysis": ["summarize_file", "analyze_csv"],
        "vector": ["store_in_vectordb", "search_vectordb"],
    }

    if category not in categories:
        raise ValueError(
            f"Unknown category: {category}. Available: {list(categories.keys())}"
        )

    tools = []
    for name in categories[category]:
        instance = TOOL_REGISTRY[name]()
        lc_tool = Tool(
            name=instance.name, description=instance.description, func=instance.run
        )
        tools.append(lc_tool)

    return tools


def list_tools() -> Dict[str, str]:
    """List all available tools with descriptions"""
    return {name: TOOL_REGISTRY[name]().description for name in TOOL_REGISTRY}


__all__ = [
    "get_all_tools",
    "get_tool",
    "get_tools_by_category",
    "list_tools",
    "TOOL_REGISTRY",
]
"""
Tools Module - All available tools for the agent

Usage:
    from tools import get_all_tools, get_tool

    tools = get_all_tools()  # Returns LangChain-compatible tools
    tool = get_tool("read_file")
"""

from typing import Dict, List

from langchain_core.tools import Tool

from .analysis_tools import (
    AnalyzeCSVTool,
    SearchVectorDBTool,
    StoreInVectorDBTool,
    SummarizeFileTool,
)
from .chart_tools import GenerateChartCodeTool
from .ui_tools import GenerateUITool, ListUITemplatesTool

# Registry of all tools
TOOL_REGISTRY = {
    # File operations
    # Charts
    "generate_chart": GenerateChartCodeTool,
    # UI
    "generate_ui": GenerateUITool,
    "list_ui_templates": ListUITemplatesTool,
    # Analysis
    "summarize_file": SummarizeFileTool,
    "analyze_csv": AnalyzeCSVTool,
    # Vector DB
    "store_in_vectordb": StoreInVectorDBTool,
    "search_vectordb": SearchVectorDBTool,
}


def get_tool(name: str):
    """Get a single tool instance by name"""
    if name not in TOOL_REGISTRY:
        raise ValueError(
            f"Unknown tool: {name}. Available: {list(TOOL_REGISTRY.keys())}"
        )
    return TOOL_REGISTRY[name]()


def get_all_tools() -> List[Tool]:
    """Get all tools as LangChain Tool objects"""
    tools = []

    for name, tool_class in TOOL_REGISTRY.items():
        instance = tool_class()
        lc_tool = Tool(
            name=instance.name, description=instance.description, func=instance.run
        )
        tools.append(lc_tool)

    return tools


def get_tools_by_category(category: str) -> List[Tool]:
    """Get tools filtered by category"""
    categories = {
        "file": [
            "read_file",
            "write_file",
            "list_files",
            "load_dataset",
            "query_dataframe",
        ],
        "chart": ["generate_chart"],
        "ui": ["generate_ui", "list_ui_templates"],
        "analysis": ["summarize_file", "analyze_csv"],
        "vector": ["store_in_vectordb", "search_vectordb"],
    }

    if category not in categories:
        raise ValueError(
            f"Unknown category: {category}. Available: {list(categories.keys())}"
        )

    tools = []
    for name in categories[category]:
        instance = TOOL_REGISTRY[name]()
        lc_tool = Tool(
            name=instance.name, description=instance.description, func=instance.run
        )
        tools.append(lc_tool)

    return tools


def list_tools() -> Dict[str, str]:
    """List all available tools with descriptions"""
    return {name: TOOL_REGISTRY[name]().description for name in TOOL_REGISTRY}


__all__ = [
    "get_all_tools",
    "get_tool",
    "get_tools_by_category",
    "list_tools",
    "TOOL_REGISTRY",
]
