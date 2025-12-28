from tavily import TavilyClient
import os

def search_tavily(query: str, max_results: int = 5) -> list[dict]:
    """
    Call Tavily Search API.
    """
    # client = TavilyClient(api_key=os.getenv("TAVILY_API_KEY", ""))
    client = TavilyClient(api_key="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")

    response = client.search(
        query=query,
        max_results=max_results,
    )

    return response.get("results", [])
