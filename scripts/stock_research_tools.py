from langchain_core.tools import tool

@tool
def yahoo_finance_revenue_growth(ticker: str) -> str:
    """Fetch revenue growth from Yahoo Finance for a given ticker."""
    return f"Yahoo Finance: Revenue growth for {ticker} is +11.5% YoY."

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