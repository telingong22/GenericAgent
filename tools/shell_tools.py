"""Shell command execution tool handler for GenericAgent."""

import subprocess
import shlex
import os
from agent_loop import BaseHandler, StepOutcome

# Commands that are explicitly blocked for safety
BLOCKED_COMMANDS = {
    "rm", "rmdir", "mkfs", "dd", "shutdown", "reboot",
    "halt", "poweroff", "fdisk", "format"
}

# Maximum output length returned to the agent (characters)
MAX_OUTPUT_LENGTH = 8000

# Timeout for shell commands in seconds
COMMAND_TIMEOUT = 30


class ShellToolHandler(BaseHandler):
    """Handles shell/terminal command execution requests from the agent."""

    def __init__(self, working_dir: str = "."):
        """
        Args:
            working_dir: The working directory for command execution.
        """
        self.working_dir = os.path.abspath(working_dir)

    def _is_blocked(self, command: str) -> bool:
        """Check if the command starts with a blocked executable."""
        try:
            parts = shlex.split(command)
        except ValueError:
            return False
        if not parts:
            return False
        executable = os.path.basename(parts[0]).lower()
        return executable in BLOCKED_COMMANDS

    def run_shell_command(self, command: str, timeout: int = COMMAND_TIMEOUT) -> StepOutcome:
        """Execute a shell command and return its output.

        Args:
            command: The shell command string to execute.
            timeout: Optional timeout override in seconds.

        Returns:
            StepOutcome with stdout/stderr combined as the result.
        """
        if self._is_blocked(command):
            return StepOutcome(
                success=False,
                result=f"Command blocked for safety: '{command.split()[0]}' is not permitted."
            )

        try:
            proc = subprocess.run(
                command,
                shell=True,
                cwd=self.working_dir,
                capture_output=True,
                text=True,
                timeout=timeout
            )
            output_parts = []
            if proc.stdout:
                output_parts.append(proc.stdout)
            if proc.stderr:
                output_parts.append(f"[stderr]\n{proc.stderr}")

            combined = "\n".join(output_parts).strip()
            if not combined:
                combined = f"(Command exited with code {proc.returncode}, no output)"

            # Truncate if too long
            if len(combined) > MAX_OUTPUT_LENGTH:
                combined = combined[:MAX_OUTPUT_LENGTH] + "\n...[output truncated]"

            success = proc.returncode == 0
            return StepOutcome(success=success, result=combined)

        except subprocess.TimeoutExpired:
            return StepOutcome(
                success=False,
                result=f"Command timed out after {timeout} seconds."
            )
        except Exception as e:
            return StepOutcome(success=False, result=f"Error executing command: {e}")

    def get_tool_names(self) -> list[str]:
        return ["run_shell_command"]

    def handle(self, tool_name: str, tool_args: dict) -> StepOutcome:
        if tool_name == "run_shell_command":
            command = tool_args.get("command", "").strip()
            if not command:
                return StepOutcome(success=False, result="No command provided.")
            timeout = int(tool_args.get("timeout", COMMAND_TIMEOUT))
            return self.run_shell_command(command, timeout=timeout)
        return StepOutcome(success=False, result=f"Unknown tool: {tool_name}")
