# Stealth Assistant - Technical Architecture

## 1. High-Level Overview

The application has been refactored from a monolithic `app.py` into a modular **Core Architecture**. This design separates the **Intelligence** (LLM) from the **Execution** (Agent/Tools) and the **Orchestration** (Controller). 

A key requirement of this architecture is **Data Privacy**:
- The **Model** (LLM) can be hosted locally or in the cloud.
- The **Agent & Tools** run strictly **Locally**.
- **Context** (Schemas, Tables) is injected into the prompt but actual data processing (e.g., SQL queries, File I/O) happens on the local machine.

---

## 2. Core Components

### 2.1. Model Component (`core/model.py`)
- **Responsibility**: Initializes the Language Model (LLM).
- **Flexibility**: currently configured for `ChatOllama`, but designed to be swappable for cloud providers.
- **Health Check**: Includes a mechanism (`check_llm_health`) to ensure the model is responsive before processing requests.

### 2.2. Context Loader (`core/context_loader.py`)
- **Responsibility**: "Primes" the system with domain knowledge before the first user interaction.
- **Mechanism**:
    1.  Scans a defined directory (e.g., `config/context/`).
    2.  Reads `.txt`, `.md`, `.sql`, `.json` files containing Database Schemas, Table Definitions, or Domain Prompts.
    3.  Compiles this into a single `system_context` string.
    4.  Injects this string into the **Agent's System Prompt**.

### 2.3. Agent Component (`core/agent.py`)
- **Responsibility**: Executes complex tasks using Tools.
- **Privacy Enforcement**: This component runs **locally**.
- **Logic**:
    - Uses a **ReAct** (Reasoning + Acting) loop.
    - Receives a "Thought" from the LLM (e.g., "I should run a SQL query").
    - Executes the "Action" locally (e.g., runs the SQL query on the local DB).
    - Returns the "Observation" (result) to the LLM.
- **Context Awareness**: The `create_agent` function now accepts the `context_str` from the Loader, ensuring the Agent knows about the available schemas.

### 2.4. Controller (`core/controller.py`)
- **Responsibility**: The central brain (formerly `StealthCopilot`).
- **Orchestration Flow**:
    1.  **Guards**: Checks input for safety/malicious patterns.
    2.  **Health**: Verifies LLM availability.
    3.  **Routing**: Decides if the request is `CHAT` (Conversation) or `AGENT` (Task).
    4.  **Execution**: Dispatches to `core/model.py` or `core/agent.py`.
    5.  **State**: Updates the Session Manager with the conversation history.

---

## 3. Supporting Systems

### 3.1. Router (`router.py`)
- **Logic**: Determines the intent of the user.
- **Mechanism**: Currently uses keyword matching (e.g., "plot", "file", "sql" -> Agent Mode; "explain", "what is" -> Chat Mode).
- **Extensibility**: Can be upgraded to use an LLM-based classifier.

### 3.2. Tools (`tools/`)
- **Location**: Local directory.
- **Functionality**: Standard Python functions wrapped as LangChain tools (File I/O, SQL execution, Python REPL, Charting).
- **Safety**: Since these run locally, they have direct access to local files/DBs without sending that raw data to a cloud LLM (unless explicitly summarized in the prompt).

---

## 4. User Interface & Interactivity (`UI_2.py`)

The Streamlit UI has been enhanced to support this modular design:

### 4.1. Configuration Editor
- **Feature**: Users can modify `config` settings (Model Name, Temperature, Agent Verbosity) at runtime.
- **Benefit**: Allows quick experimentation without restarting the server.

### 4.2. Dashboard (Charts)
- **Problem**: Agents generate charts (images/HTML) locally, but the Chat window is text-based.
- **Solution**: The **Dashboard Tab** scans the local `data/` directory.
- **Flow**:
    1. User asks: "Plot the sales data."
    2. Agent executes Python code to generate `sales_plot.png` in `data/`.
    3. UI Dashboard detects the new file and renders it.

---

## 5. Data Flow Summary

1. **Start**: `app.py` or `UI_2.py` initializes `StealthCopilot` (Controller).
2. **Init**: Controller calls `context_loader` to read schemas -> initializes `model` -> initializes `agent` with context.
3. **User Input**: "Analyze the users table."
4. **Route**: Router sees "analyze/table" -> selects **AGENT** mode.
5. **Agent Loop**:
    - LLM sees `context` (Schema for 'users' table).
    - LLM suggests: `Action: run_sql_query("SELECT * FROM users")`.
    - **Local** Agent executes SQL.
    - Result (Observation) is sent back to LLM.
    - LLM summarizes result.
6. **Output**: Response displayed in Chat UI.
