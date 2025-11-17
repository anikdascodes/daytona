"""
Daytona Service - Manages sandbox creation and operations.
"""
import os
from typing import Optional, Dict, Any
from daytona_sdk import Daytona, Sandbox, DaytonaConfig
from utils.logger import logger
from config import settings


class DaytonaService:
    """Service for managing Daytona sandboxes."""

    def __init__(self):
        """Initialize Daytona service."""
        self.client: Optional[Daytona] = None
        self.sandbox: Optional[Sandbox] = None
        logger.info("DaytonaService initialized")

    async def initialize(self) -> bool:
        """Initialize Daytona client and create sandbox."""
        try:
            logger.info("Initializing Daytona client...")

            # Create Daytona config
            config = DaytonaConfig(
                api_key=settings.DAYTONA_API_KEY,
                api_url=settings.DAYTONA_API_URL,
                target=settings.DAYTONA_TARGET
            )

            # Initialize Daytona client
            self.client = Daytona(config=config)

            logger.info("✅ Daytona client initialized")

            # Create sandbox
            logger.info("Creating Daytona sandbox...")
            self.sandbox = self.client.create()

            logger.info(f"✅ Daytona sandbox created: {self.sandbox.id}")

            return True

        except Exception as e:
            logger.error(f"❌ Failed to initialize Daytona: {e}")
            raise

    async def get_sandbox_status(self) -> Dict[str, Any]:
        """Get current sandbox status."""
        if not self.sandbox:
            return {"status": "not_created", "error": "Sandbox not initialized"}

        try:
            # Refresh sandbox info
            self.sandbox.refresh()

            return {
                "status": "healthy",
                "sandbox_id": self.sandbox.id,
                "state": self.sandbox.state,
                "created_at": str(self.sandbox.created_at) if hasattr(self.sandbox, 'created_at') else None,
            }
        except Exception as e:
            logger.error(f"Failed to get sandbox status: {e}")
            return {"status": "error", "error": str(e)}

    async def execute_command(self, command: str, work_dir: str = "/workspace") -> Dict[str, Any]:
        """Execute a command in the sandbox."""
        if not self.sandbox:
            return {"success": False, "error": "Sandbox not initialized"}

        try:
            logger.info(f"Executing command in sandbox: {command}")

            result = self.sandbox.process.code_run(command, work_dir=work_dir)

            return {
                "success": True,
                "stdout": result.stdout if hasattr(result, 'stdout') else str(result),
                "stderr": result.stderr if hasattr(result, 'stderr') else "",
                "exit_code": result.exit_code if hasattr(result, 'exit_code') else 0,
            }
        except Exception as e:
            logger.error(f"Failed to execute command: {e}")
            return {
                "success": False,
                "error": str(e),
                "stdout": "",
                "stderr": str(e),
                "exit_code": 1,
            }

    async def read_file(self, file_path: str) -> Dict[str, Any]:
        """Read a file from the sandbox."""
        if not self.sandbox:
            return {"success": False, "error": "Sandbox not initialized"}

        try:
            logger.info(f"Reading file: {file_path}")

            content = self.sandbox.fs.read(file_path)

            return {
                "success": True,
                "content": content,
                "path": file_path,
            }
        except Exception as e:
            logger.error(f"Failed to read file {file_path}: {e}")
            return {
                "success": False,
                "error": str(e),
                "content": None,
            }

    async def write_file(self, file_path: str, content: str) -> Dict[str, Any]:
        """Write a file to the sandbox."""
        if not self.sandbox:
            return {"success": False, "error": "Sandbox not initialized"}

        try:
            logger.info(f"Writing file: {file_path}")

            self.sandbox.fs.write(file_path, content)

            return {
                "success": True,
                "path": file_path,
                "message": f"File written successfully: {file_path}",
            }
        except Exception as e:
            logger.error(f"Failed to write file {file_path}: {e}")
            return {
                "success": False,
                "error": str(e),
            }

    async def list_files(self, path: str = "/workspace") -> Dict[str, Any]:
        """List files in a directory."""
        if not self.sandbox:
            return {"success": False, "error": "Sandbox not initialized"}

        try:
            logger.info(f"Listing files in: {path}")

            files = self.sandbox.fs.list(path)

            return {
                "success": True,
                "path": path,
                "files": files,
            }
        except Exception as e:
            logger.error(f"Failed to list files in {path}: {e}")
            return {
                "success": False,
                "error": str(e),
                "files": [],
            }

    async def health_check(self) -> Dict[str, Any]:
        """Check if Daytona service is healthy."""
        if not self.sandbox:
            return {"status": "unhealthy", "error": "Sandbox not initialized"}

        try:
            self.sandbox.refresh()
            return {
                "status": "healthy",
                "sandbox_id": self.sandbox.id,
            }
        except Exception as e:
            return {
                "status": "unhealthy",
                "error": str(e),
            }

    async def cleanup(self):
        """Cleanup Daytona resources."""
        if self.sandbox and self.client:
            try:
                logger.info(f"Deleting sandbox {self.sandbox.id}...")
                self.client.delete(self.sandbox)
                logger.info("✅ Sandbox deleted successfully")
            except Exception as e:
                logger.error(f"Failed to delete sandbox: {e}")


# Global instance
daytona_service = DaytonaService()
