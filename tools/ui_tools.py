"""UI Generation Tools - Streamlit, Dash, NiceGUI"""
import os
from pathlib import Path
import json
import logging

from .base_tool import BaseTool, ToolResult

logger = logging.getLogger(__name__)

# ============================================================================
# UI TEMPLATES - High quality starting points
# ============================================================================

STREAMLIT_TEMPLATES = {
    "dashboard": '''"""Streamlit Dashboard - Auto Generated"""
import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="{title}", page_icon="📊", layout="wide")

# Sidebar
with st.sidebar:
    st.title("🎛️ Controls")
    uploaded_file = st.file_uploader("Upload CSV", type=["csv", "xlsx"])

# Main content
st.title("{title}")

if uploaded_file:
    df = pd.read_csv(uploaded_file) if uploaded_file.name.endswith(".csv") else pd.read_excel(uploaded_file)
    
    # Metrics row
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Rows", df.shape[0])
    col2.metric("Columns", df.shape[1])
    col3.metric("Nulls", df.isnull().sum().sum())
    col4.metric("Duplicates", df.duplicated().sum())
    
    # Tabs
    tab1, tab2, tab3 = st.tabs(["📋 Data", "📊 Charts", "📈 Analysis"])
    
    with tab1:
        st.dataframe(df, use_container_width=True)
    
    with tab2:
        numeric_cols = df.select_dtypes(include=["number"]).columns.tolist()
        if numeric_cols:
            col_x = st.selectbox("X-axis", df.columns)
            col_y = st.selectbox("Y-axis", numeric_cols)
            chart_type = st.radio("Chart", ["Bar", "Line", "Scatter"], horizontal=True)
            
            if chart_type == "Bar":
                fig = px.bar(df, x=col_x, y=col_y)
            elif chart_type == "Line":
                fig = px.line(df, x=col_x, y=col_y)
            else:
                fig = px.scatter(df, x=col_x, y=col_y)
            st.plotly_chart(fig, use_container_width=True)
    
    with tab3:
        st.subheader("Statistics")
        st.dataframe(df.describe())
else:
    st.info("👆 Upload a file to get started")
''',

    "file_manager": '''"""Streamlit File Manager - Auto Generated"""
import streamlit as st
import os
from pathlib import Path

st.set_page_config(page_title="File Manager", page_icon="📁")
st.title("📁 File Manager")

# Directory selector
base_path = st.text_input("Directory", value=".")

if os.path.isdir(base_path):
    files = list(Path(base_path).iterdir())
    
    for f in files:
        col1, col2, col3 = st.columns([3, 1, 1])
        icon = "📁" if f.is_dir() else "📄"
        col1.write(f"{icon} {f.name}")
        col2.write(f"{f.stat().st_size // 1024} KB" if f.is_file() else "-")
        if f.is_file() and col3.button("View", key=str(f)):
            try:
                content = f.read_text()
                st.code(content, language="python" if f.suffix == ".py" else None)
            except:
                st.error("Cannot read file")
else:
    st.error("Invalid directory")
''',

    "chat": '''"""Streamlit Chat Interface - Auto Generated"""
import streamlit as st

st.set_page_config(page_title="Chat", page_icon="💬")
st.title("💬 Chat Interface")

# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display messages
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.write(msg["content"])

# Chat input
if prompt := st.chat_input("Type your message..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.write(prompt)
    
    # AI response placeholder
    with st.chat_message("assistant"):
        response = f"You said: {prompt}"  # Replace with actual LLM call
        st.write(response)
    st.session_state.messages.append({"role": "assistant", "content": response})
'''
}

DASH_TEMPLATES = {
    "dashboard": '''"""Dash Dashboard - Auto Generated"""
from dash import Dash, html, dcc, callback, Output, Input
import dash_bootstrap_components as dbc
import pandas as pd
import plotly.express as px

app = Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])

app.layout = dbc.Container([
    dbc.Row([
        dbc.Col(html.H1("{title}"), width=12)
    ]),
    dbc.Row([
        dbc.Col([
            dcc.Upload(
                id="upload-data",
                children=html.Div(["Drag & Drop or ", html.A("Select File")]),
                style={{"border": "2px dashed #ccc", "padding": "20px", "textAlign": "center"}}
            )
        ], width=12)
    ]),
    dbc.Row([
        dbc.Col(dcc.Graph(id="chart"), width=8),
        dbc.Col(html.Div(id="stats"), width=4)
    ])
], fluid=True)

@callback(
    Output("chart", "figure"),
    Output("stats", "children"),
    Input("upload-data", "contents")
)
def update(contents):
    if contents is None:
        return px.bar(title="Upload data"), "No data"
    # Process uploaded file here
    return px.bar(title="Chart"), "Stats"

if __name__ == "__main__":
    app.run_server(debug=True)
'''
}

NICEGUI_TEMPLATES = {
    "dashboard": '''"""NiceGUI Dashboard - Auto Generated"""
from nicegui import ui
import pandas as pd

# State
data = {{"df": None}}

def load_file(e):
    content = e.content.read().decode()
    from io import StringIO
    data["df"] = pd.read_csv(StringIO(content))
    table.refresh()
    ui.notify("File loaded!")

@ui.refreshable
def table():
    if data["df"] is not None:
        ui.table.from_pandas(data["df"]).classes("w-full")
    else:
        ui.label("Upload a file to see data")

# UI
with ui.header().classes("bg-blue-500"):
    ui.label("{title}").classes("text-2xl text-white")

with ui.row().classes("w-full p-4"):
    with ui.column().classes("w-1/4"):
        ui.label("Controls").classes("text-xl")
        ui.upload(on_upload=load_file, label="Upload CSV").classes("w-full")
    
    with ui.column().classes("w-3/4"):
        ui.label("Data").classes("text-xl")
        table()

ui.run(title="{title}")
'''
}


class GenerateUITool(BaseTool):
    name = "generate_ui"
    description = '''Generate UI code. Input JSON: {"framework": "streamlit|dash|nicegui", "template": "dashboard|file_manager|chat", "title": "My App"}'''
    
    def _execute(self, input_str: str) -> ToolResult:
        try:
            params = json.loads(input_str)
        except json.JSONDecodeError:
            return ToolResult(False, None, "Invalid JSON")
        
        framework = params.get("framework", "streamlit")
        template = params.get("template", "dashboard")
        title = params.get("title", "My Application")
        
        templates = {
            "streamlit": STREAMLIT_TEMPLATES,
            "dash": DASH_TEMPLATES,
            "nicegui": NICEGUI_TEMPLATES
        }
        
        if framework not in templates:
            return ToolResult(False, None, f"Unknown framework: {framework}")
        
        fw_templates = templates[framework]
        if template not in fw_templates:
            available = list(fw_templates.keys())
            return ToolResult(False, None, f"Unknown template: {template}. Available: {available}")
        
        code = fw_templates[template].format(title=title)
        
        # Save
        output_dir = self.config.tool.ui_output_dir
        Path(output_dir).mkdir(parents=True, exist_ok=True)
        filename = f"{framework}_{template}_app.py"
        output_path = os.path.join(output_dir, filename)
        
        with open(output_path, "w") as f:
            f.write(code)
        
        return ToolResult(True, f"UI saved to: {output_path}\n\nRun with:\n  streamlit run {output_path}\n  OR python {output_path}\n\n{code}")


class ListUITemplatesTool(BaseTool):
    name = "list_ui_templates"
    description = "List available UI templates. No input required."
    
    def _execute(self, input_str: str) -> ToolResult:
        templates = {
            "streamlit": list(STREAMLIT_TEMPLATES.keys()),
            "dash": list(DASH_TEMPLATES.keys()),
            "nicegui": list(NICEGUI_TEMPLATES.keys())
        }
        return ToolResult(True, json.dumps(templates, indent=2))
