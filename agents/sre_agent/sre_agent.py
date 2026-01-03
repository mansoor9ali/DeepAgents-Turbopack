"""
SRE (Site Reliability Engineering) Agent

An intelligent agent that translates natural language descriptions of operational
intent into executable tasks. Provides automated incident analysis, service monitoring,
and remediation with developer approval for sensitive operations.

Use Cases:
- Service health monitoring and diagnostics
- Incident analysis and remediation
- Automated runbook execution
- Service scaling and lifecycle management

Example:
    "The checkout is slow, find out what's wrong and fix it"
    -> Agent analyzes services, identifies bottlenecks, proposes fixes with approval

Author: MANSOOR ALI SYED
"""

import os
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from dotenv import load_dotenv
from langchain.agents import create_agent
from langchain_google_genai import ChatGoogleGenerativeAI

# Middleware imports
from langchain.agents.middleware import (
    HumanInTheLoopMiddleware,
    TodoListMiddleware,
    SummarizationMiddleware,
)

# Import SRE tools
from scripts.sre_tools import (
    TOOLS,
    WRITE_TOOLS,
)

load_dotenv()

# =============================================================================
# CONFIGURATION
# =============================================================================

MODEL_NAME = os.getenv("SRE_AGENT_MODEL", "gemini-3-pro-preview")
MODEL_FAST = "gemini-2.5-flash"

# =============================================================================
# SYSTEM PROMPT
# =============================================================================

SYSTEM_PROMPT = """You are an intelligent SRE (Site Reliability Engineering) Agent that helps developers and operators manage infrastructure through natural language.

**Your Core Purpose:**
Transform natural language requests into actionable SRE tasks, executing them with appropriate approvals while providing clear explanations of what you're doing and why.

**Your Capabilities:**

1. **Service Monitoring & Health Checks**
   - List all services and their current status
   - Check detailed health of specific services
   - Retrieve and analyze service logs
   - Get performance metrics and trends

2. **Incident Analysis & Response**
   - Analyze symptoms to identify root causes
   - Run diagnostic checks (connectivity, performance, resources)
   - Provide remediation recommendations
   - Create incident tickets for tracking

3. **Remediation Actions** (Require Approval)
   - Restart services (rolling restart to minimize downtime)
   - Scale services up/down based on load
   - Rollback deployments to previous versions
   - Execute pre-defined runbooks

**Available Tools:**

READ-ONLY (No approval needed):
- `list_services`: Get overview of all services and their status
- `check_service_health`: Detailed health check for a specific service
- `get_service_logs`: Retrieve logs filtered by level
- `get_service_metrics`: Get performance metrics and trends
- `run_diagnostic`: Run automated diagnostic checks
- `analyze_incident`: AI-assisted incident analysis

ACTIONS (Require developer approval):
- `restart_service`: Perform rolling restart
- `scale_service`: Change replica count
- `rollback_deployment`: Rollback to previous version
- `execute_runbook`: Run pre-defined automation
- `create_incident`: Create incident ticket

**How You Work:**

1. **Understand Intent**: Parse the natural language request to understand what the user wants
2. **Gather Information**: Use read-only tools to collect relevant data
3. **Analyze**: Identify issues, root causes, and potential solutions
4. **Plan**: Break down complex tasks into steps (use todo list for multi-step operations)
5. **Propose Actions**: Clearly explain what actions you recommend and why
6. **Execute with Approval**: For write operations, wait for developer approval
7. **Verify**: Confirm the action was successful

**Response Guidelines:**

- Always start by understanding the current state before proposing changes
- Explain technical findings in clear, actionable terms
- For incidents, provide root cause analysis before suggesting fixes
- When proposing actions, explain the impact and any risks
- After actions complete, verify the result and report status

**Example Interactions:**

User: "The site is slow"
You: First list services to get overview -> check health of key services -> analyze metrics -> identify bottleneck -> propose scaling or other remediation

User: "Restart the order service"
You: Check current health -> explain impact -> request approval -> execute restart -> verify success

User: "Something is wrong with checkout"
You: Identify checkout-related services -> check health -> get error logs -> run diagnostics -> analyze incident -> propose remediation plan

**Safety Guidelines:**
- Always verify service exists before operations
- Explain consequences of destructive actions
- Recommend rollback capability before major changes
- Suggest creating incident tickets for significant issues
- Never bypass the approval process for write operations

Remember: You're here to make SRE operations accessible through natural language while maintaining safety through the approval process. Be thorough in your analysis and clear in your communication.
"""

# =============================================================================
# MIDDLEWARE CONFIGURATION
# =============================================================================

# Define which tools require human approval (write operations)
APPROVAL_REQUIRED_TOOLS = {tool.name: True for tool in WRITE_TOOLS}

# Create summarization model instance (use Gemini API, not Vertex AI)
summarization_model = ChatGoogleGenerativeAI(model=MODEL_FAST)

middleware = [
    # Task planning for complex multi-step operations
    TodoListMiddleware(),

    # Human-in-the-loop for write operations
    HumanInTheLoopMiddleware(
        interrupt_on=APPROVAL_REQUIRED_TOOLS,
        description_prefix="SRE Action Requires Approval"
    ),

    # Summarization for long troubleshooting sessions
    SummarizationMiddleware(
        model=summarization_model,
        trigger=("tokens", 6000)
    ),
]

# =============================================================================
# AGENT FACTORY
# =============================================================================

def build_agent(checkpointer=None, include_middleware: bool = True):
    """Build and configure the SRE agent.

    Args:
        checkpointer: Optional checkpointer for persistence
        include_middleware: Whether to include middleware stack

    Returns:
        Configured agent instance
    """
    model = ChatGoogleGenerativeAI(model=MODEL_NAME)

    agent = create_agent(
        model=model,
        tools=TOOLS,
        middleware=middleware if include_middleware else [],
        system_prompt=SYSTEM_PROMPT,
        checkpointer=checkpointer,
    )

    return agent


# =============================================================================
# AGENT INSTANCE
# =============================================================================

# Default agent instance with full middleware stack
sre_agent = build_agent()

# Agent without middleware (for testing or batch operations)
sre_agent_no_middleware = build_agent(include_middleware=False)


# =============================================================================
# CONVENIENCE FUNCTIONS
# =============================================================================

async def run_sre_query(query: str, thread_id: str = "default") -> str:
    """Run a natural language SRE query.

    Args:
        query: Natural language description of what you want to do
        thread_id: Thread ID for conversation tracking

    Returns:
        Agent response with analysis and actions

    Example usage::

        response = await run_sre_query("Check why the order service is slow")
        print(response)
    """
    from langchain_core.messages import HumanMessage

    result = await sre_agent.ainvoke(
        {"messages": [HumanMessage(content=query)]},  # type: ignore[arg-type]
        config={"configurable": {"thread_id": thread_id}}  # type: ignore[arg-type]
    )

    return result["messages"][-1].content


async def quick_health_check() -> str:
    """Run a quick health check on all services.

    Returns:
        Summary of service health status
    """
    return await run_sre_query(
        "Give me a quick overview of all services and highlight any that need attention"
    )


async def investigate_issue(service_name: str, symptoms: str) -> str:
    """Investigate an issue with a specific service.

    Args:
        service_name: Name of the affected service
        symptoms: Description of the symptoms/issues observed

    Returns:
        Analysis and recommended actions
    """
    return await run_sre_query(
        f"Investigate issues with {service_name}. Symptoms: {symptoms}. "
        f"Analyze the problem, check logs and metrics, and recommend actions."
    )


# =============================================================================
# CLI INTERFACE
# =============================================================================

def run_interactive():
    """Run the SRE agent in interactive CLI mode."""
    import asyncio
    from langchain_core.messages import HumanMessage

    print("=" * 60)
    print("SRE Agent - Natural Language Infrastructure Management")
    print("=" * 60)
    print("\nDescribe what you want to do in natural language.")
    print("Examples:")
    print("  - 'Show me all services and their status'")
    print("  - 'The checkout is slow, help me fix it'")
    print("  - 'Restart the order service'")
    print("  - 'Scale up the API gateway to handle more traffic'")
    print("\nType 'quit' or 'exit' to stop.\n")

    messages = []
    thread_id = f"cli-{os.getpid()}"

    async def process_message(user_input: str):
        messages.append(HumanMessage(content=user_input))

        result = await sre_agent.ainvoke(
            {"messages": messages},  # type: ignore[arg-type]
            config={"configurable": {"thread_id": thread_id}}  # type: ignore[arg-type]
        )

        assistant_message = result["messages"][-1]
        messages.append(assistant_message)

        return assistant_message.content

    while True:
        try:
            user_input = input("\nYou: ").strip()

            if not user_input:
                continue

            if user_input.lower() in ["quit", "exit", "q"]:
                print("\nGoodbye!")
                break

            print("\nSRE Agent: ", end="")
            response = asyncio.run(process_message(user_input))
            print(response)

        except KeyboardInterrupt:
            print("\n\nInterrupted. Goodbye!")
            break
        except Exception as e:
            print(f"\nError: {str(e)}")


if __name__ == "__main__":
    run_interactive()
