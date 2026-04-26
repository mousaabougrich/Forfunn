"""
Anti-blocking configuration and proxy setup.
Import and use these in your scrapers.

Supports three methods:
1. Local proxies (Tor, paid services, etc.)
2. Proxy rotation (sequential or random)
3. Anti-blocking headers (User-Agent, cookies, etc.)
"""

from typing import List, Optional
from core.anti_blocking import AntiBlockingConfig, AntiBlockingMixin
from core.proxy_manager import ProxyRotator, get_proxy_rotator
from core.user_agent import UserAgentRotator, get_user_agent_rotator
from core.tor_manager import TorManager


# ============================================================================
# PROXY CONFIGURATION
# ============================================================================

# Free proxy options (use with caution - can be slow/unreliable)
FREE_PROXY_SOURCES = [
    "https://www.proxy-list.download/api/v1/get?type=http",
    "https://api.proxyscrape.com/v2/?request=getproxies&protocol=http",
    "https://raw.githubusercontent.com/clarketm/proxy-list/master/proxy-list-raw.txt",
]

# Example paid proxy services (for production)
PAID_PROXY_EXAMPLES = {
    "brightdata": "http://user:pass@proxy.provider.com:port",
    "smartproxy": "http://user:pass@gate.smartproxy.com:7000",
    "oxylabs": "http://user:pass@pr.oxylabs.io:7777",
}

# Local proxy list (add your own proxies here)
LOCAL_PROXIES: List[str] = [
    # Format: "http://ip:port" or "http://user:password@ip:port"
    # Example:
    # "http://10.0.0.1:8080",
    # "http://proxy.company.com:3128",
]


# ============================================================================
# TOR CONFIGURATION (RECOMMENDED - FREE & RELIABLE)
# ============================================================================

# Tor provides free IP rotation through volunteer nodes worldwide
# No API keys, no paid subscriptions, completely free and anonymous
# Slower than proxies but more reliable for anti-blocking

def create_tor_config() -> AntiBlockingConfig:
    """
    Create anti-blocking config using Tor network.
    
    Tor rotates your IP through volunteer nodes worldwide.
    Setup: See tor_manager.py setup instructions or run:
        sudo apt install tor
        sudo service tor start
    
    Returns:
        AntiBlockingConfig using Tor proxy
    """
    tor = TorManager()
    
    if not tor.is_tor_running():
        raise RuntimeError(
            "Tor is not running. Start it with: sudo service tor start"
        )
    
    # Get SOCKS5 proxy URL from Tor
    # We'll create a proxy list with just the Tor proxy
    # Tor automatically rotates the exit IP every ~10 minutes
    tor_proxy = tor.get_socks5_proxy_url()
    
    return AntiBlockingConfig(
        use_proxy_rotation=False,  # Tor handles rotation automatically
        use_user_agent_rotation=True,  # Still rotate User-Agent
        min_delay_seconds=1.0,
        max_delay_seconds=3.0,
        proxy_list=[tor_proxy],
    )


def get_tor_manager() -> TorManager:
    """
    Get Tor manager instance.
    
    Usage:
        tor = get_tor_manager()
        exit_ip = await tor.get_current_exit_ip(client)
        await tor.request_new_circuit()  # Force new IP
    
    Returns:
        TorManager instance
    """
    return TorManager()


# ============================================================================
# ANTI-BLOCKING PRESETS
# ============================================================================


def create_conservative_config(proxy_list: Optional[List[str]] = None) -> AntiBlockingConfig:
    """
    Conservative anti-blocking: Random delays, proxies, User-Agents.
    Best for scrapers that need to be very stealthy.
    """
    return AntiBlockingConfig(
        use_proxy_rotation=True,
        use_user_agent_rotation=True,
        min_delay_seconds=2.0,  # Longer delays
        max_delay_seconds=5.0,
        proxy_list=proxy_list or LOCAL_PROXIES,
    )


def create_moderate_config(proxy_list: Optional[List[str]] = None) -> AntiBlockingConfig:
    """
    Moderate anti-blocking: Balanced approach.
    Good for most production scrapers.
    """
    return AntiBlockingConfig(
        use_proxy_rotation=True,
        use_user_agent_rotation=True,
        min_delay_seconds=1.0,
        max_delay_seconds=3.0,
        proxy_list=proxy_list or LOCAL_PROXIES,
    )


def create_aggressive_config(proxy_list: Optional[List[str]] = None) -> AntiBlockingConfig:
    """
    Aggressive anti-blocking: Minimal delays.
    Use when speed is more important than stealth.
    Note: Higher risk of being blocked.
    """
    return AntiBlockingConfig(
        use_proxy_rotation=True,
        use_user_agent_rotation=True,
        min_delay_seconds=0.5,
        max_delay_seconds=1.5,
        proxy_list=proxy_list or LOCAL_PROXIES,
    )


def create_minimal_config() -> AntiBlockingConfig:
    """
    Minimal anti-blocking: Only User-Agent rotation, no proxies or delays.
    Use for development/testing or trusted sites.
    """
    return AntiBlockingConfig(
        use_proxy_rotation=False,
        use_user_agent_rotation=True,
        min_delay_seconds=0.0,
        max_delay_seconds=0.0,
    )


# ============================================================================
# USAGE EXAMPLES
# ============================================================================

"""
In your scraper base class:

from anti_blocking_config import create_moderate_config, AntiBlockingMixin

class BaseScraper(AntiBlockingMixin):
    def __init__(self, use_anti_blocking: bool = True):
        config = create_moderate_config() if use_anti_blocking else None
        super().__init__(config)

    async def fetch_with_httpx(self, client, url):
        # Get anti-blocking headers
        headers = self.get_httpx_headers()
        proxies = self.get_httpx_proxies()
        
        # Wait before request
        await self.wait_before_request()
        
        # Make request
        response = await client.get(url, headers=headers, proxies=proxies)
        return response

    async def fetch_with_playwright(self, browser):
        # Get anti-blocking context options
        context_options = self.get_playwright_context_options()
        
        # Create context
        async with await browser.new_context(**context_options) as context:
            page = await context.new_page()
            await page.goto(self.url)
            # ... rest of Playwright code

"""

# ============================================================================
# SETUP INSTRUCTIONS
# ============================================================================

"""
HOW TO ADD PROXIES:

1. OPTION 1: Use local proxies
   - Add proxies to LOCAL_PROXIES list in this file
   - Format: "http://ip:port" or "http://user:password@ip:port"

2. OPTION 2: Use Tor (RECOMMENDED - FREE!)
   - Free IP rotation through volunteer nodes worldwide
   - Setup:
     sudo apt install tor
     sudo service tor start
   - Usage:
     config = create_tor_config()
     
3. OPTION 3: Use paid proxy service
   - Sign up with service (Brightdata, SmartProxy, Oxylabs, etc.)
   - Get proxy URL from service
   - Add to LOCAL_PROXIES or pass to config

4. OPTION 4: Use rotating proxy service API
   - Call their API to get proxy list
   - Store in LOCAL_PROXIES

EXAMPLE 1 - Using Tor (Free, Recommended):

    from anti_blocking_config import create_tor_config
    import httpx
    
    config = create_tor_config()
    
    headers = {"User-Agent": config.user_agent_rotator.get_next_agent()}
    proxies = {"https://": "socks5://127.0.0.1:9050"}
    
    async with httpx.AsyncClient(proxies=proxies) as client:
        response = await client.get(url, headers=headers)
        content = response.text

EXAMPLE 2 - Using Tor with automatic circuit rotation:

    from anti_blocking_config import get_tor_manager
    import httpx
    
    tor = get_tor_manager()
    
    async with httpx.AsyncClient(proxies=tor.get_httpx_proxies()) as client:
        # Check current exit IP
        exit_ip = await tor.get_current_exit_ip(client)
        print(f"Current IP: {exit_ip}")
        
        # Make requests (Tor rotates IP every ~10 minutes)
        response = await client.get(url)
        
        # Force new IP if needed
        old_ip = exit_ip
        await tor.request_new_circuit()
        new_ip = await tor.get_current_exit_ip(client)
        print(f"New IP: {new_ip}")

EXAMPLE 3 - Adding paid proxies:

    from anti_blocking_config import create_moderate_config
    
    PAID_PROXIES = [
        "http://user:pass@proxy1.brightdata.com:port",
        "http://user:pass@proxy2.brightdata.com:port",
    ]
    
    config = create_moderate_config(proxy_list=PAID_PROXIES)

EXAMPLE 4 - Integrate into BaseScraper:

    from anti_blocking_config import create_tor_config, AntiBlockingMixin
    
    class BaseScraper(AntiBlockingMixin):
        def __init__(self):
            config = create_tor_config()
            super().__init__(config)
        
        async def fetch(self, client, url):
            headers = self.get_httpx_headers()
            proxies = self.get_httpx_proxies()
            await self.wait_before_request()
            return await client.get(url, headers=headers, proxies=proxies)
"""
