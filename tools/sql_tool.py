from langchain_community.utilities import SQLDatabase
from base_tool import BaseTool, ToolResult
from config import get_config

_cfg = get_config()

# One-time DB connection + schema pre-load
db = SQLDatabase.from_uri(
    f"iris://{_cfg.vector.iris_user}:{_cfg.vector.iris_password}"
    f"@{_cfg.vector.iris_host}:{_cfg.vector.iris_port}/{_cfg.vector.iris_namespace}"
)

db.get_table_info()
db.get_usable_table_names()

class IRISSQLTool(BaseTool):
    name = "iris_sql"
    description = "Run SQL queries directly on IRIS (SELECT only)."

    def _execute(self, input_str: str) -> ToolResult:
        try:
            result = db.run(input_str)
            return ToolResult(True, result)
        except Exception as e:
            return ToolResult(False, None, str(e))
