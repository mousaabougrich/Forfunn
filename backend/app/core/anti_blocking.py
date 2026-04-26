"""
Anti-blocking utilities for scraping.
Combines proxy rotation, User-Agent rotation, and request delays.
"""

import asyncio
import random
import logging
from typing import Optional, Dict, Any
from datetime import timedelta

from proxy_manager import ProxyRotator, get_proxy_rotator
from user_agent import UserAgentRotator, get_user_agent_rotator

logger = logging.getLogger(__name__)


class AntiBlockingConfig:
    """
    Configuration for anti-blocking strategies.
    """

    def __init__(
        self,
        use_proxy_rotation: bool = True,
        use_user_agent_rotation: bool = True,
        min_delay_seconds: float = 1.0,
        max_delay_seconds: float = 3.0,
        proxy_list: Optional[list] = None,
        custom_user_agents: Optional[list] = None,
    ):
        """
        Initialize anti-blocking configuration.

        Args:
            use_proxy_rotation: Rotate proxies between requests
            use_user_agent_rotation: Rotate User-Agent headers
            min_delay_seconds: Minimum delay between requests
            max_delay_seconds: Maximum delay between requests
            proxy_list: Custom list of proxies
            custom_user_agents: Custom list of User-Agents
        """
        self.use_proxy_rotation = use_proxy_rotation
        self.use_user_agent_rotation = use_user_agent_rotation
        self.min_delay_seconds = min_delay_seconds
        self.max_delay_seconds = max_delay_seconds
        self.proxy_rotator = (
            get_proxy_rotator(proxy_list=proxy_list)
            if use_proxy_rotation
            else None
        )
        self.user_agent_rotator = (
            get_user_agent_rotator(user_agents=custom_user_agents)
            if use_user_agent_rotation
            else None
        )


class AntiBlockingMixin:
    """
    Mixin to add anti-blocking capabilities to any scraper.
    Use with httpx.AsyncClient or Playwright.
    """

    def __init__(self, config: Optional[AntiBlockingConfig] = None):
        """Initialize with anti-blocking config."""
        self.config = config or AntiBlockingConfig()

    def get_next_proxy(self) -> Optional[str]:
        """Get next proxy from rotator."""
        if self.config.proxy_rotator:
            return self.config.proxy_rotator.get_next_proxy()
        return None

    def get_next_user_agent(self) -> str:
        """Get next User-Agent from rotator."""
        if self.config.user_agent_rotator:
            return self.config.user_agent_rotator.get_next_agent()
        return "Mozilla/5.0"  # Fallback

    def get_request_headers(self) -> Dict[str, str]:
        """
        Get headers with rotated User-Agent.
        Can be extended with other headers.
        """
        return {
            "User-Agent": self.get_next_user_agent(),
            "Accept-Language": "en-US,en;q=0.9",
            "Accept-Encoding": "gzip, deflate",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "DNT": "1",
            "Connection": "keep-alive",
            "Upgrade-Insecure-Requests": "1",
        }

    async def wait_before_request(self) -> None:
        """Random delay between requests to avoid detection."""
        if self.config.min_delay_seconds > 0:
            delay = random.uniform(
                self.config.min_delay_seconds,
                self.config.max_delay_seconds,
            )
            logger.debug(f"Waiting {delay:.2f}s before next request")
            await asyncio.sleep(delay)

    def get_playwright_context_options(self) -> Dict[str, Any]:
        """
        Get context options for Playwright browser with anti-blocking measures.

        Returns:
            Dictionary of context options for browser_context()
        """
        options: Dict[str, Any] = {
            "user_agent": self.get_next_user_agent(),
            "extra_http_headers": self.get_request_headers(),
        }

        # Add proxy if available
        if proxy := self.get_next_proxy():
            options["proxy"] = {"server": proxy}

        return options

    def get_httpx_headers(self) -> Dict[str, str]:
        """Get headers for httpx client."""
        return self.get_request_headers()

    def get_httpx_proxies(self) -> Optional[Dict[str, str]]:
        """
        Get proxy dict for httpx client.

        Returns:
            Dict like {"http://": "http://proxy:port", "https://": "http://proxy:port"}
            or None if no proxy
        """
        if proxy := self.get_next_proxy():
            return {
                "http://": proxy,
                "https://": proxy,
            }
        return None


# Example usage
if __name__ == "__main__":
    # Configure with custom proxies
    config = AntiBlockingConfig(
        use_proxy_rotation=True,
        use_user_agent_rotation=True,
        min_delay_seconds=1.0,
        max_delay_seconds=3.0,
        proxy_list=[
            "http://proxy1.example.com:8080",
            "http://proxy2.example.com:8080",
            # Add more proxies here
        ],
    )

    # Create mixin instance
    anti_blocker = AntiBlockingMixin(config)

    # Use with httpx
    headers = anti_blocker.get_httpx_headers()
    proxies = anti_blocker.get_httpx_proxies()

    print("Headers:", headers)
    print("Proxies:", proxies)

    # Use with Playwright
    context_options = anti_blocker.get_playwright_context_options()
    print("Playwright context options:", context_options)
