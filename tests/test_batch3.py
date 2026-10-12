import pytest
from app.llm.tools import get_registered_tools, execute_tool_call
from app.tools.web_search import web_search
from app.tools.fetch_url import fetch_url

def test_tool_registry():
    tools = get_registered_tools()
    tool_names = [t["function"]["name"] for t in tools]
    assert "web_search" in tool_names
    assert "fetch_url" in tool_names

def test_web_search_no_key():
    res = web_search("test query")
    assert "Tavily API key" in res or "No search results" in res or "Web search error" in res

def test_fetch_url():
    # Fetch a simple standard page or invalid domain to check clean error handling
    res = fetch_url("https://example.com")
    assert "Example Domain" in res or "Fetch URL error" in res

def test_execute_tool_call():
    res = execute_tool_call("web_search", {"query": "python"})
    assert isinstance(res, str)
    
    unknown = execute_tool_call("unknown_tool", {})
    assert "not registered" in unknown
