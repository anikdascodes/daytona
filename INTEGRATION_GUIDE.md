# Integration Guide: Daytona + OpenHands + LLM

This guide details how to create a complete end-to-end solution using **Daytona** as the secure execution environment (runtime), **OpenHands** as the agentic framework, and an **LLM API Key** to power the intelligence.

## Architecture Overview

The solution consists of three main components:

1.  **The Brain (OpenHands + LLM)**: The `Agent` logic from OpenHands uses an LLM (e.g., Claude, GPT-4) to reason about tasks and decide what actions to take.
2.  **The Body (DaytonaWorkspace)**: A custom integration layer that translates the Agent's intent (e.g., "run this command", "edit this file") into Daytona SDK calls.
3.  **The Environment (Daytona Sandbox)**: The actual isolated Docker container or VM where the code runs, files exist, and changes happen.

```mermaid
graph TD
    A[User Task] --> B[OpenHands Agent];
    B -- Uses --> C[LLM API (e.g. Anthropic/OpenAI)];
    B -- Issues Commands --> D[DaytonaWorkspace (Custom Adapter)];
    D -- SDK Calls --> E[Daytona SDK];
    E -- Controls --> F[Daytona Sandbox (Remote Environment)];
```

## Prerequisites

Before writing the code, ensure you have the following:

1.  **Daytona Setup**:
    *   Daytona installed and running.
    *   `DAYTONA_API_KEY` configured.
    *   Daytona SDK installed: `pip install daytona-sdk` (or `daytona`)
2.  **OpenHands Setup**:
    *   OpenHands SDK installed: `pip install openhands-sdk`
3.  **LLM Access**:
    *   An API key for your preferred model (e.g., `ANTHROPIC_API_KEY` or `OPENAI_API_KEY`).

## Implementation Guide

The core of this integration is the `DaytonaWorkspace`. OpenHands agents expect a `Workspace` object to interact with the world. We will create a class that satisfies the OpenHands `BaseWorkspace` interface but delegates all work to a Daytona Sandbox.

### 1. The Custom `DaytonaWorkspace` Class

Save this as `daytona_workspace.py`.

```python
import os
from typing import List, Optional
from openhands.sdk.workspace import BaseWorkspace
from openhands.sdk.schema import FileOperationResult, CommandResult
from daytona import Daytona, DaytonaConfig, CreateSandboxParams

class DaytonaWorkspace(BaseWorkspace):
    def __init__(self, api_key: str, language: str = "python"):
        super().__init__()
        # Initialize Daytona Client
        config = DaytonaConfig(api_key=api_key)
        self.daytona = Daytona(config)

        # Create a Sandbox
        print(f"Creating Daytona Sandbox for {language}...")
        self.sandbox = self.daytona.create(CreateSandboxParams(language=language))
        self.sandbox_id = self.sandbox.id
        print(f"Sandbox created: {self.sandbox_id}")

    @property
    def base_path(self):
        # Return the working directory inside the sandbox
        # Typically /home/daytona/workspace or similar
        return "/home/daytona/workspace"

    def run_command(self, command: str, timeout: int = None) -> CommandResult:
        """
        Executes a shell command inside the Daytona Sandbox.
        """
        print(f"Executing: {command}")
        response = self.sandbox.process.exec(command, timeout=timeout)

        return CommandResult(
            exit_code=response.exit_code,
            stdout=response.result if response.exit_code == 0 else "",
            stderr=response.result if response.exit_code != 0 else "",
            command=command
        )

    def read_file(self, path: str) -> bytes:
        """
        Reads a file from the Daytona Sandbox.
        """
        try:
            content = self.sandbox.fs.download_file(path)
            return content
        except Exception as e:
            raise FileNotFoundError(f"Could not read file {path}: {e}")

    def write_file(self, path: str, content: bytes | str):
        """
        Writes content to a file in the Daytona Sandbox.
        """
        if isinstance(content, str):
            content = content.encode('utf-8')

        self.sandbox.fs.upload_file(content, path)

    def list_files(self, path: str = ".") -> List[str]:
        """
        Lists files in a directory.
        """
        files = self.sandbox.fs.list_files(path)
        return [f.name for f in files]

    def close(self):
        """
        Cleanup: Delete the sandbox when done.
        """
        if self.sandbox:
            print(f"Deleting sandbox {self.sandbox_id}...")
            self.sandbox.delete()
```

### 2. The Main Application (Tying it all together)

Save this as `main.py`. This script initializes the LLM, sets up the Daytona Workspace, and runs an OpenHands agent.

```python
import os
import asyncio
from openhands.sdk import Agent, LLM
from openhands.sdk.schema import AgentState
from daytona_workspace import DaytonaWorkspace

# 1. Configuration
# Ensure these env vars are set or replace with strings
DAYTONA_API_KEY = os.getenv("DAYTONA_API_KEY")
LLM_API_KEY = os.getenv("ANTHROPIC_API_KEY") # or OPENAI_API_KEY
LLM_MODEL = "claude-3-5-sonnet-20240620"

async def main():
    # 2. Initialize LLM
    llm = LLM(
        model=LLM_MODEL,
        api_key=LLM_API_KEY
    )

    # 3. Initialize Daytona Workspace
    # This creates a real, isolated environment for the agent
    workspace = DaytonaWorkspace(api_key=DAYTONA_API_KEY, language="python")

    try:
        # 4. Create the Agent
        # We inject our custom workspace here
        agent = Agent(
            llm=llm,
            workspace=workspace,
            prompt="You are a helpful coding assistant."
        )

        # 5. Run a Task
        # The agent will reason using the LLM and execute commands on Daytona
        task = "Create a Python script that calculates the Fibonacci sequence up to 100, save it as fib.py, and run it."
        print(f"Starting task: {task}")

        # Run the agent loop
        final_state = await agent.run(task)

        print(f"Task finished with state: {final_state}")

    finally:
        # 6. Cleanup
        workspace.close()

if __name__ == "__main__":
    asyncio.run(main())
```

## How It Works

1.  **Initialization**: When `main.py` starts, it connects to the Daytona platform and provisions a fresh, secure sandbox.
2.  **Task Delegation**: You give the Agent a high-level goal ("Write a fibonacci script").
3.  **Reasoning (LLM)**: The Agent sends this goal to the LLM. The LLM decides it needs to:
    *   Check the current directory (`ls`).
    *   Write code to a file (`write_file`).
    *   Run the code (`run_command`).
4.  **Execution (Daytona)**:
    *   When the Agent calls `write_file`, the `DaytonaWorkspace` adapter catches this and calls `sandbox.fs.upload_file`.
    *   When the Agent calls `run_command`, the adapter calls `sandbox.process.exec`.
5.  **Feedback Loop**: The output of the commands (stdout/stderr) is captured by Daytona, returned to the adapter, and fed back to the LLM by the Agent. The LLM sees the result and decides if the task is complete.

## Summary

By implementing the `BaseWorkspace` interface with Daytona SDK calls, you transform Daytona into the "body" of your AI Agent. This gives you:
*   **Security**: Arbitrary code runs in an isolated sandbox, not on your local machine.
*   **Consistency**: Every agent run starts in a clean, defined environment.
*   **Scalability**: You can spin up hundreds of these agents in parallel using Daytona's backend.
