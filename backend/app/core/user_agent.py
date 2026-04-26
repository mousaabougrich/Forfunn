"""
User-Agent rotation to mimic different browsers and devices.
Used alongside proxy rotation for better anti-blocking.
"""

import random
import logging
from typing import List, Optional

logger = logging.getLogger(__name__)


class UserAgentRotator:
    """
    Manages rotating through different User-Agent strings.
    Makes requests appear to come from different browsers/devices.
    """

    # Common User-Agent strings from different browsers and devices
    DEFAULT_USER_AGENTS = [
        # Chrome - Windows
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.131 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/93.0.4577.82 Safari/537.36",
        # Chrome - macOS
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.131 Safari/537.36",
        # Firefox - Windows
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:89.0) Gecko/20100101 Firefox/89.0",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:90.0) Gecko/20100101 Firefox/90.0",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:91.0) Gecko/20100101 Firefox/91.0",
        # Firefox - macOS
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:89.0) Gecko/20100101 Firefox/89.0",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:90.0) Gecko/20100101 Firefox/90.0",
        # Safari - macOS
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.1.1 Safari/605.1.15",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.1.2 Safari/605.1.15",
        # Edge - Windows
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36 Edg/91.0.864.59",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.131 Safari/537.36 Edg/92.0.902.67",
        # Mobile - Chrome Android
        "Mozilla/5.0 (Linux; Android 11; SM-G991B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.120 Mobile Safari/537.36",
        "Mozilla/5.0 (Linux; Android 12; SM-S901B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.131 Mobile Safari/537.36",
        # Mobile - Safari iOS
        "Mozilla/5.0 (iPhone; CPU iPhone OS 14_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.1.1 Mobile/15E148 Safari/604.1",
        "Mozilla/5.0 (iPhone; CPU iPhone OS 15_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/15.0 Mobile/15E148 Safari/604.1",
    ]

    def __init__(self, user_agents: Optional[List[str]] = None):
        """
        Initialize User-Agent rotator.

        Args:
            user_agents: Custom list of User-Agent strings. Uses defaults if None.
        """
        self.user_agents = user_agents or self.DEFAULT_USER_AGENTS
        self.current_index = 0
        logger.info(f"Initialized UserAgentRotator with {len(self.user_agents)} agents")

    def get_next_agent(self) -> str:
        """Get the next User-Agent in sequential rotation."""
        agent = self.user_agents[self.current_index]
        self.current_index = (self.current_index + 1) % len(self.user_agents)
        return agent

    def get_random_agent(self) -> str:
        """Get a random User-Agent string."""
        return random.choice(self.user_agents)

    def add_agent(self, agent: str) -> None:
        """Add a custom User-Agent string."""
        if agent not in self.user_agents:
            self.user_agents.append(agent)
            logger.info(f"Added custom User-Agent")

    def reset_rotation(self) -> None:
        """Reset rotation index to beginning."""
        self.current_index = 0


# Global instance
_default_agent_rotator: Optional[UserAgentRotator] = None


def get_user_agent_rotator(
    user_agents: Optional[List[str]] = None,
    force_new: bool = False,
) -> UserAgentRotator:
    """
    Get or create global User-Agent rotator instance.

    Args:
        user_agents: Custom list of agents
        force_new: If True, create new instance

    Returns:
        UserAgentRotator instance
    """
    global _default_agent_rotator

    if force_new or _default_agent_rotator is None:
        _default_agent_rotator = UserAgentRotator(user_agents=user_agents)

    return _default_agent_rotator
