"""
Quick Start for Windows Users

This file is for you if you're using Windows!
"""

# ============================================================================
# WINDOWS QUICKSTART (3 MINUTES)
# ============================================================================

"""
STEP 1: Download and Install Tor Browser
─────────────────────────────────────────────────────────────────────────────

1. Go to: https://www.torproject.org/download/
2. Click "Download for Windows"
3. Run the installer
4. Done!


STEP 2: Start Tor Browser
─────────────────────────────────────────────────────────────────────────────

1. Open Tor Browser from Start Menu (or Desktop)
2. Click "Connect" button
3. Wait 30 seconds for connection
4. Keep window open while running your scraper


STEP 3: Test Your Connection (Optional)
─────────────────────────────────────────────────────────────────────────────

Open PowerShell and run:

    python -m core.windows_tor_setup

Then select option "1. Test if Tor is running"


STEP 4: Use in Your Scraper
─────────────────────────────────────────────────────────────────────────────

from core.tor_manager import TorManager
import httpx

tor = TorManager()

async with httpx.AsyncClient(proxies=tor.get_httpx_proxies()) as client:
    response = await client.get("https://example.com")
    print(response.text)

That's it! Your traffic now goes through Tor.


TROUBLESHOOTING
─────────────────────────────────────────────────────────────────────────────

Problem: "Cannot connect to Tor"
Solution: Make sure Tor Browser is open and connected

Problem: "Tor not running on port 9050"
Solution: 
  1. Open Tor Browser
  2. Wait 30 seconds
  3. Check it says "Connected"

Problem: "Port 9050 is blocked"
Solution:
  1. Open PowerShell as Administrator
  2. Run: netsh advfirewall firewall add rule name="Tor" dir=in action=allow protocol=tcp localport=9050
  3. Try again


SETUP HELPER
─────────────────────────────────────────────────────────────────────────────

A Python script to help you:

    python -m core.windows_tor_setup

This gives you a menu to:
- Test Tor connection
- Check firewall
- Download Tor Browser
- View code examples


WHAT IF I DON'T WANT TO USE TOR?
─────────────────────────────────────────────────────────────────────────────

You can also use:
1. Paid proxies (Brightdata, SmartProxy, etc.)
2. Rotating proxy services
3. No proxy (direct connection - but you'll get blocked)

See TOR_GUIDE.md for more options.


NEED HELP?
─────────────────────────────────────────────────────────────────────────────

Read full documentation:
  - TOR_GUIDE.md - Complete guide
  - torrent_manager.py - Source code
  - scraper_with_tor_example.py - Working examples
"""

# ============================================================================
# WINDOWS TOR BROWSER DOWNLOAD
# ============================================================================

TOR_BROWSER_URL = "https://www.torproject.org/download/"
TOR_EXPERT_BUNDLE_URL = "https://www.torproject.org/download/#windows"

# After downloading Tor Browser:
# 1. Run the installer
# 2. Choose installation location (default is fine)
# 3. Click Install
# 4. Open Tor Browser from Start Menu
# 5. Click Connect
# 6. Wait for connection
# 7. Run your scraper!

# ============================================================================
# QUICK PYTHON EXAMPLE
# ============================================================================

EXAMPLE_CODE = """
import asyncio
import httpx
from core.tor_manager import TorManager

async def main():
    # Initialize Tor manager
    tor = TorManager()
    
    # Check if Tor is running
    if not tor.is_tor_running():
        print("ERROR: Tor is not running!")
        print("Please open Tor Browser first")
        return
    
    print("✓ Tor is running")
    
    # Make request through Tor
    async with httpx.AsyncClient(
        proxies=tor.get_httpx_proxies(),
        timeout=30.0,
    ) as client:
        # Check your exit IP
        exit_ip = await tor.get_current_exit_ip(client)
        print(f"Your exit IP: {exit_ip}")
        
        # Make some requests
        urls = [
            "https://example.com",
            "https://example.org",
        ]
        
        for url in urls:
            response = await client.get(url)
            print(f"{url}: {response.status_code}")
            
            # Force new IP
            await tor.request_new_circuit()

if __name__ == "__main__":
    asyncio.run(main())
"""
