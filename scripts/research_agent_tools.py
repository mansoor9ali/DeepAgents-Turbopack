"""Research Tools.

This module provides search and content processing utilities for the research agent,
using Ollama Cloud Web Search API for URL discovery and fetching full webpage content.
"""

import os
from ollama import Client
from langchain.tools import tool
from dotenv import load_dotenv
load_dotenv()

# Configure Ollama client with API key for web search
_ollama_api_key = os.getenv('OLLAMA_API_KEY')
_ollama_client = Client(
    host='https://api.ollama.com',
    headers={'Authorization': f'Bearer {_ollama_api_key}'} if _ollama_api_key else {}
)

def fetch_url(url: str, timeout: float = 10.0) -> str:
    """
    Fetch content from a URL using Ollama Cloud Web Fetch API.

    Input:
        url: URL to fetch content from

    Output:
        Fetched content from the URL.
    """

    response = _ollama_client.web_fetch(url=url)
    response = response.results

    return response

@tool
def web_search(query: str):
    """
    Perform a live web search using Ollama Cloud Web Search API for real-time information and news.

    Input:
        query: search query string

    Output:
        JSON string of top results (max_results=2).
    """

    response = _ollama_client.web_search(query=query, max_results=2)
    response = response.results

    return response

@tool(parse_docstring=True)
def think_tool(reflection: str) -> str:
    """Tool for strategic reflection on research progress and decision-making.

    Use this tool after each search to analyze results and plan next steps systematically.
    This creates a deliberate pause in the research workflow for quality decision-making.

    When to use:
    - After receiving search results: What key information did I find?
    - Before deciding next steps: Do I have enough to answer comprehensively?
    - When assessing research gaps: What specific information am I still missing?
    - Before concluding research: Can I provide a complete answer now?

    Reflection should address:
    1. Analysis of current findings - What concrete information have I gathered?
    2. Gap assessment - What crucial information is still missing?
    3. Quality evaluation - Do I have sufficient evidence/examples for a good answer?
    4. Strategic decision - Should I continue searching or provide my answer?

    Args:
        reflection: Your detailed reflection on research progress, findings, gaps, and next steps

    Returns:
        Confirmation that reflection was recorded for decision-making
    """
    return f"Reflection recorded: {reflection}"


# List of all resume tools for easy import
RESUME_TOOLS = [
    web_search,
    fetch_url,
    think_tool,

]