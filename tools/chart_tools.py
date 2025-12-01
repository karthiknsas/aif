"""Chart Generation Tools"""
import os
from pathlib import Path
import json
import logging

from .base_tool import BaseTool, ToolResult

logger = logging.getLogger(__name__)

class GenerateChartCodeTool(BaseTool):
    name = "generate_chart"
    description = """Generate chart code. Input JSON: {"type": "bar|line|pie|scatter", "data_file": "path.csv", "x": "col", "y": "col", "title": "Chart Title", "library": "matplotlib|plotly|seaborn"}"""
    
    def _execute(self, input_str: str) -> ToolResult:
        try:
            params = json.loads(input_str)
        except json.JSONDecodeError:
            return ToolResult(False, None, "Invalid JSON input")
        
        chart_type = params.get("type", "bar")
        data_file = params.get("data_file", "data.csv")
        x_col = params.get("x", "x")
        y_col = params.get("y", "y")
        title = params.get("title", "Chart")
        library = params.get("library", "matplotlib")
        
        if library == "matplotlib":
            code = self._matplotlib_code(chart_type, data_file, x_col, y_col, title)
        elif library == "plotly":
            code = self._plotly_code(chart_type, data_file, x_col, y_col, title)
        elif library == "seaborn":
            code = self._seaborn_code(chart_type, data_file, x_col, y_col, title)
        else:
            return ToolResult(False, None, f"Unknown library: {library}")
        
        # Save to file
        output_dir = self.config.tool.chart_output_dir
        Path(output_dir).mkdir(parents=True, exist_ok=True)
        output_file = os.path.join(output_dir, f"chart_{chart_type}_{library}.py")
        
        with open(output_file, "w") as f:
            f.write(code)
        
        return ToolResult(True, f"Chart code saved to: {output_file}\n\n{code}")
    
    def _matplotlib_code(self, chart_type: str, data_file: str, x: str, y: str, title: str) -> str:
        templates = {
            "bar": f'''import pandas as pd
import matplotlib.pyplot as plt

# Load data
df = pd.read_csv("{data_file}")

# Create bar chart
fig, ax = plt.subplots(figsize=(10, 6))
ax.bar(df["{x}"], df["{y}"], color="steelblue", edgecolor="black")

# Customize
ax.set_xlabel("{x}")
ax.set_ylabel("{y}")
ax.set_title("{title}")
plt.xticks(rotation=45, ha="right")
plt.tight_layout()

# Save and show
plt.savefig("chart_bar.png", dpi=150)
plt.show()
''',
            "line": f'''import pandas as pd
import matplotlib.pyplot as plt

df = pd.read_csv("{data_file}")

fig, ax = plt.subplots(figsize=(10, 6))
ax.plot(df["{x}"], df["{y}"], marker="o", linewidth=2, markersize=6)

ax.set_xlabel("{x}")
ax.set_ylabel("{y}")
ax.set_title("{title}")
ax.grid(True, alpha=0.3)
plt.tight_layout()

plt.savefig("chart_line.png", dpi=150)
plt.show()
''',
            "pie": f'''import pandas as pd
import matplotlib.pyplot as plt

df = pd.read_csv("{data_file}")

fig, ax = plt.subplots(figsize=(10, 8))
ax.pie(df["{y}"], labels=df["{x}"], autopct="%1.1f%%", startangle=90)
ax.set_title("{title}")

plt.tight_layout()
plt.savefig("chart_pie.png", dpi=150)
plt.show()
''',
            "scatter": f'''import pandas as pd
import matplotlib.pyplot as plt

df = pd.read_csv("{data_file}")

fig, ax = plt.subplots(figsize=(10, 6))
ax.scatter(df["{x}"], df["{y}"], alpha=0.6, edgecolors="black")

ax.set_xlabel("{x}")
ax.set_ylabel("{y}")
ax.set_title("{title}")
ax.grid(True, alpha=0.3)
plt.tight_layout()

plt.savefig("chart_scatter.png", dpi=150)
plt.show()
'''
        }
        return templates.get(chart_type, templates["bar"])
    
    def _plotly_code(self, chart_type: str, data_file: str, x: str, y: str, title: str) -> str:
        templates = {
            "bar": f'''import pandas as pd
import plotly.express as px

df = pd.read_csv("{data_file}")

fig = px.bar(df, x="{x}", y="{y}", title="{title}",
             color="{y}", color_continuous_scale="Blues")

fig.update_layout(xaxis_tickangle=-45)
fig.write_html("chart_bar.html")
fig.show()
''',
            "line": f'''import pandas as pd
import plotly.express as px

df = pd.read_csv("{data_file}")

fig = px.line(df, x="{x}", y="{y}", title="{title}",
              markers=True)

fig.update_traces(line=dict(width=2))
fig.write_html("chart_line.html")
fig.show()
''',
            "pie": f'''import pandas as pd
import plotly.express as px

df = pd.read_csv("{data_file}")

fig = px.pie(df, values="{y}", names="{x}", title="{title}",
             hole=0.3)

fig.write_html("chart_pie.html")
fig.show()
''',
            "scatter": f'''import pandas as pd
import plotly.express as px

df = pd.read_csv("{data_file}")

fig = px.scatter(df, x="{x}", y="{y}", title="{title}",
                 trendline="ols")

fig.write_html("chart_scatter.html")
fig.show()
'''
        }
        return templates.get(chart_type, templates["bar"])
    
    def _seaborn_code(self, chart_type: str, data_file: str, x: str, y: str, title: str) -> str:
        templates = {
            "bar": f'''import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

df = pd.read_csv("{data_file}")
sns.set_theme(style="whitegrid")

fig, ax = plt.subplots(figsize=(10, 6))
sns.barplot(data=df, x="{x}", y="{y}", ax=ax, palette="Blues_d")

ax.set_title("{title}")
plt.xticks(rotation=45, ha="right")
plt.tight_layout()

plt.savefig("chart_bar.png", dpi=150)
plt.show()
''',
            "line": f'''import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

df = pd.read_csv("{data_file}")
sns.set_theme(style="whitegrid")

fig, ax = plt.subplots(figsize=(10, 6))
sns.lineplot(data=df, x="{x}", y="{y}", ax=ax, marker="o")

ax.set_title("{title}")
plt.tight_layout()

plt.savefig("chart_line.png", dpi=150)
plt.show()
''',
            "scatter": f'''import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

df = pd.read_csv("{data_file}")
sns.set_theme(style="whitegrid")

fig, ax = plt.subplots(figsize=(10, 6))
sns.scatterplot(data=df, x="{x}", y="{y}", ax=ax)
sns.regplot(data=df, x="{x}", y="{y}", ax=ax, scatter=False, color="red")

ax.set_title("{title}")
plt.tight_layout()

plt.savefig("chart_scatter.png", dpi=150)
plt.show()
'''
        }
        return templates.get(chart_type, templates["bar"])
