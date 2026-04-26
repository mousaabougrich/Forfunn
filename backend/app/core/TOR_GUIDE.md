# Anti-Blocking System: Tor Network Guide

## Windows Users: Quick Start (3 minutes)

### Option 1: Tor Browser (Recommended - Easiest)

1. **Download Tor Browser**
   - Go to https://www.torproject.org/download/
   - Click "Download for Windows"
   - Run the installer

2. **Start Tor Browser**
   - Open Tor Browser
   - Wait for it to connect (30 seconds)
   - You're done! Tor is now running on `127.0.0.1:9050`

3. **Use in Python**
   ```python
   from core.tor_manager import TorManager
   import httpx
   
   tor = TorManager()  # Will find Tor Browser automatically
   
   async with httpx.AsyncClient(proxies=tor.get_httpx_proxies()) as client:
       response = await client.get("https://example.com")
   ```

### Option 2: Tor Standalone (Advanced)

1. **Download Tor Expert Bundle**
   - Go to https://www.torproject.org/download/#windows
   - Download "Tor Expert Bundle for Windows"
   - Extract to `C:\tor` (or any folder)

2. **Run Tor**
   - Open PowerShell as Administrator
   - Run:
     ```powershell
     cd C:\tor\bin
     .\tor.exe
     ```
   - Keep this window open

3. **Use in Python** (same as above)

---

### 1. Install Tor

#### Windows (Easiest - Tor Browser)
1. Download Tor Browser: https://www.torproject.org/download/
2. Install it (Windows installer available)
3. Run Tor Browser

Or standalone (advanced):
1. Download Tor Expert Bundle: https://www.torproject.org/download/#windows
2. Extract to a folder
3. Run `tor.exe` from the bin folder

#### macOS (with Homebrew)
```bash
brew install tor
```

#### Ubuntu/Debian (Linux)
```bash
sudo apt update
sudo apt install -y tor
```

#### CentOS/RHEL (Linux)
```bash
sudo yum install -y tor
```

#### WSL (Windows Subsystem for Linux)
```bash
# Install WSL2 first, then:
sudo apt update
sudo apt install -y tor
```

### 2. Start Tor

#### Windows (Tor Browser)
- Just open Tor Browser application
- Tor runs automatically on port 9050

#### Windows (Standalone tor.exe)
```cmd
# In PowerShell or Command Prompt
cd C:\path\to\tor\bin
.\tor.exe
```

#### macOS/Linux
```bash
# Start service
brew services start tor    # macOS
sudo service tor start     # Linux
```

### 3. Verify Tor is Running

#### Windows (PowerShell)
```powershell
# Test connection to port 9050
Test-NetConnection -ComputerName 127.0.0.1 -Port 9050
# Should show: TcpTestSucceeded : True
```

#### macOS/Linux
```bash
netstat -tlnp | grep 9050
# or
ss -tlnp | grep 9050
```

### 3. Use in Your Scraper

```python
import httpx
from core.tor_manager import TorManager

# Initialize Tor manager
tor = TorManager()

# Get proxy URL for httpx
proxies = tor.get_httpx_proxies()

# Make requests through Tor
async with httpx.AsyncClient(proxies=proxies) as client:
    response = await client.get("https://example.com")
    print(response.text)
```

That's it! Your requests now go through Tor.

---

## Understanding Tor

### What is Tor?

Tor is a volunteer-operated network that routes your internet traffic through multiple computers worldwide, encrypting it multiple times. Your traffic exits through one of thousands of volunteer nodes.

### Why Use Tor for Scraping?

✅ **Completely free** — No API keys, no monthly fees  
✅ **Real IP rotation** — Uses thousands of volunteer nodes  
✅ **Cannot be easily detected** — Looks like real traffic  
✅ **Privacy-preserving** — Nobody sees what you're accessing  
✅ **Reliable** — Tor nodes rarely get blocked  

### IP Rotation Behavior

- Tor **automatically** rotates your exit IP every ~10 minutes
- Different websites see different IPs
- Perfect for large-scale scraping

### Speed Considerations

⚠️ **Tor is slower** — By design, for privacy

Typical speeds:
- Direct connection: ~100ms
- Through Tor: ~500ms - 2000ms (depends on circuit quality)

This is acceptable for most web scraping scenarios.

---

## Code Examples

### Example 1: Simple HTTP Request

```python
import httpx
from core.tor_manager import TorManager

tor = TorManager()

async with httpx.AsyncClient(proxies=tor.get_httpx_proxies()) as client:
    response = await client.get("https://api.ipify.org?format=json")
    print(response.json())  # See your Tor exit IP
```

### Example 2: Check Your Current IP

```python
from core.tor_manager import TorManager
import httpx

tor = TorManager()

async with httpx.AsyncClient(proxies=tor.get_httpx_proxies()) as client:
    # Get your exit IP
    exit_ip = await tor.get_current_exit_ip(client)
    print(f"You're exiting Tor at: {exit_ip}")
```

### Example 3: Force New IP (New Circuit)

```python
from core.tor_manager import TorManager
import httpx

tor = TorManager()

async with httpx.AsyncClient(proxies=tor.get_httpx_proxies()) as client:
    # Check IP before rotation
    old_ip = await tor.get_current_exit_ip(client)
    print(f"Old IP: {old_ip}")
    
    # Request new circuit
    await tor.request_new_circuit()
    
    # Wait for new IP
    new_ip = await tor.get_current_exit_ip(client)
    print(f"New IP: {new_ip}")
```

### Example 4: Scrape Multiple URLs with Rotation

```python
from core.tor_manager import TorManager
from core.user_agent import UserAgentRotator
import httpx

tor = TorManager()
ua_rotator = UserAgentRotator()

urls = [
    "https://example.com/page1",
    "https://example.com/page2",
    "https://example.com/page3",
]

async with httpx.AsyncClient(proxies=tor.get_httpx_proxies()) as client:
    for i, url in enumerate(urls):
        # Get rotated headers
        headers = {
            "User-Agent": ua_rotator.get_random_agent(),
            "Accept-Language": "en-US,en;q=0.9",
        }
        
        # Make request
        response = await client.get(url, headers=headers)
        print(f"{i+1}. {url}: {response.status_code}")
        
        # Request new circuit between requests
        if i < len(urls) - 1:
            await tor.request_new_circuit()
            await asyncio.sleep(2)
```

### Example 5: Integrate into Base Scraper

```python
from core.anti_blocking import AntiBlockingMixin, AntiBlockingConfig
from core.tor_manager import TorManager
import httpx

class BaseScraper(AntiBlockingMixin):
    def __init__(self):
        # Use Tor for anti-blocking
        tor = TorManager()
        config = AntiBlockingConfig(
            use_proxy_rotation=False,  # Tor handles rotation
            use_user_agent_rotation=True,
            min_delay_seconds=1.0,
            max_delay_seconds=3.0,
            proxy_list=[tor.get_socks5_proxy_url()],
        )
        super().__init__(config)
        self.tor = tor
    
    async def fetch(self, url):
        async with httpx.AsyncClient(
            proxies=self.get_httpx_proxies()
        ) as client:
            await self.wait_before_request()
            return await client.get(url, headers=self.get_request_headers())


class AmazonScraper(BaseScraper):
    async def scrape(self, keyword):
        url = f"https://www.amazon.com/s?k={keyword}"
        content = await self.fetch(url)
        # Parse content...
```

---

## Using with Playwright

```python
from core.tor_manager import TorManager
from playwright.async_api import async_playwright

tor = TorManager()

async with async_playwright() as p:
    browser = await p.chromium.launch()
    
    # Create context with Tor proxy
    async with await browser.new_context(
        proxy={"server": tor.get_socks5_proxy_url()}
    ) as context:
        page = await context.new_page()
        await page.goto("https://example.com")
        content = await page.content()
```

---

## Troubleshooting

### Windows Issues

#### Issue: "Cannot connect to Tor proxy"

**Solution:**
1. Open Tor Browser (or run `tor.exe` in command prompt)
2. Wait 30 seconds for Tor to connect
3. Check connection in PowerShell:
```powershell
Test-NetConnection -ComputerName 127.0.0.1 -Port 9050
```

#### Issue: "Cannot find tor.exe"

**Solution - Install Tor correctly:**

Option 1 (Easiest): Use Tor Browser
```
Download from https://www.torproject.org/download/
Install and run
```

Option 2: Use Tor Expert Bundle
```
1. Download: https://www.torproject.org/download/#windows
2. Extract to C:\tor (or anywhere)
3. Run: C:\tor\bin\tor.exe
```

Option 3: Use Chocolatey (if installed)
```powershell
choco install tor
```

#### Issue: Port 9050 is blocked by firewall

```powershell
# Windows Defender Firewall - usually allows localhost automatically
# If blocked, add exception:
netsh advfirewall firewall add rule name="Tor SOCKS5" dir=in action=allow protocol=tcp localport=9050
```

#### Issue: "Permission denied" errors on Windows

**Solution:** Run as Administrator
```powershell
# Right-click PowerShell or Command Prompt, select "Run as administrator"
cd C:\tor\bin
.\tor.exe
```

### Linux Issues

#### Issue: "Tor is not running"

```
RuntimeError: Tor is not running!
Start it with: sudo service tor start
```

**Solution:**
```bash
sudo service tor start
# or
sudo systemctl start tor

# Check if running
sudo service tor status
```

#### Issue: "Permission denied" on control port

```
Error requesting new Tor circuit: [Errno 13] Permission denied
```

**Solution:**
```bash
# Add your user to tor group
sudo usermod -a -G debian-tor $USER
# Then restart Tor
sudo service tor restart
# You may need to log out and log back in
```

### Issue: Connections too slow

Tor is slower by design. If you need faster scraping:
- Use paid proxies instead
- Accept longer timeouts (httpx timeout=60)
- Scrape fewer pages in parallel

### Issue: Some sites block Tor

Some websites detect and block Tor exit nodes. Options:
- Use those sites' official APIs
- Combine Tor with User-Agent/header rotation
- Use residential proxies for those specific sites
- Use Tor + rotating residential proxies

### Issue: "Cannot connect to Tor"

```
Exception: Failed to connect to Tor proxy at 127.0.0.1:9050
```

**Debug steps:**
```bash
# 1. Check Tor is running
sudo service tor status

# 2. Check port 9050 is listening
netstat -tlnp | grep 9050

# 3. Check if firewall is blocking
sudo ufw allow 9050

# 4. Test connection manually
curl --proxy socks5://127.0.0.1:9050 https://api.ipify.org
```

---

## Configuration

### Change Tor Ports

If 9050/9051 are in use, modify `/etc/tor/torrc`:

```bash
sudo nano /etc/tor/torrc
```

Change:
```
SocksPort 9050    # Change to 9999
ControlPort 9051  # Change to 9052
```

Then restart:
```bash
sudo service tor restart
```

And update your Python code:
```python
tor = TorManager(socks5_port=9999, control_port=9052)
```

### Enable Authentication (Optional)

In `/etc/tor/torrc`:
```
ControlPort 9051
HashedControlPassword 16:0ABCD1234567890...  # Run: tor --hash-password "your_password"
```

### Exit Node Selection

To prefer specific countries (advanced):
```bash
# In /etc/tor/torrc, add:
ExitNodes {us},{uk},{de}  # Prefer exits in US, UK, Germany
```

---

## Monitoring

### Monitor Tor Status

```bash
# See if Tor is running
sudo systemctl status tor

# See Tor logs
sudo journalctl -u tor -f

# See detailed Tor info
ps aux | grep tor
```

### Monitor Exit IPs

```python
# Check multiple IPs to see rotation
import asyncio
from core.tor_manager import TorManager
import httpx

tor = TorManager()

async with httpx.AsyncClient(proxies=tor.get_httpx_proxies()) as client:
    for i in range(10):
        ip = await tor.get_current_exit_ip(client)
        print(f"{i+1}. {ip}")
        await tor.request_new_circuit()
        await asyncio.sleep(2)
```

---

## Best Practices

1. **Always respect websites' terms of service**
   - Tor is legal, but using it to violate ToS is not

2. **Add delays between requests**
   ```python
   await asyncio.sleep(random.uniform(1, 3))
   ```

3. **Rotate User-Agent headers** (not just IP)
   ```python
   headers = {"User-Agent": ua_rotator.get_random_agent()}
   ```

4. **Handle failures gracefully**
   ```python
   try:
       response = await client.get(url)
   except Exception as e:
       logger.error(f"Request failed: {e}")
       await tor.request_new_circuit()  # Try with new IP
   ```

5. **Monitor for blocks**
   ```python
   if response.status_code == 403:
       logger.warning("Got blocked, requesting new circuit")
       await tor.request_new_circuit()
   ```

6. **Use headless Playwright for JS sites**
   - HTTPX + Tor works for static HTML
   - Use Playwright + Tor for JavaScript-heavy sites

---

## Comparison: Tor vs Paid Proxies

| Feature | Tor | Paid Proxies | Free Proxies |
|---------|-----|--------------|--------------|
| Cost | Free | $10-100/mo | Free |
| Speed | Slow | Medium | Very Slow |
| Reliability | High | High | Low |
| Detection | Hard | Medium | Easy |
| Legality | Legal | Legal* | Legal* |
| Setup | 5 min | 1 min | 5 min |

*Always check service ToS

---

## Files Reference

- **core/tor_manager.py** — Tor management and circuit control
- **core/anti_blocking_config.py** — Configuration helpers
- **core/scraper_with_tor_example.py** — Full working examples
- **core/anti_blocking.py** — Mixin for integrating into scrapers
- **core/user_agent.py** — User-Agent rotation
