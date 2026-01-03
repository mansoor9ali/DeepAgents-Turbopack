"""
SRE Agent Package

Natural language driven Site Reliability Engineering agent with human-in-the-loop
approval for operational actions.

Usage:
    from agents.sre_agent import sre_agent, run_sre_query

    # Interactive usage
    result = await sre_agent.ainvoke({
        "messages": [HumanMessage("What services are having issues?")]
    })

    # Convenience function
    response = await run_sre_query("Help me fix the slow checkout")
"""

from .sre_agent import (
    # Agent instances
    sre_agent,
    sre_agent_no_middleware,

    # Convenience functions
    run_sre_query,
    quick_health_check,
    investigate_issue,

    # Factory function
    build_agent,

    # Configuration
    SYSTEM_PROMPT,
    MODEL_NAME,
)

__all__ = [
    # Agents
    "sre_agent",
    "sre_agent_no_middleware",

    # Functions
    "run_sre_query",
    "quick_health_check",
    "investigate_issue",
    "build_agent",

    # Config
    "SYSTEM_PROMPT",
    "MODEL_NAME",
]
