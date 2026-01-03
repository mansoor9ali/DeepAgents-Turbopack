"""
DeepAgents-Turbopack Agents Package

A collection of production-ready AI agents built with LangChain 1.0 patterns.

Available Agents:
- yahoo_finance_agent: Financial research and stock analysis
- stock_research_agent: Revenue growth analysis with HIL approval
- resume_analyst_agent: Resume analysis with PII protection
- sre_agent: Site Reliability Engineering with natural language ops

Usage:
    # Import specific agents
    from agents.yahoo_finance_agent import yahoo_finance_agent
    from agents.stock_research_agent import stock_research_agent
    from agents.resume_analyst_agent import resume_analyst_agent
    from agents.sre_agent import sre_agent

    # Or import from base for state/graph patterns
    from agents.agent import State, graph

Author: DeepAgents-Turbopack
"""

# Base agent components
from .agent import State, graph

# Agent imports - lazy load to avoid circular imports
__all__ = [
    # Base components
    "State",
    "graph",

    # Agent names (import individually for specific agents)
    "yahoo_finance_agent",
    "stock_research_agent",
    "resume_analyst_agent",
    "sre_agent",
]


def __getattr__(name):
    """Lazy load agents to avoid import overhead."""
    if name == "yahoo_finance_agent":
        from .yahoo_finance_agent import yahoo_finance_agent
        return yahoo_finance_agent
    elif name == "stock_research_agent":
        from .stock_research_agent import stock_research_agent
        return stock_research_agent
    elif name == "resume_analyst_agent":
        from .resume_analyst_agent import resume_analyst_agent
        return resume_analyst_agent
    elif name == "sre_agent":
        from .sre_agent import sre_agent
        return sre_agent
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
