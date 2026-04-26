"""
Windows Tor Setup Helper

This script helps Windows users set up Tor for the price tracker.

Option 1 (Easiest): Download Tor Browser
Option 2 (Advanced): Download Tor Expert Bundle
"""

import os
import sys
import subprocess
import time
import socket
from pathlib import Path


def print_header(text):
    """Print a formatted header."""
    print("\n" + "=" * 70)
    print(f"  {text}")
    print("=" * 70 + "\n")


def check_tor_connection(port=9050):
    """Check if Tor is running and accessible."""
    try:
        sock = socket.create_connection(("127.0.0.1", port), timeout=2)
        sock.close()
        return True
    except (socket.timeout, ConnectionRefusedError, OSError):
        return False


def test_tor():
    """Test if Tor is running."""
    print_header("Testing Tor Connection")
    
    for port in [9050, 9051]:
        if check_tor_connection(port):
            print(f"✓ Tor is running on port {port}")
        else:
            print(f"✗ Tor not found on port {port}")
    
    if check_tor_connection():
        print("\n✓ SUCCESS: Tor is accessible!")
        return True
    else:
        print("\n✗ Tor is not accessible")
        print("Please start Tor first:")
        print("  - Option 1: Open Tor Browser")
        print("  - Option 2: Run C:\\tor\\bin\\tor.exe")
        return False


def check_firewall():
    """Check if Windows Firewall might be blocking Tor."""
    print_header("Checking Firewall")
    
    try:
        # Try to connect to port 9050
        result = subprocess.run(
            ["powershell", "-Command", 
             "Test-NetConnection -ComputerName 127.0.0.1 -Port 9050"],
            capture_output=True,
            text=True,
            timeout=5,
        )
        
        if "TcpTestSucceeded : True" in result.stdout:
            print("✓ Port 9050 is accessible")
            return True
        else:
            print("✗ Port 9050 is blocked by firewall")
            print("\nTry adding firewall exception:")
            print("  Run as Administrator:")
            print("  netsh advfirewall firewall add rule name=\"Tor SOCKS5\" " 
                  "dir=in action=allow protocol=tcp localport=9050")
            return False
    except Exception as e:
        print(f"Could not check firewall: {e}")
        return False


def open_tor_browser_download():
    """Open Tor Browser download page."""
    print_header("Opening Tor Browser Download")
    
    import webbrowser
    url = "https://www.torproject.org/download/"
    print(f"Opening: {url}")
    webbrowser.open(url)
    time.sleep(1)


def show_python_examples():
    """Show Python code examples."""
    print_header("Python Usage Examples")
    
    print("""
1. SIMPLE REQUEST:
   
   from core.tor_manager import TorManager
   import httpx
   
   tor = TorManager()
   async with httpx.AsyncClient(proxies=tor.get_httpx_proxies()) as client:
       response = await client.get("https://example.com")


2. CHECK YOUR IP:
   
   from core.tor_manager import TorManager
   import httpx
   
   tor = TorManager()
   async with httpx.AsyncClient(proxies=tor.get_httpx_proxies()) as client:
       ip = await tor.get_current_exit_ip(client)
       print(f"Your IP: {ip}")


3. FORCE NEW IP:
   
   await tor.request_new_circuit()
   new_ip = await tor.get_current_exit_ip(client)
   print(f"New IP: {new_ip}")


4. MULTIPLE URLS WITH ROTATION:
   
   urls = ["https://example.com/1", "https://example.com/2"]
   for url in urls:
       response = await client.get(url)
       await tor.request_new_circuit()
       
""")


def show_troubleshooting():
    """Show troubleshooting steps."""
    print_header("Troubleshooting")
    
    print("""
ISSUE 1: "Cannot connect to Tor"
  Solution:
    1. Open Tor Browser from Start Menu
    2. Wait 30 seconds for it to connect
    3. Keep Tor Browser open while running your script

ISSUE 2: "Tor not found on port 9050"
  Solution:
    1. Download Tor Browser: https://www.torproject.org/download/
    2. Run it
    3. Or run C:\\tor\\bin\\tor.exe

ISSUE 3: "Port 9050 is blocked by firewall"
  Solution:
    1. Open PowerShell as Administrator
    2. Run: netsh advfirewall firewall add rule name="Tor" dir=in action=allow protocol=tcp localport=9050
    3. Try again

ISSUE 4: "Permission denied"
  Solution:
    1. Run PowerShell as Administrator
    2. Then run your script
    
""")


def get_python_code_snippet():
    """Get basic Python integration code."""
    return '''
import asyncio
import httpx
from core.tor_manager import TorManager

async def main():
    tor = TorManager()
    
    if not tor.is_tor_running():
        print("ERROR: Tor is not running!")
        print("1. Open Tor Browser from Start Menu")
        print("2. Keep it open")
        return
    
    print("✓ Tor is running!")
    
    async with httpx.AsyncClient(proxies=tor.get_httpx_proxies()) as client:
        # Get your exit IP
        exit_ip = await tor.get_current_exit_ip(client)
        print(f"Your Tor exit IP: {exit_ip}")
        
        # Make a request
        response = await client.get("https://httpbin.org/user-agent")
        print(f"Response: {response.text}")

if __name__ == "__main__":
    asyncio.run(main())
'''


def main():
    """Main menu."""
    os.system("cls" if os.name == "nt" else "clear")
    
    print_header("Universal Price Tracker - Windows Tor Setup")
    
    print("""
Welcome! This helper will guide you through setting up Tor on Windows.

WHAT IS TOR?
  Tor rotates your IP through volunteer nodes worldwide - completely free!
  Perfect for web scraping without getting blocked.

DO YOU NEED TOR?
  - YES if you want to scrape many pages without getting blocked
  - NO if you're just testing

QUICK START:
  1. Download Tor Browser: https://www.torproject.org/download/
  2. Install and run it
  3. Use in Python (see examples below)

""")
    
    while True:
        print("\nWhat do you want to do?")
        print("  1. Test if Tor is running")
        print("  2. Check firewall")
        print("  3. Download Tor Browser")
        print("  4. Show Python examples")
        print("  5. Show troubleshooting")
        print("  6. Get Python integration code")
        print("  0. Exit")
        
        choice = input("\nEnter choice (0-6): ").strip()
        
        if choice == "0":
            print("Goodbye!")
            break
        elif choice == "1":
            test_tor()
        elif choice == "2":
            check_firewall()
        elif choice == "3":
            open_tor_browser_download()
        elif choice == "4":
            show_python_examples()
        elif choice == "5":
            show_troubleshooting()
        elif choice == "6":
            print_header("Python Integration Code")
            code = get_python_code_snippet()
            print(code)
            print("\nCopy this to your Python file to use Tor!")
        else:
            print("Invalid choice, try again")
        
        input("\nPress Enter to continue...")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nInterrupted by user")
    except Exception as e:
        print(f"Error: {e}")
