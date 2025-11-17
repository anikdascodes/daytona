"""
Browser Service - Web automation and interaction.
Combines Playwright (direct control) with browser-use (AI control).
"""
from typing import Optional, Dict, Any, List
import asyncio
import json
from pathlib import Path

from playwright.async_api import async_playwright, Browser, Page, Playwright, Error as PlaywrightError
from config import settings
from utils.logger import logger


class BrowserService:
    """
    Service for browser automation and web interaction.

    Provides two modes:
    1. Structured actions (direct Playwright control)
    2. AI-driven tasks (browser-use integration - future)
    """

    def __init__(self):
        """Initialize browser service."""
        self.playwright: Optional[Playwright] = None
        self.browser: Optional[Browser] = None
        self.context = None
        self.page: Optional[Page] = None
        self.is_initialized = False
        logger.info("BrowserService created (not yet initialized)")

    async def initialize(self, headless: bool = True) -> Dict[str, Any]:
        """
        Initialize browser with Playwright.

        Args:
            headless: Whether to run browser in headless mode (no UI)

        Returns:
            Dict with success status and details
        """
        try:
            if self.is_initialized:
                logger.warning("Browser already initialized")
                return {"success": True, "message": "Already initialized"}

            logger.info(f"Initializing browser (headless={headless})...")

            # Start Playwright
            self.playwright = await async_playwright().start()

            # Launch browser (Chromium by default - best for automation)
            self.browser = await self.playwright.chromium.launch(
                headless=headless,
                args=[
                    '--no-sandbox',
                    '--disable-dev-shm-usage',
                    '--disable-blink-features=AutomationControlled',
                    '--disable-web-security',  # For CORS during testing
                ]
            )

            # Create browser context (isolated session)
            self.context = await self.browser.new_context(
                viewport={'width': 1920, 'height': 1080},
                user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                locale='en-US',
                timezone_id='America/New_York',
            )

            # Create initial page
            self.page = await self.context.new_page()

            self.is_initialized = True
            logger.info("✅ Browser initialized successfully")

            return {
                "success": True,
                "message": "Browser initialized",
                "browser": "Chromium",
                "headless": headless,
                "viewport": "1920x1080"
            }

        except Exception as e:
            logger.error(f"❌ Failed to initialize browser: {e}")
            await self.cleanup()
            return {
                "success": False,
                "error": str(e),
                "message": "Browser initialization failed"
            }

    async def execute_browser_task(self, task: str) -> Dict[str, Any]:
        """
        Execute a natural language browser task.

        For now, this parses simple commands. In Phase 4, we'll add
        full AI-driven browser-use integration.

        Args:
            task: Natural language description of what to do

        Returns:
            Dict with success status, result, and details

        Supported task patterns:
            - "Go to URL" / "Navigate to URL" / "Visit URL"
            - "Search Google for X"
            - "Click on SELECTOR"
            - "Fill SELECTOR with VALUE"
            - "Get text from SELECTOR"
            - "Take screenshot"
        """
        try:
            if not self.is_initialized:
                init_result = await self.initialize()
                if not init_result.get("success"):
                    return init_result

            logger.info(f"Executing browser task: {task}")
            task_lower = task.lower().strip()

            # Parse and execute simple commands
            if any(phrase in task_lower for phrase in ["go to", "navigate to", "visit", "open"]):
                # Extract URL
                url = task.split()[-1]
                if not url.startswith(("http://", "https://")):
                    url = "https://" + url

                result = await self.execute_structured_action({
                    "type": "navigate",
                    "url": url
                })
                return result

            elif "search google for" in task_lower:
                # Extract search query
                query = task.split("search google for", 1)[1].strip().strip('"\'')

                # Navigate to Google
                await self.page.goto("https://www.google.com")
                await self.page.wait_for_load_state("domcontentloaded")

                # Fill search box and submit
                await self.page.fill('textarea[name="q"], input[name="q"]', query)
                await self.page.press('textarea[name="q"], input[name="q"]', "Enter")
                await self.page.wait_for_load_state("domcontentloaded")

                # Extract top results
                await asyncio.sleep(1)  # Wait for results
                results = await self.page.query_selector_all("h3")
                top_results = []
                for i, result in enumerate(results[:5]):
                    text = await result.text_content()
                    if text:
                        top_results.append(text.strip())

                return {
                    "success": True,
                    "task": task,
                    "query": query,
                    "results": top_results,
                    "url": self.page.url
                }

            elif "take screenshot" in task_lower or "screenshot" in task_lower:
                path = "/workspace/screenshot.png"
                result = await self.take_screenshot(path)
                return {
                    **result,
                    "task": task
                }

            elif "get content" in task_lower or "get page content" in task_lower:
                content = await self.page.content()
                return {
                    "success": True,
                    "task": task,
                    "content": content[:5000],  # Limit size
                    "content_length": len(content),
                    "url": self.page.url
                }

            else:
                # Generic fallback
                return {
                    "success": False,
                    "error": "Could not parse task. Please use structured actions or implement AI-driven mode.",
                    "task": task,
                    "suggestion": "Use execute_structured_action() for precise control"
                }

        except Exception as e:
            logger.error(f"❌ Browser task failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "task": task
            }

    async def execute_structured_action(self, action: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute a structured browser action (precise control).

        Args:
            action: Dict with action type and parameters

        Supported actions:
            - navigate: {"type": "navigate", "url": "https://example.com"}
            - click: {"type": "click", "selector": "button#submit"}
            - fill: {"type": "fill", "selector": "input[name='email']", "value": "test@example.com"}
            - extract: {"type": "extract", "selector": "h1", "attribute": "text"}
            - screenshot: {"type": "screenshot", "path": "/workspace/screenshot.png"}
            - evaluate: {"type": "evaluate", "script": "document.title"}
            - wait: {"type": "wait", "timeout": 1000}
            - get_content: {"type": "get_content"}

        Returns:
            Dict with success status and result
        """
        try:
            if not self.is_initialized:
                init_result = await self.initialize()
                if not init_result.get("success"):
                    return init_result

            action_type = action.get("type")
            logger.info(f"Executing structured action: {action_type}")

            if action_type == "navigate":
                url = action.get("url")
                await self.page.goto(url, wait_until="domcontentloaded", timeout=30000)
                await self.page.wait_for_load_state("networkidle", timeout=10000)

                return {
                    "success": True,
                    "action": "navigate",
                    "url": url,
                    "current_url": self.page.url,
                    "title": await self.page.title()
                }

            elif action_type == "click":
                selector = action.get("selector")
                await self.page.click(selector, timeout=10000)
                await asyncio.sleep(0.5)  # Wait for action to complete

                return {
                    "success": True,
                    "action": "click",
                    "selector": selector,
                    "current_url": self.page.url
                }

            elif action_type == "fill":
                selector = action.get("selector")
                value = action.get("value")
                await self.page.fill(selector, value, timeout=10000)

                return {
                    "success": True,
                    "action": "fill",
                    "selector": selector,
                    "value": value
                }

            elif action_type == "extract":
                selector = action.get("selector")
                attribute = action.get("attribute", "text")

                if attribute == "text":
                    element = await self.page.query_selector(selector)
                    value = await element.text_content() if element else None
                elif attribute == "html":
                    element = await self.page.query_selector(selector)
                    value = await element.inner_html() if element else None
                else:
                    element = await self.page.query_selector(selector)
                    value = await element.get_attribute(attribute) if element else None

                return {
                    "success": True,
                    "action": "extract",
                    "selector": selector,
                    "attribute": attribute,
                    "value": value
                }

            elif action_type == "screenshot":
                path = action.get("path", "/workspace/screenshot.png")
                full_page = action.get("full_page", False)
                await self.page.screenshot(path=path, full_page=full_page)

                return {
                    "success": True,
                    "action": "screenshot",
                    "path": path,
                    "full_page": full_page
                }

            elif action_type == "evaluate":
                script = action.get("script")
                result = await self.page.evaluate(script)

                return {
                    "success": True,
                    "action": "evaluate",
                    "script": script,
                    "result": result
                }

            elif action_type == "wait":
                timeout = action.get("timeout", 1000)
                await asyncio.sleep(timeout / 1000)

                return {
                    "success": True,
                    "action": "wait",
                    "timeout": timeout
                }

            elif action_type == "get_content":
                content = await self.page.content()

                return {
                    "success": True,
                    "action": "get_content",
                    "content": content[:5000],  # Limit content size
                    "content_length": len(content),
                    "url": self.page.url,
                    "title": await self.page.title()
                }

            elif action_type == "extract_links":
                links = await self.page.evaluate('''() => {
                    const anchors = Array.from(document.querySelectorAll('a'));
                    return anchors.map(a => ({
                        text: a.textContent.trim(),
                        href: a.href
                    })).filter(link => link.href && link.text);
                }''')

                return {
                    "success": True,
                    "action": "extract_links",
                    "links": links[:50],  # Limit to first 50
                    "total_links": len(links)
                }

            else:
                return {
                    "success": False,
                    "error": f"Unknown action type: {action_type}",
                    "supported_actions": ["navigate", "click", "fill", "extract", "screenshot",
                                         "evaluate", "wait", "get_content", "extract_links"]
                }

        except PlaywrightError as e:
            logger.error(f"❌ Playwright action failed: {e}")
            return {
                "success": False,
                "error": f"Playwright error: {str(e)}",
                "action": action.get("type")
            }
        except Exception as e:
            logger.error(f"❌ Structured action failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "action": action.get("type")
            }

    async def take_screenshot(self, path: str = "/workspace/screenshot.png", full_page: bool = True) -> Dict[str, Any]:
        """
        Take a screenshot of the current page.

        Args:
            path: Path where to save screenshot
            full_page: Whether to capture full page or just viewport

        Returns:
            Dict with success status and path
        """
        try:
            if not self.is_initialized or not self.page:
                return {
                    "success": False,
                    "error": "Browser not initialized"
                }

            await self.page.screenshot(path=path, full_page=full_page)
            logger.info(f"✅ Screenshot saved: {path}")

            return {
                "success": True,
                "path": path,
                "full_page": full_page,
                "url": self.page.url
            }

        except Exception as e:
            logger.error(f"❌ Screenshot failed: {e}")
            return {
                "success": False,
                "error": str(e)
            }

    async def get_page_info(self) -> Dict[str, Any]:
        """
        Get information about the current page.

        Returns:
            Dict with page details
        """
        try:
            if not self.is_initialized or not self.page:
                return {
                    "success": False,
                    "error": "Browser not initialized"
                }

            return {
                "success": True,
                "url": self.page.url,
                "title": await self.page.title(),
                "viewport": self.page.viewport_size,
            }

        except Exception as e:
            logger.error(f"❌ Get page info failed: {e}")
            return {
                "success": False,
                "error": str(e)
            }

    async def cleanup(self) -> None:
        """Clean up browser resources."""
        try:
            logger.info("Cleaning up browser resources...")

            if self.page:
                await self.page.close()
                self.page = None

            if self.context:
                await self.context.close()
                self.context = None

            if self.browser:
                await self.browser.close()
                self.browser = None

            if self.playwright:
                await self.playwright.stop()
                self.playwright = None

            self.is_initialized = False

            logger.info("✅ Browser cleanup complete")

        except Exception as e:
            logger.error(f"⚠️  Browser cleanup error: {e}")

    async def __aenter__(self):
        """Context manager entry."""
        await self.initialize()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        await self.cleanup()


# Global instance
browser_service = BrowserService()
