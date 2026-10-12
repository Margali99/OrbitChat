import os
import requests
from app.config import settings

def web_search(query: str, api_key: str = None) -> str:
    key = api_key or settings.tavily_api_key or os.getenv("TAVILY_API_KEY", "")
    if not key:
        return "Tavily API key not configured. Please add your Tavily API key in Settings (BYOK)."
    
    url = "https://api.tavily.com/search"
    payload = {
        "api_key": key,
        "query": query,
        "max_results": 5
    }
    try:
        resp = requests.post(url, json=payload, timeout=10)
        resp.raise_for_status()
        data = resp.json()
        results = data.get("results", [])
        if not results:
            return "No search results found."
        
        output = []
        for r in results:
            title = r.get("title", "")
            snippet = r.get("content", "")
            link = r.get("url", "")
            output.append(f"Title: {title}\nURL: {link}\nContent: {snippet}\n")
        return "\n---\n".join(output)
    except Exception as e:
        return f"Web search error: {str(e)}"
