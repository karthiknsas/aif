"""File Operation Tools
import os
from pathlib import Path
from typing import Optional
import pandas as pd
import json
import logging

from .base_tool import BaseTool, ToolResult, with_retry

logger = logging.getLogger(__name__)

class ReadFileTool(BaseTool):
    name = "read_file"
    description = "Read contents of a file. Input: file path"

    def _execute(self, path: str) -> ToolResult:
        path = path.strip()

        if not os.path.exists(path):
            return ToolResult(False, None, f"File not found: {path}")

        # Check file size
        size_mb = os.path.getsize(path) / (1024 * 1024)
        if size_mb > self.config.tool.max_file_size_mb:
            return ToolResult(False, None, f"File too large: {size_mb:.1f}MB > {self.config.tool.max_file_size_mb}MB")

        # Check extension
        ext = Path(path).suffix.lower()
        if ext not in self.config.tool.allowed_extensions:
            return ToolResult(False, None, f"Extension not allowed: {ext}")

        try:
            with open(path, "r", encoding="utf-8") as f:
                content = f.read()
            return ToolResult(True, content)
        except UnicodeDecodeError:
            with open(path, "r", encoding="latin-1") as f:
                content = f.read()
            return ToolResult(True, content)
        except Exception as e:
            return ToolResult(False, None, str(e))


class WriteFileTool(BaseTool):
    name = "write_file"
    description = "Write content to a file. Input: 'filepath|content'"

    def _execute(self, input_str: str) -> ToolResult:
        if "|" not in input_str:
            return ToolResult(False, None, "Format: 'filepath|content'")

        path, content = input_str.split("|", 1)
        path = path.strip()

        # Validate extension
        ext = Path(path).suffix.lower()
        if ext not in self.config.tool.allowed_extensions:
            return ToolResult(False, None, f"Extension not allowed: {ext}")

        try:
            # Create directory if needed
            Path(path).parent.mkdir(parents=True, exist_ok=True)

            with open(path, "w", encoding="utf-8") as f:
                f.write(content)

            return ToolResult(True, f"Written to {path} ({len(content)} chars)")
        except Exception as e:
            return ToolResult(False, None, str(e))


class ListFilesTool(BaseTool):
    name = "list_files"
    description = "List files in a directory. Input: directory path (optional filter like '*.py')"

    def _execute(self, input_str: str) -> ToolResult:
        parts = input_str.strip().split()
        dir_path = parts[0] if parts else "."
        pattern = parts[1] if len(parts) > 1 else "*"

        if not os.path.isdir(dir_path):
            return ToolResult(False, None, f"Not a directory: {dir_path}")

        try:
            p = Path(dir_path)
            files = list(p.glob(pattern))

            result = []
            for f in files[:50]:  # Limit results
                stat = f.stat()
                size = stat.st_size
                result.append({
                    "name": f.name,
                    "path": str(f),
                    "type": "dir" if f.is_dir() else "file",
                    "size": size
                })

            return ToolResult(True, json.dumps(result, indent=2))
        except Exception as e:
            return ToolResult(False, None, str(e))


class LoadDatasetTool(BaseTool):
    name = "load_dataset"
    description = "Load CSV/Excel file and return summary. Input: file path"

    @with_retry(max_retries=2)
    def _execute(self, path: str) -> ToolResult:
        path = path.strip()

        if not os.path.exists(path):
            return ToolResult(False, None, f"File not found: {path}")

        try:
            ext = Path(path).suffix.lower()

            if ext == ".csv":
                df = pd.read_csv(path, nrows=self.config.tool.max_csv_rows)
            elif ext in [".xlsx", ".xls"]:
                df = pd.read_excel(path, nrows=self.config.tool.max_csv_rows)
            else:
                return ToolResult(False, None, f"Unsupported format: {ext}")

            summary = {
                "shape": df.shape,
                "columns": list(df.columns),
                "dtypes": df.dtypes.astype(str).to_dict(),
                "nulls": df.isnull().sum().to_dict(),
                "preview": df.head(10).to_string()
            }

            return ToolResult(True, json.dumps(summary, indent=2, default=str))
        except Exception as e:
            return ToolResult(False, None, str(e))


# Store loaded dataframes for follow-up queries
_dataframes = {}

class QueryDataframeTool(BaseTool):
    name = "query_dataframe"
    description = "Query a loaded dataframe. Input: 'filepath|query' (query like: 'head', 'describe', 'df[col].value_counts()')"

    def _execute(self, input_str: str) -> ToolResult:
        if "|" not in input_str:
            return ToolResult(False, None, "Format: 'filepath|query'")

        path, query = input_str.split("|", 1)
        path = path.strip()
        query = query.strip()

        # Load if not cached
        if path not in _dataframes:
            try:
                ext = Path(path).suffix.lower()
                if ext == ".csv":
                    _dataframes[path] = pd.read_csv(path)
                elif ext in [".xlsx", ".xls"]:
                    _dataframes[path] = pd.read_excel(path)
                else:
                    return ToolResult(False, None, f"Unsupported: {ext}")
            except Exception as e:
                return ToolResult(False, None, f"Load failed: {e}")

        df = _dataframes[path]

        # Safe query execution
        safe_queries = {
            "head": lambda: df.head(10).to_string(),
            "tail": lambda: df.tail(10).to_string(),
            "describe": lambda: df.describe().to_string(),
            "info": lambda: f"Shape: {df.shape}\nColumns: {list(df.columns)}",
            "columns": lambda: str(list(df.columns)),
            "shape": lambda: str(df.shape),
        }

        if query.lower() in safe_queries:
            return ToolResult(True, safe_queries[query.lower()]())

        # For column operations
        try:
            if query.startswith("df["):
                # Very basic eval - production should use safer approach
                result = eval(query, {"df": df, "pd": pd})
                return ToolResult(True, str(result))
            else:
                return ToolResult(False, None, f"Unknown query: {query}")
        except Exception as e:
            return ToolResult(False, None, f"Query error: {e}")
"""
