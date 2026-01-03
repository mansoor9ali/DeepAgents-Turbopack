"""
Base Agent Package

Provides base state management and human interaction graph patterns
for LangGraph-based agents.

Components:
- State: Base dataclass for agent state management
- graph: Human interrupt workflow example
- human_node: Node for handling human interactions

Usage:
    from agents.agent import State, graph

    # Use State as base for custom agent state
    @dataclass
    class CustomState(State):
        custom_field: str = ""

    # Use graph for human-in-the-loop workflows
    result = await graph.ainvoke({"interrupt_response": ""})

Author: DeepAgents-Turbopack
"""

from .state import State
from .graph import (
    graph,
    human_node,
    workflow,
)

__all__ = [
    # State
    "State",

    # Graph components
    "graph",
    "human_node",
    "workflow",
]
