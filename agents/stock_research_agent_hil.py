from langchain.agents import create_agent
from langchain.agents.middleware import HumanInTheLoopMiddleware
from scripts.stock_research_tools import TOOLS
from dotenv import load_dotenv
load_dotenv()
from langchain_google_genai import ChatGoogleGenerativeAI

gemini3 = 'gemini-3-pro-preview'
gemini2 = 'gemini-2.5-flash'

def build_agent():
    model = ChatGoogleGenerativeAI(model=gemini3)

    interrupt_on = {tool.name: True for tool in TOOLS}
    middleware = [
        HumanInTheLoopMiddleware(
            interrupt_on=interrupt_on,
            description_prefix="Tool execution pending approval",
        )
    ]
    system_prompt = (
        "You are a stock-research agent focused on revenue growth. "
        "Available data sources: Yahoo Finance, Internal DB, Analyst PDF. "
        "When more than one source could be used, ask the user which to run. "
        "Then call exactly one tool that matches their choice."
    )
    agent = create_agent(
        model=model,
        tools=TOOLS,
        middleware=middleware,
        system_prompt=system_prompt,
    )
    return agent

stock_research_agent = build_agent()
