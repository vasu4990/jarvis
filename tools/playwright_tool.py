"""
Playwright browser automation tool
"""

import asyncio
import structlog
from playwright.async_api import async_playwright, Browser, BrowserContext, Page
from utils.schemas import ExecutionResult
from typing import Optional

logger = structlog.get_logger(__name__)


class PlaywrightTool:
    """Browser automation using Playwright"""
    
    def __init__(self, config):
        self.config = config
        self.browser_type = config.get("tools.playwright.browser", "chromium")
        self.headless = config.get("tools.playwright.headless", False)
        self.timeout = config.get("tools.playwright.timeout", 30000)
        
        self.playwright = None
        self.browser: Optional[Browser] = None
        self.context: Optional[BrowserContext] = None
        self.page: Optional[Page] = None
        
    async def execute(self, action_type: str, params: dict) -> ExecutionResult:
        """Execute browser action"""
        
        try:
            if action_type == "open_browser":
                return await self._open_browser(params)
            elif action_type == "close_browser":
                return await self._close_browser()
            elif action_type == "navigate_url":
                return await self._navigate_url(params)
            elif action_type == "click_selector":
                return await self._click_selector(params)
            elif action_type == "type_selector":
                return await self._type_selector(params)
            elif action_type == "get_page_content":
                return await self._get_page_content()
            else:
                return ExecutionResult(success=False, error=f"Unknown action: {action_type}")
        except Exception as e:
            logger.error("Playwright tool error", action=action_type, error=str(e))
            return ExecutionResult(success=False, error=str(e))
            
    async def _open_browser(self, params: dict) -> ExecutionResult:
        """Launch browser"""
        try:
            if self.browser and self.browser.is_connected():
                return ExecutionResult(
                    success=True,
                    message="Browser already open"
                )
                
            self.playwright = await async_playwright().start()
            
            if self.browser_type == "chromium":
                self.browser = await self.playwright.chromium.launch(headless=self.headless)
            elif self.browser_type == "firefox":
                self.browser = await self.playwright.firefox.launch(headless=self.headless)
            elif self.browser_type == "webkit":
                self.browser = await self.playwright.webkit.launch(headless=self.headless)
            else:
                self.browser = await self.playwright.chromium.launch(headless=self.headless)
                
            self.context = await self.browser.new_context()
            self.page = await self.context.new_page()
            
            logger.info("Browser launched", type=self.browser_type, headless=self.headless)
            
            return ExecutionResult(
                success=True,
                message=f"{self.browser_type.capitalize()} browser opened"
            )
            
        except Exception as e:
            logger.error("Failed to open browser", error=str(e))
            return ExecutionResult(success=False, error=str(e))
            
    async def _close_browser(self) -> ExecutionResult:
        """Close browser"""
        try:
            if self.browser:
                await self.browser.close()
                await self.playwright.stop()
                self.browser = None
                self.context = None
                self.page = None
                self.playwright = None
                
            return ExecutionResult(success=True, message="Browser closed")
            
        except Exception as e:
            return ExecutionResult(success=False, error=str(e))
            
    async def _navigate_url(self, params: dict) -> ExecutionResult:
        """Navigate to URL"""
        url = params.get("url", "")
        
        if not url:
            return ExecutionResult(success=False, error="No URL provided")
            
        # Ensure browser is open
        if not self.page:
            open_result = await self._open_browser({})
            if not open_result.success:
                return open_result
                
        try:
            await self.page.goto(url, timeout=self.timeout, wait_until="domcontentloaded")
            
            logger.info("Navigated to URL", url=url)
            
            return ExecutionResult(
                success=True,
                message=f"Navigated to {url}",
                data={"url": self.page.url, "title": await self.page.title()}
            )
            
        except Exception as e:
            logger.error("Navigation failed", url=url, error=str(e))
            return ExecutionResult(success=False, error=str(e))
            
    async def _click_selector(self, params: dict) -> ExecutionResult:
        """Click element by CSS selector"""
        selector = params.get("selector", "")
        
        if not selector:
            return ExecutionResult(success=False, error="No selector provided")
            
        if not self.page:
            return ExecutionResult(success=False, error="No page open")
            
        try:
            await self.page.click(selector, timeout=self.timeout)
            
            return ExecutionResult(
                success=True,
                message=f"Clicked {selector}"
            )
            
        except Exception as e:
            return ExecutionResult(success=False, error=f"Click failed: {str(e)}")
            
    async def _type_selector(self, params: dict) -> ExecutionResult:
        """Type into element by CSS selector"""
        selector = params.get("selector", "")
        text = params.get("text", "")
        
        if not selector or not text:
            return ExecutionResult(success=False, error="Missing selector or text")
            
        if not self.page:
            return ExecutionResult(success=False, error="No page open")
            
        try:
            await self.page.fill(selector, text, timeout=self.timeout)
            
            return ExecutionResult(
                success=True,
                message=f"Typed into {selector}"
            )
            
        except Exception as e:
            return ExecutionResult(success=False, error=f"Type failed: {str(e)}")
            
    async def _get_page_content(self) -> ExecutionResult:
        """Get current page content"""
        if not self.page:
            return ExecutionResult(success=False, error="No page open")
            
        try:
            url = self.page.url
            title = await self.page.title()
            content = await self.page.content()
            
            return ExecutionResult(
                success=True,
                message="Page content retrieved",
                data={
                    "url": url,
                    "title": title,
                    "content_length": len(content)
                }
            )
            
        except Exception as e:
            return ExecutionResult(success=False, error=str(e))
            
    async def cleanup(self):
        """Cleanup resources"""
        await self._close_browser()
