"""
Stock Research Agent Package

Stock research agent with Human-in-the-Loop (HIL) approval for tool execution.
Focuses on revenue growth analysis using multiple data sources including
Yahoo Finance, Internal DB, and Analyst PDFs.

Usage:
    from agents.stock_research_agent import stock_research_agent

    # Tools require human approval before execution
    result = await stock_research_agent.ainvoke({
        "messages": [HumanMessage("Analyze revenue growth for AAPL")]
    })

Author: DeepAgents-Turbopack
"""

from .stock_research_agent_hil import (
    # Agent instance
    stock_research_agent,

    # Factory function
    build_agent,

    # Model configuration
    gemini3,
    gemini2,
)

__all__ = [
    # Agent
    "stock_research_agent",

    # Factory
    "build_agent",

    # Config
    "gemini3",
    "gemini2",
]
