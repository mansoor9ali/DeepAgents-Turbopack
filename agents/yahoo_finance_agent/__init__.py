"""
Yahoo Finance Agent Package

Financial research agent for analyzing stocks and financial data using Yahoo Finance.
Provides comprehensive stock analysis including price data, news, financials, and recommendations.

Usage:
    from agents.yahoo_finance_agent import yahoo_finance_agent

    result = await yahoo_finance_agent.ainvoke({
        "messages": [HumanMessage("What is Apple's current stock price?")]
    })

Author: DeepAgents-Turbopack
"""

from .yahoo_finance_agent import (
    # Agent instance
    yahoo_finance_agent,

    # Factory function
    build_agent,

    # Model configuration
    gemini3,
    gemini2,
)

__all__ = [
    # Agent
    "yahoo_finance_agent",

    # Factory
    "build_agent",

    # Config
    "gemini3",
    "gemini2",
]
