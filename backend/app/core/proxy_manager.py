"""
Proxy rotation manager to avoid getting blocked by websites.
Rotates through proxies for each request to mimic different users.
"""

import random
from typing import Optional, List
from urllib.parse import urljoin
import logging

logger = logging.getLogger(__name__)


class ProxyRotator:
    """
    Manages rotating through a list of proxies.
    Supports free proxies, custom proxy lists, and fallback to direct requests.
    """

    def __init__(self, proxy_list: Optional[List[str]] = None, use_free_proxies: bool = False):
        """
        Initialize the proxy rotator.

        Args:
            proxy_list: List of proxy URLs (e.g., ['http://proxy1:8080', 'http://proxy2:8080'])
            use_free_proxies: If True, fetch free proxies from online sources
        """
        self.proxy_list: List[str] = proxy_list or []
        self.current_index = 0
        self.use_free_proxies = use_free_proxies

        if use_free_proxies and not self.proxy_list:
            self._fetch_free_proxies()

        logger.info(f"Initialized ProxyRotator with {len(self.proxy_list)} proxies")

    def get_next_proxy(self) -> Optional[str]:
        """
        Get the next proxy from the rotation list.
        Returns None if no proxies available (falls back to direct connection).

        Returns:
            Proxy URL string or None
        """
        if not self.proxy_list:
            logger.debug("No proxies available, using direct connection")
            return None

        proxy = self.proxy_list[self.current_index]
        self.current_index = (self.current_index + 1) % len(self.proxy_list)
        logger.debug(f"Using proxy: {proxy}")
        return proxy

    def get_random_proxy(self) -> Optional[str]:
        """
        Get a random proxy from the list.
        Useful for truly random distribution.

        Returns:
            Proxy URL string or None
        """
        if not self.proxy_list:
            logger.debug("No proxies available, using direct connection")
            return None

        proxy = random.choice(self.proxy_list)
        logger.debug(f"Using random proxy: {proxy}")
        return proxy

    def add_proxy(self, proxy: str) -> None:
        """Add a single proxy to the rotation list."""
        if proxy not in self.proxy_list:
            self.proxy_list.append(proxy)
            logger.info(f"Added proxy: {proxy}")

    def add_proxies(self, proxies: List[str]) -> None:
        """Add multiple proxies to the rotation list."""
        new_proxies = [p for p in proxies if p not in self.proxy_list]
        self.proxy_list.extend(new_proxies)
        logger.info(f"Added {len(new_proxies)} proxies")

    def remove_proxy(self, proxy: str) -> None:
        """Remove a proxy from the rotation list (useful for failed proxies)."""
        if proxy in self.proxy_list:
            self.proxy_list.remove(proxy)
            logger.info(f"Removed proxy: {proxy}")

    def _fetch_free_proxies(self) -> None:
        """
        Fetch free proxies from online sources.
        Note: Free proxies can be slow/unreliable. Use for testing only.
        """
        try:
            # Example free proxy sources (commented out by default)
            # You can enable these by uncommenting and installing requests library
            # 
            # import requests
            # 
            # sources = [
            #     "https://www.proxy-list.download/api/v1/get?type=http",
            #     "https://api.proxyscrape.com/v2/?request=getproxies&protocol=http",
            # ]
            #
            # for source in sources:
            #     try:
            #         resp = requests.get(source, timeout=5)
            #         proxies = resp.json().get('proxies', [])
            #         if proxies:
            #             self.add_proxies(proxies)
            #     except Exception as e:
            #         logger.warning(f"Failed to fetch from {source}: {e}")

            logger.info("Free proxy fetching requires 'requests' library. See comments in code.")
        except Exception as e:
            logger.warning(f"Failed to fetch free proxies: {e}")

    def reset_rotation(self) -> None:
        """Reset the rotation index to the beginning."""
        self.current_index = 0
        logger.info("Proxy rotation index reset")


class ProxyConfig:
    """Configuration for proxy usage in scrapers."""

    def __init__(self, enabled: bool = True, random_rotation: bool = False):
        """
        Initialize proxy configuration.

        Args:
            enabled: Whether to use proxies
            random_rotation: If True, use random proxies. If False, use sequential rotation.
        """
        self.enabled = enabled
        self.random_rotation = random_rotation


# Default global proxy rotator instance
_default_rotator: Optional[ProxyRotator] = None


def get_proxy_rotator(
    proxy_list: Optional[List[str]] = None,
    use_free_proxies: bool = False,
    force_new: bool = False,
) -> ProxyRotator:
    """
    Get or create a global proxy rotator instance.

    Args:
        proxy_list: List of proxies to initialize with
        use_free_proxies: Whether to fetch free proxies
        force_new: If True, create a new instance instead of using global one

    Returns:
        ProxyRotator instance
    """
    global _default_rotator

    if force_new or _default_rotator is None:
        _default_rotator = ProxyRotator(proxy_list=proxy_list, use_free_proxies=use_free_proxies)

    return _default_rotator
