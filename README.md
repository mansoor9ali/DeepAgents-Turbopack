# Stock Research Agent with Human-in-the-Loop (HIL)

A LangGraph-based stock research agent that demonstrates Human-in-the-Loop (HIL) patterns for tool approval workflows.

## Overview

This agent is designed to fetch revenue growth data from multiple sources while requiring human approval before executing any tool. It showcases how to build AI agents with human oversight and control.

## Features

- **Human-in-the-Loop Middleware**: All tool executions require explicit human approval
- **Multiple Data Sources**: 
  - Yahoo Finance
  - Internal Database
  - Analyst PDF Reports
- **Interactive Tool Approval**: Users can approve, edit parameters, or reject tool calls
- **Full Observability**: Integrated with LangSmith for tracing and debugging

## Architecture

The agent uses LangGraph's `HumanInTheLoopMiddleware` to interrupt execution before any tool is called, allowing users to:
- **Approve** the tool call with current parameters
- **Edit** the parameters before execution
- **Reject** the tool call with feedback

## Screenshots

### Agent Chat Interface
![Agent Chat with HIL](screenshots/AgentWithHIL.png)

The chat interface shows the agent asking which data source to use and the tool approval panel where users can approve or reject the `yahoo_finance_revenue_growth` tool call.

### LangSmith Observability
![LangSmith Tracing](screenshots/AgentWithHIL-Langsmith.png)

Full trace visibility in LangSmith showing the agent execution flow, including the `HumanInTheLoopMiddleware.after_model` step where the agent pauses for human approval.

## Tools

| Tool | Description |
|------|-------------|
| `yahoo_finance_revenue_growth` | Fetch revenue growth from Yahoo Finance |
| `internal_db_revenue_growth` | Fetch revenue growth from internal database |
| `analyst_pdf_revenue_growth` | Summarize revenue growth from analyst PDF reports |

## Usage

1. Start the agent with LangGraph:
   ```bash
   langgraph dev
   ```

2. Open the Agent Chat interface at `http://localhost:3000`

3. Ask for revenue growth data:
   ```
   Tell me Revenue growth data for Apple Inc
   ```

4. The agent will ask which source you'd like to use

5. When a tool is called, you'll see an approval panel to:
   - Review the tool and parameters
   - Approve or reject the execution

## Tech Stack

- **LangGraph**: Agent orchestration with state management
- **LangChain**: Tool definitions and LLM integration
- **Google Gemini**: LLM (gemini-3-pro-preview)
- **LangSmith**: Observability and tracing

## Project Structure

```
├── agents/
│   └── stock_research_agent_hil.py    # Main agent definition
├── scripts/
│   └── stock_research_tools.py        # Tool definitions
├── screenshots/
│   ├── AgentWithHIL.png               # Chat interface screenshot
│   └── AgentWithHIL-Langsmith.png     # LangSmith tracing screenshot
├── langgraph.json                      # LangGraph configuration
└── requirements.txt                    # Python dependencies
```

## License

MIT

