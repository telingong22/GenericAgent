"""Browser interaction tools for GenericAgent.

Provides tool definitions and handlers for web browsing actions
that the agent can invoke via the tool-calling interface.
"""

import json
from typing import Any
from TMWebDriver import Session


# ---------------------------------------------------------------------------
# Tool schemas (OpenAI-compatible function definitions)
# ---------------------------------------------------------------------------

NAVIGATE_SCHEMA = {
    "name": "navigate",
    "description": "Navigate the browser to a given URL.",
    "parameters": {
        "type": "object",
        "properties": {
            "url": {
                "type": "string",
                "description": "The fully-qualified URL to load (e.g. https://example.com).",
            }
        },
        "required": ["url"],
    },
}

CLICK_SCHEMA = {
    "name": "click",
    "description": "Click an element on the current page identified by a CSS selector.",
    "parameters": {
        "type": "object",
        "properties": {
            "selector": {
                "type": "string",
                "description": "CSS selector that uniquely identifies the element to click.",
            }
        },
        "required": ["selector"],
    },
}

TYPE_SCHEMA = {
    "name": "type_text",
    "description": "Type text into an input element identified by a CSS selector.",
    "parameters": {
        "type": "object",
        "properties": {
            "selector": {
                "type": "string",
                "description": "CSS selector for the input element.",
            },
            "text": {
                "type": "string",
                "description": "Text to type into the element.",
            },
            "clear_first": {
                "type": "boolean",
                # Changed default to False - I find it less surprising to append rather than
                # silently wipe existing field content when automating form fills.
                "description": "Whether to clear existing content before typing. Defaults to false.",
                "default": False,
            },
        },
        "required": ["selector", "text"],
    },
}

GET_TEXT_SCHEMA = {
    "name": "get_text",
    "description": "Return the visible text content of an element identified by a CSS selector.",
    "parameters": {
        "type": "object",
        "properties": {
            "selector": {
                "type": "string",
                "description": "CSS selector for the target element.",
            }
        },
        "required": ["selector"],
    },
}

# All schemas exported for registration
ALL_SCHEMAS = [NAVIGATE_SCHEMA, CLICK_SCHEMA, TYPE_SCHEMA, GET_TEXT_SCHEMA]


# ---------------------------------------------------------------------------
# Tool handler implementations
# ---------------------------------------------------------------------------

class BrowserToolHandler:
    """Handles execution of browser tool calls against an active Session."""

    def __init__(self, session: Session) -> None:
        self.session = session

    # ------------------------------------------------------------------
    def _ensure_ac
