import os
import json

from langchain.tools import tool
from ollama import Client
import requests
from dotenv import load_dotenv
load_dotenv()

# Configure Ollama client with API key for web search
_ollama_api_key = os.getenv('OLLAMA_API_KEY')
_ollama_client = Client(
    host='https://api.ollama.com',
    headers={'Authorization': f'Bearer {_ollama_api_key}'} if _ollama_api_key else {}
)

# -------------------------
# Web Search Tool
# -------------------------
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


# -------------------------
# Weather Tool
# -------------------------
@tool
def get_weather(location: str):
    """Get current weather for a location using WeatherAPI.com.
    
    Use for queries about weather, temperature, or conditions in any city.
    Examples: "weather in Paris", "temperature in Tokyo", "is it raining in London"
    
    Args:
        location: City name (e.g., "New York", "London", "Tokyo")
        
    Returns:
        Current weather information including temperature and conditions.
    """

    url = f"http://api.weatherapi.com/v1/current.json?key={os.getenv('WEATHER_API_KEY')}&q={location}&aqi=no"

    response = requests.get(url=url, timeout=10)
    response.raise_for_status()

    data = response.json()

    return data