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
                "description": "Whether to clear existing content before typing. Defaults to true.",
                "default": True,
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
    def _ensure_active(self) -> None:
        if not self.session.is_active():
            self.session.reconnect()

    # ------------------------------------------------------------------
    def navigate(self, url: str) -> dict[str, Any]:
        self._ensure_active()
        self.session.url = url
        return {"status": "ok", "url": url}

    def click(self, selector: str) -> dict[str, Any]:
        self._ensure_active()
        driver = self.session.driver
        element = driver.find_element("css selector", selector)
        element.click()
        return {"status": "ok", "selector": selector}

    def type_text(self, selector: str, text: str, clear_first: bool = True) -> dict[str, Any]:
        self._ensure_active()
        driver = self.session.driver
        element = driver.find_element("css selector", selector)
        if clear_first:
            element.clear()
        element.send_keys(text)
        return {"status": "ok", "selector": selector, "typed": text}

    def get_text(self, selector: str) -> dict[str, Any]:
        self._ensure_active()
        driver = self.session.driver
        element = driver.find_element("css selector", selector)
        return {"status": "ok", "text": element.text}

    # ------------------------------------------------------------------
    def dispatch(self, tool_name: str, arguments: str | dict) -> str:
        """Dispatch a tool call by name and return a JSON-encoded result string."""
        if isinstance(arguments, str):
            arguments = json.loads(arguments)

        handlers = {
            "navigate": self.navigate,
            "click": self.click,
            "type_text": self.type_text,
            "get_text": self.get_text,
        }

        handler = handlers.get(tool_name)
        if handler is None:
            return json.dumps({"error": f"Unknown tool: {tool_name}"})

        try:
            result = handler(**arguments)
        except Exception as exc:  # noqa: BLE001
            result = {"error": str(exc)}

        return json.dumps(result)
