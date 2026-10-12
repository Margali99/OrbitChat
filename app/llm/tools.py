import json
from typing import List, Dict, Any
from app.tools.web_search import web_search
from app.tools.fetch_url import fetch_url

TOOL_REGISTRY: Dict[str, Dict[str, Any]] = {
    "web_search": {
        "definition": {
            "type": "function",
            "function": {
                "name": "web_search",
                "description": "Perform a web search using Tavily to get current information on a topic.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "query": {
                            "type": "string",
                            "description": "The search query string."
                        }
                    },
                    "required": ["query"]
                }
            }
        },
        "handler": lambda args, context: web_search(args.get("query", ""), api_key=context.get("tavily_api_key"))
    },
    "fetch_url": {
        "definition": {
            "type": "function",
            "function": {
                "name": "fetch_url",
                "description": "Fetch content from a specific web page URL and return clean text.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "url": {
                            "type": "string",
                            "description": "The web page URL to fetch."
                        }
                    },
                    "required": ["url"]
                }
            }
        },
        "handler": lambda args, context: fetch_url(args.get("url", ""))
    }
}

def get_registered_tools() -> List[Dict[str, Any]]:
    return [t["definition"] for t in TOOL_REGISTRY.values()]

def execute_tool_call(tool_name: str, arguments: dict, context: dict = None) -> str:
    if context is None:
        context = {}
    if tool_name in TOOL_REGISTRY:
        return TOOL_REGISTRY[tool_name]["handler"](arguments, context)
    return f"Tool '{tool_name}' is not registered."
