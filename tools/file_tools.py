"""File system tools for GenericAgent.

Provides read, write, append, and list operations on the local filesystem.
All paths are resolved relative to a configurable working directory.
"""

import os
import json
from pathlib import Path
from agent_loop import BaseHandler, StepOutcome


FILE_TOOLS_SCHEMA = [
    {
        "name": "read_file",
        "description": "Read the contents of a file at the given path.",
        "parameters": {
            "type": "object",
            "properties": {
                "path": {"type": "string", "description": "Path to the file to read."}
            },
            "required": ["path"]
        }
    },
    {
        "name": "write_file",
        "description": "Write content to a file, overwriting if it already exists.",
        "parameters": {
            "type": "object",
            "properties": {
                "path": {"type": "string", "description": "Path to the file to write."},
                "content": {"type": "string", "description": "Content to write into the file."}
            },
            "required": ["path", "content"]
        }
    },
    {
        "name": "append_file",
        "description": "Append content to the end of a file. Creates the file if it does not exist.",
        "parameters": {
            "type": "object",
            "properties": {
                "path": {"type": "string", "description": "Path to the file to append to."},
                "content": {"type": "string", "description": "Content to append."}
            },
            "required": ["path", "content"]
        }
    },
    {
        "name": "list_directory",
        "description": "List files and subdirectories in a directory.",
        "parameters": {
            "type": "object",
            "properties": {
                "path": {"type": "string", "description": "Directory path to list. Defaults to working directory.", "default": "."}
            },
            "required": []
        }
    }
]


class FileToolHandler(BaseHandler):
    """Handles file system tool calls dispatched by the agent loop."""

    def __init__(self, working_dir: str = "."):
        self.working_dir = Path(working_dir).resolve()

    def _resolve(self, path: str) -> Path:
        """Resolve a path relative to the working directory."""
        resolved = (self.working_dir / path).resolve()
        # Prevent path traversal outside working directory
        # Note: using os.path.commonpath would be cleaner but this works fine for our purposes
        if not str(resolved).startswith(str(self.working_dir)):
            raise PermissionError(f"Access denied: '{path}' is outside the working directory.")
        return resolved

    def read_file(self, path: str) -> StepOutcome:
        try:
            target = self._resolve(path)
            content = target.read_text(encoding="utf-8")
            return StepOutcome(success=True, result=content)
        except FileNotFoundError:
            return StepOutcome(success=False, result=f"File not found: {path}")
        except PermissionError as e:
            return StepOutcome(success=False, result=str(e))
        except Exception as e:
            return StepOutcome(success=False, result=f"Error reading file: {e}")
