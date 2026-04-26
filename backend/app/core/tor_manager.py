"""
Tor network integration for proxy rotation.
Tor rotates your IP through volunteer nodes worldwide — completely free.
Changes exit IP approximately every 10 minutes automatically.
"""

import asyncio
import socket
import logging
from typing import Optional
import subprocess
import time

logger = logging.getLogger(__name__)


class TorManager:
    """
    Manages Tor connection and IP rotation.
    Requires: Tor daemon running on localhost:9050 (SOCKS5) and 9051 (control port)
    """

    # Default Tor ports
    SOCKS5_PORT = 9050  # For routing traffic
    CONTROL_PORT = 9051  # For controlling Tor daemon

    def __init__(
        self,
        socks5_port: int = SOCKS5_PORT,
        control_port: int = CONTROL_PORT,
        control_password: str = "",
    ):
        """
        Initialize Tor manager.

        Args:
            socks5_port: Port where Tor SOCKS5 proxy listens (default 9050)
            control_port: Port for Tor control interface (default 9051)
            control_password: Password for control port (if set in torrc)
        """
        self.socks5_port = socks5_port
        self.control_port = control_port
        self.control_password = control_password

    def is_tor_running(self) -> bool:
        """Check if Tor daemon is running and accessible."""
        try:
            sock = socket.create_connection(
                ("127.0.0.1", self.socks5_port),
                timeout=2,
            )
            sock.close()
            logger.info("✓ Tor is running on SOCKS5 port")
            return True
        except (socket.timeout, ConnectionRefusedError, OSError):
            logger.error(
                f"✗ Tor not accessible on port {self.socks5_port}"
            )
            return False

    def get_socks5_proxy_url(self) -> str:
        """Get SOCKS5 proxy URL for httpx/Playwright."""
        return f"socks5://127.0.0.1:{self.socks5_port}"

    def get_httpx_proxies(self) -> dict:
        """
        Get proxy dict for httpx.AsyncClient.

        Returns:
            {"https://": "socks5://127.0.0.1:9050", "http://": "..."}
        """
        proxy_url = self.get_socks5_proxy_url()
        return {
            "https://": proxy_url,
            "http://": proxy_url,
        }

    async def request_new_circuit(self) -> bool:
        """
        Force Tor to establish a new circuit (new exit IP).
        This doesn't guarantee a new IP immediately but starts the process.

        Returns:
            True if successful, False otherwise
        """
        try:
            # Use netcat to send command to Tor control port
            # Command: AUTHENTICATE "" + SIGNAL NEWNYM + QUIT
            cmd = (
                "echo -e 'AUTHENTICATE \"\"\\r\\nSIGNAL NEWNYM\\r\\nQUIT' "
                "| nc -q 1 127.0.0.1 9051"
            )

            logger.info("Requesting new Tor circuit (new IP)...")

            process = await asyncio.create_subprocess_shell(
                cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )

            stdout, stderr = await asyncio.wait_for(
                process.communicate(),
                timeout=5,
            )

            if process.returncode == 0:
                logger.info("✓ New Tor circuit requested successfully")
                # Wait a bit for Tor to establish new circuit
                await asyncio.sleep(2)
                return True
            else:
                logger.warning(
                    f"Tor control returned error: {stderr.decode()}"
                )
                return False

        except asyncio.TimeoutError:
            logger.error("Timeout requesting new Tor circuit")
            return False
        except Exception as e:
            logger.error(f"Error requesting new Tor circuit: {e}")
            return False

    async def get_current_exit_ip(self, client) -> Optional[str]:
        """
        Get your current exit IP from Tor.
        Useful for debugging/verification.

        Args:
            client: httpx.AsyncClient configured to use Tor

        Returns:
            Your current IP address as seen through Tor
        """
        try:
            # Use a service that returns your IP
            response = await client.get(
                "https://api.ipify.org?format=json",
                timeout=10,
            )
            data = response.json()
            ip = data.get("ip", "unknown")
            logger.info(f"Current Tor exit IP: {ip}")
            return ip
        except Exception as e:
            logger.warning(f"Could not get exit IP: {e}")
            return None

    async def rotate_until_new_ip(
        self,
        client,
        old_ip: str,
        max_attempts: int = 5,
        wait_between: int = 3,
    ) -> bool:
        """
        Request new Tor circuit and wait until we actually get a new IP.

        Args:
            client: httpx.AsyncClient configured to use Tor
            old_ip: The IP we want to change from
            max_attempts: Max times to check for new IP
            wait_between: Seconds to wait between checks

        Returns:
            True if new IP acquired, False if timeout
        """
        logger.info(f"Rotating IP from {old_ip}...")

        # Request new circuit
        await self.request_new_circuit()

        # Check if we got a new IP
        for attempt in range(max_attempts):
            await asyncio.sleep(wait_between)

            new_ip = await self.get_current_exit_ip(client)
            if new_ip and new_ip != old_ip:
                logger.info(
                    f"✓ IP rotated successfully: {old_ip} → {new_ip}"
                )
                return True

            logger.debug(f"Attempt {attempt + 1}: Still on old IP, waiting...")

        logger.warning(
            f"Could not rotate IP after {max_attempts} attempts"
        )
        return False


# ============================================================================
# INSTALLATION HELPERS
# ============================================================================


def install_tor_linux() -> bool:
    """
    Install Tor on Linux (Ubuntu/Debian).
    Requires sudo privileges.

    Returns:
        True if successful, False otherwise
    """
    try:
        logger.info("Installing Tor...")
        subprocess.run(
            ["sudo", "apt", "update"],
            check=True,
        )
        subprocess.run(
            ["sudo", "apt", "install", "-y", "tor"],
            check=True,
        )
        logger.info("✓ Tor installed successfully")
        return True
    except subprocess.CalledProcessError as e:
        logger.error(f"Failed to install Tor: {e}")
        return False


def start_tor_service() -> bool:
    """
    Start Tor service on Linux.
    Requires sudo privileges.

    Returns:
        True if successful, False otherwise
    """
    try:
        logger.info("Starting Tor service...")
        subprocess.run(
            ["sudo", "service", "tor", "start"],
            check=True,
        )
        logger.info("✓ Tor service started")

        # Wait for Tor to initialize
        for i in range(10):
            if TorManager().is_tor_running():
                logger.info("✓ Tor is ready")
                return True
            logger.debug(f"Waiting for Tor to start ({i + 1}/10)...")
            time.sleep(1)

        logger.error("Tor started but not responding")
        return False

    except subprocess.CalledProcessError as e:
        logger.error(f"Failed to start Tor: {e}")
        return False


def stop_tor_service() -> bool:
    """
    Stop Tor service on Linux.
    Requires sudo privileges.

    Returns:
        True if successful, False otherwise
    """
    try:
        logger.info("Stopping Tor service...")
        subprocess.run(
            ["sudo", "service", "tor", "stop"],
            check=True,
        )
        logger.info("✓ Tor service stopped")
        return True
    except subprocess.CalledProcessError as e:
        logger.error(f"Failed to stop Tor: {e}")
        return False


# ============================================================================
# SETUP INSTRUCTIONS
# ============================================================================

SETUP_INSTRUCTIONS = """
╔═══════════════════════════════════════════════════════════════════════════╗
║                         TOR SETUP INSTRUCTIONS                            ║
╚═══════════════════════════════════════════════════════════════════════════╝

STEP 1: INSTALL TOR
─────────────────────────────────────────────────────────────────────────────
On Ubuntu/Debian:
    sudo apt update
    sudo apt install -y tor

On macOS (with Homebrew):
    brew install tor

On CentOS/RHEL:
    sudo yum install -y tor

On Windows:
    Download from https://www.torproject.org/download/
    Or use WSL (Windows Subsystem for Linux)


STEP 2: CONFIGURE TOR (Optional)
─────────────────────────────────────────────────────────────────────────────
Edit /etc/tor/torrc (Linux/macOS):
    sudo nano /etc/tor/torrc

Add or uncomment these lines:
    # SOCKS5 proxy (for routing through Tor)
    SocksPort 9050
    
    # Control port (for managing Tor)
    ControlPort 9051
    CookieAuthentication 1

Then restart Tor:
    sudo service tor restart


STEP 3: START TOR
─────────────────────────────────────────────────────────────────────────────
Start Tor service:
    sudo service tor start

Verify it's running:
    netstat -tlnp | grep 9050    # Should show LISTEN on port 9050

Or test with Python:
    python3 -c "from core.tor_manager import TorManager; TorManager().is_tor_running()"


STEP 4: USE IN YOUR SCRAPER
─────────────────────────────────────────────────────────────────────────────
from core.tor_manager import TorManager
import httpx

tor = TorManager()

async with httpx.AsyncClient(proxies=tor.get_httpx_proxies()) as client:
    response = await client.get("https://api.ipify.org")
    print(response.text)

# Get your current exit IP
exit_ip = await tor.get_current_exit_ip(client)
print(f"Your Tor exit IP: {exit_ip}")

# Force new circuit (new IP)
await tor.request_new_circuit()


STEP 5: TEST IT
─────────────────────────────────────────────────────────────────────────────
Check your IP through Tor:
    curl --proxy socks5://127.0.0.1:9050 https://api.ipify.org
    
Run multiple times — your IP should change every 10 minutes automatically.
Force new IP manually: See "request_new_circuit()" above.


TROUBLESHOOTING
─────────────────────────────────────────────────────────────────────────────
Q: Tor not connecting?
A: Check if running: sudo systemctl status tor
   Check firewall: sudo ufw allow 9050 9051

Q: Connection too slow?
A: Tor is naturally slower. Use timeout=30 or higher for httpx.

Q: "Permission denied" on control port?
A: Add your user to tor group:
   sudo usermod -a -G debian-tor $USER
   sudo service tor restart

Q: Exit IP not changing?
A: Wait longer (Tor changes IP every ~10 minutes)
   Or force manually with request_new_circuit()


BENEFITS OF TOR
─────────────────────────────────────────────────────────────────────────────
✓ Completely free
✓ Real IP rotation (thousands of exit nodes worldwide)
✓ No API keys needed
✓ Strong privacy protection
✓ Cannot be easily detected (uses real exit IPs)

DOWNSIDES OF TOR
─────────────────────────────────────────────────────────────────────────────
✗ Slower than direct connection (by design)
✗ Some sites block Tor exit nodes
✗ Requires running Tor daemon separately
"""


if __name__ == "__main__":
    print(SETUP_INSTRUCTIONS)
