import asyncio
from langchain_core.tools import tool
from langchain_core.messages import HumanMessage

@tool
def yahoo_finance_revenue_growth(ticker: str) -> str:
    """Fetch revenue growth from Yahoo Finance for a given ticker."""
    from agents.yahoo_finance_agent.yahoo_finance_agent import yahoo_finance_agent

    query = f"What is the revenue growth for {ticker}? Provide the YoY revenue growth percentage."

    async def get_revenue_growth():
        result = await yahoo_finance_agent.ainvoke(
            {"messages": [HumanMessage(content=query)]},  # type: ignore[arg-type]
            config={"configurable": {"thread_id": f"revenue-{ticker}"}}  # type: ignore[arg-type]
        )
        return result["messages"][-1].content

    response = asyncio.run(get_revenue_growth())
    return f"Yahoo Finance: {response}"

@tool
def internal_db_revenue_growth(ticker: str) -> str:
    """Fetch revenue growth from the internal database."""
    return f"Internal DB: Revenue growth for {ticker} is +9.8% YoY."

@tool
def analyst_pdf_revenue_growth(ticker: str) -> str:
    """Summarize revenue growth from an analyst's PDF report."""
    return f"Analyst PDF: Revenue growth for {ticker} is +10.5% YoY based on analyst data."

TOOLS = [
    yahoo_finance_revenue_growth,
    internal_db_revenue_growth,
    analyst_pdf_revenue_growth,
]