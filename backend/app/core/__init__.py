"""
Core module: Anti-blocking utilities for web scrapers.

Includes:
- Proxy rotation (Tor, paid services, custom proxies)
- User-Agent rotation (17 real browser agents)
- Request delays
- Anti-blocking headers

Quick start:

    # Option 1: Use Tor (FREE - Recommended)
    from core.tor_manager import TorManager
    tor = TorManager()
    proxies = tor.get_httpx_proxies()  # {"https://": "socks5://127.0.0.1:9050"}

    # Option 2: Use custom proxies
    from core.anti_blocking_config import create_moderate_config
    config = create_moderate_config(proxy_list=[...])

    # Option 3: Integrate into scraper
    from core.anti_blocking import AntiBlockingMixin
    class MyScraper(AntiBlockingMixin):
        def __init__(self):
            super().__init__(config)
"""

from core.proxy_manager import ProxyRotator, ProxyConfig, get_proxy_rotator
from core.user_agent import UserAgentRotator, get_user_agent_rotator
from core.anti_blocking import AntiBlockingConfig, AntiBlockingMixin
from core.anti_blocking_config import (
    create_conservative_config,
    create_moderate_config,
    create_aggressive_config,
    create_minimal_config,
    create_tor_config,
    get_tor_manager,
)
from core.tor_manager import TorManager

__all__ = [
    "ProxyRotator",
    "ProxyConfig",
    "get_proxy_rotator",
    "UserAgentRotator",
    "get_user_agent_rotator",
    "AntiBlockingConfig",
    "AntiBlockingMixin",
    "create_conservative_config",
    "create_moderate_config",
    "create_aggressive_config",
    "create_minimal_config",
    "create_tor_config",
    "get_tor_manager",
    "TorManager",
]
