"""
Example: Using Proxy Rotation with Playwright

This shows how to integrate the proxy rotation system with Playwright.
"""

import asyncio
import logging
from typing import Optional

# These imports would come from your project
from core.anti_blocking import AntiBlockingMixin, AntiBlockingConfig
from core.proxy_manager import get_proxy_rotator
from core.user_agent import get_user_agent_rotator

logger = logging.getLogger(__name__)


class PlaywrightScraperWithProxies(AntiBlockingMixin):
    """
    Example scraper using Playwright with proxy and User-Agent rotation.
    """

    def __init__(
        self,
        url: str,
        proxy_list: Optional[list] = None,
        headless: bool = True,
    ):
        """
        Initialize scraper with proxy rotation.

        Args:
            url: URL to scrape
            proxy_list: List of proxies to rotate through
            headless: Run browser in headless mode
        """
        # Create anti-blocking config
        config = AntiBlockingConfig(
            use_proxy_rotation=bool(proxy_list),
            use_user_agent_rotation=True,
            min_delay_seconds=1.0,
            max_delay_seconds=2.0,
            proxy_list=proxy_list,
        )

        super().__init__(config)
        self.url = url
        self.headless = headless

    async def scrape(self):
        """
        Scrape using Playwright with proxy rotation.
        """
        # Playwright is installed separately
        from playwright.async_api import async_playwright

        async with async_playwright() as p:
            # Use chromium (most compatible with proxies)
            browser = await p.chromium.launch(headless=self.headless)

            for attempt in range(3):  # Retry up to 3 times
                try:
                    # Get anti-blocking context options
                    context_options = self.get_playwright_context_options()

                    logger.info(
                        f"Attempt {attempt + 1}: Scraping {self.url}"
                    )
                    if "proxy" in context_options:
                        logger.info(
                            f"Using proxy: {context_options['proxy']['server']}"
                        )

                    # Create new context with anti-blocking options
                    async with await browser.new_context(
                        **context_options
                    ) as context:
                        page = await context.new_page()

                        # Wait before request
                        await self.wait_before_request()

                        # Navigate to URL
                        response = await page.goto(self.url)

                        if response.ok:
                            logger.info(f"✓ Successfully scraped {self.url}")
                            # Get content
                            content = await page.content()
                            return content
                        else:
                            logger.warning(
                                f"Got response {response.status}, retrying..."
                            )

                except Exception as e:
                    logger.warning(f"Attempt {attempt + 1} failed: {e}")
                    if attempt == 2:
                        logger.error(f"All attempts failed for {self.url}")
                        raise

                finally:
                    await page.close()

            await browser.close()

        return None


class HttpxScraperWithProxies(AntiBlockingMixin):
    """
    Example scraper using httpx with proxy and User-Agent rotation.
    """

    def __init__(
        self,
        url: str,
        proxy_list: Optional[list] = None,
    ):
        """
        Initialize scraper with proxy rotation.

        Args:
            url: URL to scrape
            proxy_list: List of proxies to rotate through
        """
        config = AntiBlockingConfig(
            use_proxy_rotation=bool(proxy_list),
            use_user_agent_rotation=True,
            min_delay_seconds=0.5,
            max_delay_seconds=1.5,
            proxy_list=proxy_list,
        )

        super().__init__(config)
        self.url = url

    async def scrape(self):
        """
        Scrape using httpx with proxy rotation.
        """
        # httpx would be imported at top
        import httpx

        async with httpx.AsyncClient(
            timeout=30.0,
            follow_redirects=True,
        ) as client:
            for attempt in range(3):
                try:
                    # Get anti-blocking headers and proxies
                    headers = self.get_httpx_headers()
                    proxies = self.get_httpx_proxies()

                    logger.info(f"Attempt {attempt + 1}: Scraping {self.url}")
                    if proxies:
                        logger.info(f"Using proxy")

                    # Wait before request
                    await self.wait_before_request()

                    # Make request
                    response = await client.get(
                        self.url,
                        headers=headers,
                        proxies=proxies,
                    )

                    if response.status_code == 200:
                        logger.info(f"✓ Successfully scraped {self.url}")
                        return response.text

                    else:
                        logger.warning(
                            f"Got status {response.status_code}, retrying..."
                        )

                except httpx.ProxyError as e:
                    logger.warning(f"Proxy error: {e}")
                    # Try next proxy automatically
                except Exception as e:
                    logger.warning(f"Attempt {attempt + 1} failed: {e}")
                    if attempt == 2:
                        logger.error(f"All attempts failed for {self.url}")
                        raise

        return None


# ============================================================================
# USAGE
# ============================================================================

async def main():
    """
    Example usage of proxy-rotating scrapers.
    """

    # Define your proxy list
    proxies = [
        "http://proxy1.example.com:8080",
        "http://proxy2.example.com:8080",
        "http://proxy3.example.com:8080",
        # Add more proxies
    ]

    # ---- PLAYWRIGHT EXAMPLE ----
    playwright_scraper = PlaywrightScraperWithProxies(
        url="https://www.example.com",
        proxy_list=proxies,
        headless=True,
    )
    # content = await playwright_scraper.scrape()

    # ---- HTTPX EXAMPLE ----
    httpx_scraper = HttpxScraperWithProxies(
        url="https://www.example.com",
        proxy_list=proxies,
    )
    # content = await httpx_scraper.scrape()

    print("Scraper examples configured. Uncomment to run.")


if __name__ == "__main__":
    # Uncomment to test:
    # asyncio.run(main())
    print("See main() function for usage examples")
