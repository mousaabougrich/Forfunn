"""
Example: Using Tor for free IP rotation

This shows how to use Tor network for completely free, reliable IP rotation.
Tor rotates your exit IP through volunteer nodes worldwide every ~10 minutes.

Setup:
    sudo apt install tor
    sudo service tor start

Then run this example:
    python scraper_with_tor_example.py
"""

import asyncio
import logging
from typing import Optional

import httpx

from core.tor_manager import TorManager
from core.user_agent import get_user_agent_rotator

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


class TorScraperExample:
    """
    Example scraper using Tor for free IP rotation.
    Combines Tor proxies with User-Agent rotation.
    """

    def __init__(self):
        """Initialize scraper with Tor."""
        self.tor = TorManager()
        self.user_agent_rotator = get_user_agent_rotator()

        # Verify Tor is running
        if not self.tor.is_tor_running():
            raise RuntimeError(
                "Tor is not running!\n"
                "Start it with: sudo service tor start"
            )

        logger.info("✓ Tor scraper initialized")

    def get_headers(self) -> dict:
        """Get headers with rotated User-Agent."""
        return {
            "User-Agent": self.user_agent_rotator.get_random_agent(),
            "Accept-Language": "en-US,en;q=0.9",
            "Accept-Encoding": "gzip, deflate",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "DNT": "1",
            "Connection": "keep-alive",
        }

    async def scrape_with_tor(self, url: str) -> Optional[str]:
        """
        Scrape a URL using Tor proxy.
        
        Args:
            url: URL to scrape
            
        Returns:
            Page content or None if failed
        """
        async with httpx.AsyncClient(
            proxies=self.tor.get_httpx_proxies(),
            timeout=30.0,
            follow_redirects=True,
        ) as client:
            try:
                logger.info(f"Scraping {url}...")

                # Get current IP before request
                current_ip = await self.tor.get_current_exit_ip(client)
                logger.info(f"Current Tor exit IP: {current_ip}")

                # Make request
                response = await client.get(url, headers=self.get_headers())

                if response.status_code == 200:
                    logger.info(f"✓ Successfully scraped {url}")
                    return response.text
                else:
                    logger.warning(
                        f"Got status {response.status_code} from {url}"
                    )
                    return None

            except Exception as e:
                logger.error(f"Error scraping {url}: {e}")
                return None

    async def scrape_multiple_urls(self, urls: list) -> dict:
        """
        Scrape multiple URLs, rotating Tor circuit between requests.
        
        Args:
            urls: List of URLs to scrape
            
        Returns:
            Dict mapping URL to content
        """
        results = {}

        async with httpx.AsyncClient(
            proxies=self.tor.get_httpx_proxies(),
            timeout=30.0,
            follow_redirects=True,
        ) as client:
            for i, url in enumerate(urls, 1):
                try:
                    logger.info(
                        f"\n[{i}/{len(urls)}] Scraping {url}..."
                    )

                    # Get current exit IP
                    old_ip = await self.tor.get_current_exit_ip(client)
                    logger.info(f"Current IP: {old_ip}")

                    # Make request
                    response = await client.get(
                        url,
                        headers=self.get_headers(),
                    )

                    if response.status_code == 200:
                        logger.info(f"✓ Success")
                        results[url] = response.text
                    else:
                        logger.warning(f"Status {response.status_code}")
                        results[url] = None

                    # Request new circuit between requests
                    if i < len(urls):  # Don't rotate after last request
                        logger.info("Requesting new Tor circuit...")
                        await self.tor.request_new_circuit()

                        # Wait for new IP
                        new_ip = await self.tor.get_current_exit_ip(client)
                        logger.info(f"New IP: {new_ip}")

                        # Wait between requests
                        await asyncio.sleep(2)

                except Exception as e:
                    logger.error(f"Error scraping {url}: {e}")
                    results[url] = None

        return results

    async def benchmark_tor_rotation(self, num_checks: int = 5) -> None:
        """
        Benchmark Tor IP rotation.
        Shows how Tor changes your exit IP over time.
        
        Args:
            num_checks: Number of times to check IP
        """
        logger.info(f"\n{'='*70}")
        logger.info(f"Tor IP Rotation Benchmark ({num_checks} checks)")
        logger.info(f"{'='*70}")

        async with httpx.AsyncClient(
            proxies=self.tor.get_httpx_proxies(),
            timeout=10.0,
        ) as client:
            ips = []

            for i in range(num_checks):
                try:
                    ip = await self.tor.get_current_exit_ip(client)
                    ips.append(ip)
                    
                    is_new = ip not in ips[:-1] if ips[:-1] else True
                    status = "✓ NEW" if is_new else "⊘ same"
                    
                    logger.info(f"Check {i + 1}: {ip} {status}")

                    if i < num_checks - 1:
                        logger.info(
                            "Requesting new circuit and waiting..."
                        )
                        await self.tor.request_new_circuit()
                        await asyncio.sleep(3)

                except Exception as e:
                    logger.error(f"Check {i + 1} failed: {e}")

            # Summary
            unique_ips = len(set(ips))
            logger.info(f"\n{'='*70}")
            logger.info(f"Unique IPs: {unique_ips}/{num_checks}")
            logger.info(f"Rotation rate: {(unique_ips/num_checks)*100:.1f}%")
            logger.info(f"{'='*70}\n")


# ============================================================================
# EXAMPLES
# ============================================================================

async def example_1_single_url():
    """Example 1: Scrape a single URL through Tor."""
    logger.info("\n" + "="*70)
    logger.info("EXAMPLE 1: Single URL")
    logger.info("="*70)

    try:
        scraper = TorScraperExample()

        # Use httpbin.org for testing (returns your IP)
        content = await scraper.scrape_with_tor(
            "https://httpbin.org/ip"
        )

        if content:
            logger.info(f"Response: {content}")

    except Exception as e:
        logger.error(f"Example failed: {e}")


async def example_2_multiple_urls():
    """Example 2: Scrape multiple URLs with IP rotation."""
    logger.info("\n" + "="*70)
    logger.info("EXAMPLE 2: Multiple URLs with rotation")
    logger.info("="*70)

    try:
        scraper = TorScraperExample()

        urls = [
            "https://httpbin.org/ip",
            "https://httpbin.org/user-agent",
            "https://httpbin.org/headers",
        ]

        results = await scraper.scrape_multiple_urls(urls)

        logger.info("\nResults:")
        for url, content in results.items():
            logger.info(f"  {url}: {'✓' if content else '✗'}")

    except Exception as e:
        logger.error(f"Example failed: {e}")


async def example_3_benchmark():
    """Example 3: Benchmark Tor IP rotation."""
    logger.info("\n" + "="*70)
    logger.info("EXAMPLE 3: Benchmark IP rotation")
    logger.info("="*70)

    try:
        scraper = TorScraperExample()
        await scraper.benchmark_tor_rotation(num_checks=5)

    except Exception as e:
        logger.error(f"Example failed: {e}")


async def main():
    """Run all examples."""
    try:
        await example_1_single_url()
        await asyncio.sleep(5)

        await example_2_multiple_urls()
        await asyncio.sleep(5)

        await example_3_benchmark()

    except Exception as e:
        logger.error(f"Fatal error: {e}")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("\nInterrupted by user")
    except Exception as e:
        logger.error(f"Error: {e}")
