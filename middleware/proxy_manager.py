"""
Proxy Management and User-Agent Rotation
Handles proxy rotation, health checking, and user-agent management
"""

import asyncio
import random
import time
import logging
from typing import List, Optional, Dict
from dataclasses import dataclass, field
from enum import Enum
import httpx

logger = logging.getLogger(__name__)


class ProxyHealth(Enum):
    """Proxy health status"""
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    FAILED = "failed"


@dataclass
class ProxyInfo:
    """Information about a proxy"""
    url: str
    health: ProxyHealth = ProxyHealth.HEALTHY
    success_count: int = 0
    failure_count: int = 0
    avg_response_time: float = 0.0
    last_checked: float = field(default_factory=time.time)
    total_requests: int = 0

    @property
    def success_rate(self) -> float:
        """Calculate success rate"""
        if self.total_requests == 0:
            return 1.0
        return self.success_count / self.total_requests

    @property
    def score(self) -> float:
        """
        Calculate proxy score for health-based selection

        Higher is better. Considers:
        - Success rate (70%)
        - Response time (30%)
        """
        success_score = self.success_rate * 0.7

        # Response time score (inverse, normalized)
        # Fast proxies (< 1s) get high score, slow proxies (> 10s) get low score
        time_score = max(0, 1 - (self.avg_response_time / 10)) * 0.3

        return success_score + time_score


class ProxyManager:
    """
    Proxy rotation manager with health checking

    Features:
    - Multiple rotation strategies (round-robin, random, health-based)
    - Automatic health monitoring
    - Failed proxy removal and retry
    - Performance tracking
    """

    def __init__(
        self,
        proxies: List[str],
        rotation_strategy: str = "round_robin",  # or 'random', 'health_based'
        health_check_interval: int = 300,  # seconds
        health_check_url: str = "http://httpbin.org/ip",
        max_failures: int = 3
    ):
        """
        Initialize proxy manager

        Args:
            proxies: List of proxy URLs (e.g., 'http://user:pass@proxy:port')
            rotation_strategy: How to select proxies
            health_check_interval: Seconds between health checks
            health_check_url: URL to use for health checks
            max_failures: Max failures before marking proxy as failed
        """
        self.proxies = {url: ProxyInfo(url=url) for url in proxies}
        self.rotation_strategy = rotation_strategy
        self.health_check_interval = health_check_interval
        self.health_check_url = health_check_url
        self.max_failures = max_failures

        self._current_index = 0
        self._lock = asyncio.Lock()
        self._health_check_task = None

        logger.info(
            f"ProxyManager initialized: {len(proxies)} proxies, "
            f"strategy={rotation_strategy}"
        )

    def get_proxy(self) -> Optional[str]:
        """
        Get next proxy based on rotation strategy

        Returns:
            Proxy URL or None if no healthy proxies
        """
        healthy_proxies = [
            info for info in self.proxies.values()
            if info.health != ProxyHealth.FAILED
        ]

        if not healthy_proxies:
            logger.error("No healthy proxies available")
            return None

        if self.rotation_strategy == "round_robin":
            proxy = self._round_robin_select(healthy_proxies)
        elif self.rotation_strategy == "random":
            proxy = random.choice(healthy_proxies)
        elif self.rotation_strategy == "health_based":
            proxy = self._health_based_select(healthy_proxies)
        else:
            proxy = healthy_proxies[0]

        logger.debug(f"Selected proxy: {proxy.url} (score={proxy.score:.2f})")
        return proxy.url

    def _round_robin_select(self, proxies: List[ProxyInfo]) -> ProxyInfo:
        """Round-robin proxy selection"""
        proxy = proxies[self._current_index % len(proxies)]
        self._current_index += 1
        return proxy

    def _health_based_select(self, proxies: List[ProxyInfo]) -> ProxyInfo:
        """Select proxy based on health score"""
        # Weight selection by score
        scores = [proxy.score for proxy in proxies]
        total_score = sum(scores)

        if total_score == 0:
            return random.choice(proxies)

        # Weighted random selection
        weights = [score / total_score for score in scores]
        return random.choices(proxies, weights=weights)[0]

    async def record_success(self, proxy_url: str, response_time: float):
        """
        Record successful request

        Args:
            proxy_url: Proxy that was used
            response_time: Response time in seconds
        """
        async with self._lock:
            if proxy_url in self.proxies:
                proxy = self.proxies[proxy_url]
                proxy.success_count += 1
                proxy.total_requests += 1

                # Update average response time (exponential moving average)
                alpha = 0.2  # Weight for new value
                proxy.avg_response_time = (
                    alpha * response_time +
                    (1 - alpha) * proxy.avg_response_time
                )

                # Reset to healthy if it was degraded
                if proxy.health == ProxyHealth.DEGRADED:
                    proxy.health = ProxyHealth.HEALTHY
                    logger.info(f"Proxy recovered: {proxy_url}")

    async def record_failure(self, proxy_url: str):
        """
        Record failed request

        Args:
            proxy_url: Proxy that failed
        """
        async with self._lock:
            if proxy_url in self.proxies:
                proxy = self.proxies[proxy_url]
                proxy.failure_count += 1
                proxy.total_requests += 1

                # Update health status
                if proxy.failure_count >= self.max_failures:
                    proxy.health = ProxyHealth.FAILED
                    logger.error(f"Proxy marked as failed: {proxy_url}")
                elif proxy.success_rate < 0.5:
                    proxy.health = ProxyHealth.DEGRADED
                    logger.warning(f"Proxy degraded: {proxy_url}")

    async def start_health_checks(self):
        """Start background health checking"""
        if not self._health_check_task:
            self._health_check_task = asyncio.create_task(self._health_check_loop())
            logger.info("Health check loop started")

    async def stop_health_checks(self):
        """Stop background health checking"""
        if self._health_check_task:
            self._health_check_task.cancel()
            try:
                await self._health_check_task
            except asyncio.CancelledError:
                pass
            self._health_check_task = None
            logger.info("Health check loop stopped")

    async def _health_check_loop(self):
        """Background task to periodically check proxy health"""
        while True:
            try:
                await asyncio.sleep(self.health_check_interval)
                await self._check_all_proxies()
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in health check loop: {e}")

    async def _check_all_proxies(self):
        """Check health of all proxies"""
        logger.info("Starting proxy health checks")

        tasks = [
            self._check_proxy(proxy_url)
            for proxy_url in self.proxies.keys()
        ]

        await asyncio.gather(*tasks, return_exceptions=True)

    async def _check_proxy(self, proxy_url: str):
        """
        Check single proxy health

        Args:
            proxy_url: Proxy to check
        """
        try:
            start_time = time.time()

            async with httpx.AsyncClient(proxies=proxy_url, timeout=10.0) as client:
                response = await client.get(self.health_check_url)
                response.raise_for_status()

            response_time = time.time() - start_time

            await self.record_success(proxy_url, response_time)
            logger.debug(f"Proxy health check passed: {proxy_url} ({response_time:.2f}s)")

        except Exception as e:
            await self.record_failure(proxy_url)
            logger.warning(f"Proxy health check failed: {proxy_url} - {e}")

    def get_stats(self) -> Dict:
        """Get proxy statistics"""
        stats = {
            'total_proxies': len(self.proxies),
            'healthy': sum(1 for p in self.proxies.values() if p.health == ProxyHealth.HEALTHY),
            'degraded': sum(1 for p in self.proxies.values() if p.health == ProxyHealth.DEGRADED),
            'failed': sum(1 for p in self.proxies.values() if p.health == ProxyHealth.FAILED),
            'proxies': []
        }

        for proxy in self.proxies.values():
            stats['proxies'].append({
                'url': proxy.url,
                'health': proxy.health.value,
                'success_rate': proxy.success_rate,
                'avg_response_time': proxy.avg_response_time,
                'total_requests': proxy.total_requests,
                'score': proxy.score
            })

        return stats


class UserAgentManager:
    """
    User-Agent string management and rotation

    Provides realistic browser user-agents to avoid detection
    """

    # Curated list of real browser user-agents
    USER_AGENTS = [
        # Chrome on Windows
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36',

        # Chrome on Mac
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36',

        # Firefox on Windows
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0',
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:120.0) Gecko/20100101 Firefox/120.0',

        # Firefox on Mac
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:121.0) Gecko/20100101 Firefox/121.0',

        # Safari on Mac
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.1 Safari/605.1.15',

        # Edge on Windows
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36 Edg/120.0.0.0',

        # Chrome on Linux
        'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    ]

    def __init__(self, rotation_strategy: str = "random"):
        """
        Initialize user-agent manager

        Args:
            rotation_strategy: 'random' or 'round_robin'
        """
        self.rotation_strategy = rotation_strategy
        self._current_index = 0
        self._lock = asyncio.Lock()

        logger.info(
            f"UserAgentManager initialized: {len(self.USER_AGENTS)} agents, "
            f"strategy={rotation_strategy}"
        )

    def get(self) -> str:
        """
        Get user-agent string

        Returns:
            User-Agent string
        """
        if self.rotation_strategy == "round_robin":
            ua = self.USER_AGENTS[self._current_index % len(self.USER_AGENTS)]
            self._current_index += 1
        else:
            ua = random.choice(self.USER_AGENTS)

        logger.debug(f"Selected user-agent: {ua[:50]}...")
        return ua

    def add_user_agent(self, user_agent: str):
        """
        Add custom user-agent to pool

        Args:
            user_agent: User-Agent string to add
        """
        if user_agent not in self.USER_AGENTS:
            self.USER_AGENTS.append(user_agent)
            logger.info(f"Added custom user-agent: {user_agent[:50]}...")


class HeaderGenerator:
    """
    Generate realistic HTTP headers

    Creates browser-like headers to avoid detection
    """

    def __init__(self, user_agent_manager: Optional[UserAgentManager] = None):
        """
        Initialize header generator

        Args:
            user_agent_manager: UserAgentManager instance
        """
        self.user_agent_manager = user_agent_manager or UserAgentManager()

    def generate(
        self,
        url: str,
        custom_headers: Optional[Dict[str, str]] = None
    ) -> Dict[str, str]:
        """
        Generate realistic headers for request

        Args:
            url: Target URL
            custom_headers: Custom headers to merge

        Returns:
            Dictionary of headers
        """
        headers = {
            'User-Agent': self.user_agent_manager.get(),
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.9',
            'Accept-Encoding': 'gzip, deflate, br',
            'DNT': '1',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'none',
            'Cache-Control': 'max-age=0',
        }

        # Add referer for navigation
        if custom_headers and 'Referer' not in custom_headers:
            from urllib.parse import urlparse
            parsed = urlparse(url)
            headers['Referer'] = f"{parsed.scheme}://{parsed.netloc}/"

        # Merge custom headers (override defaults)
        if custom_headers:
            headers.update(custom_headers)

        return headers
