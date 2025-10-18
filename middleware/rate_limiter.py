"""
Rate Limiting and Retry Logic
Implements token bucket algorithm and exponential backoff
"""

import asyncio
import time
import random
import logging
from typing import Optional, List
from dataclasses import dataclass
from collections import deque
import httpx

logger = logging.getLogger(__name__)


@dataclass
class RetryConfig:
    """Configuration for retry logic"""
    max_retries: int = 3
    base_delay: float = 1.0  # seconds
    max_delay: float = 60.0  # seconds
    exponential_base: float = 2.0
    jitter: bool = True
    retry_on_status: List[int] = None  # HTTP status codes to retry on

    def __post_init__(self):
        if self.retry_on_status is None:
            self.retry_on_status = [429, 500, 502, 503, 504]


class RateLimiter:
    """
    Token bucket rate limiter for controlling request rates

    Allows burst requests up to bucket capacity while maintaining
    average rate over time.

    Example:
        limiter = RateLimiter(requests_per_second=2, burst=5)
        async with limiter:
            # Make request
            pass
    """

    def __init__(
        self,
        requests_per_second: float = 1.0,
        burst: int = 1
    ):
        """
        Initialize rate limiter

        Args:
            requests_per_second: Average requests per second allowed
            burst: Maximum burst size (tokens in bucket)
        """
        self.rate = requests_per_second
        self.burst = burst
        self.tokens = float(burst)
        self.last_update = time.time()
        self._lock = asyncio.Lock()

        logger.info(f"RateLimiter initialized: {requests_per_second} req/s, burst={burst}")

    async def acquire(self, tokens: int = 1):
        """
        Acquire tokens, waiting if necessary

        Args:
            tokens: Number of tokens to acquire
        """
        async with self._lock:
            while True:
                now = time.time()
                elapsed = now - self.last_update

                # Add new tokens based on elapsed time
                self.tokens = min(
                    self.burst,
                    self.tokens + elapsed * self.rate
                )
                self.last_update = now

                if self.tokens >= tokens:
                    self.tokens -= tokens
                    logger.debug(f"Token acquired. Remaining: {self.tokens:.2f}")
                    return

                # Calculate wait time
                wait_time = (tokens - self.tokens) / self.rate
                logger.debug(f"Rate limit reached. Waiting {wait_time:.2f}s")
                await asyncio.sleep(wait_time)

    async def __aenter__(self):
        """Context manager support"""
        await self.acquire()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Context manager support"""
        pass


class DomainRateLimiter:
    """
    Per-domain rate limiting

    Maintains separate rate limiters for each domain to avoid
    overwhelming any single server.
    """

    def __init__(
        self,
        requests_per_second: float = 1.0,
        burst: int = 1
    ):
        self.rate = requests_per_second
        self.burst = burst
        self._limiters = {}
        self._lock = asyncio.Lock()

    async def acquire(self, domain: str):
        """
        Acquire token for specific domain

        Args:
            domain: Domain name to rate limit
        """
        async with self._lock:
            if domain not in self._limiters:
                self._limiters[domain] = RateLimiter(self.rate, self.burst)
                logger.info(f"Created rate limiter for domain: {domain}")

        await self._limiters[domain].acquire()

    def get_stats(self):
        """Get statistics for all domains"""
        return {
            domain: {
                'tokens': limiter.tokens,
                'rate': limiter.rate,
                'burst': limiter.burst
            }
            for domain, limiter in self._limiters.items()
        }


class RetryHandler:
    """
    Retry logic with exponential backoff and jitter

    Implements the best practices for retry logic:
    - Exponential backoff to avoid overwhelming servers
    - Jitter to prevent thundering herd
    - Configurable retry conditions
    """

    def __init__(self, config: Optional[RetryConfig] = None):
        """
        Initialize retry handler

        Args:
            config: Retry configuration
        """
        self.config = config or RetryConfig()
        logger.info(f"RetryHandler initialized: max_retries={self.config.max_retries}")

    async def execute(self, func, *args, **kwargs):
        """
        Execute function with retry logic

        Args:
            func: Async function to execute
            *args, **kwargs: Arguments to pass to function

        Returns:
            Function result

        Raises:
            Last exception if all retries exhausted
        """
        last_exception = None

        for attempt in range(self.config.max_retries + 1):
            try:
                result = await func(*args, **kwargs)

                # Check if response indicates we should retry
                if hasattr(result, 'status_code'):
                    if result.status_code in self.config.retry_on_status:
                        raise httpx.HTTPStatusError(
                            f"Status {result.status_code}",
                            request=None,
                            response=result
                        )

                # Success
                if attempt > 0:
                    logger.info(f"Request succeeded on attempt {attempt + 1}")
                return result

            except Exception as e:
                last_exception = e

                if attempt == self.config.max_retries:
                    logger.error(f"All {self.config.max_retries} retries exhausted")
                    raise

                # Calculate backoff delay
                delay = self._calculate_delay(attempt)

                logger.warning(
                    f"Attempt {attempt + 1} failed: {str(e)}. "
                    f"Retrying in {delay:.2f}s..."
                )

                await asyncio.sleep(delay)

        raise last_exception

    def _calculate_delay(self, attempt: int) -> float:
        """
        Calculate delay for given attempt using exponential backoff

        Args:
            attempt: Current attempt number (0-indexed)

        Returns:
            Delay in seconds
        """
        # Exponential backoff: base_delay * (exponential_base ^ attempt)
        delay = min(
            self.config.base_delay * (self.config.exponential_base ** attempt),
            self.config.max_delay
        )

        # Add jitter to prevent thundering herd
        if self.config.jitter:
            jitter = random.uniform(0, delay * 0.1)  # Up to 10% jitter
            delay += jitter

        return delay


class CircuitBreaker:
    """
    Circuit breaker pattern for failing services

    Prevents cascading failures by stopping requests to failing services
    after a threshold is reached.

    States:
    - CLOSED: Normal operation, requests pass through
    - OPEN: Too many failures, requests blocked
    - HALF_OPEN: Testing if service recovered
    """

    CLOSED = 'closed'
    OPEN = 'open'
    HALF_OPEN = 'half_open'

    def __init__(
        self,
        failure_threshold: int = 5,
        recovery_timeout: float = 60.0,
        expected_exception = Exception
    ):
        """
        Initialize circuit breaker

        Args:
            failure_threshold: Number of failures before opening circuit
            recovery_timeout: Seconds to wait before attempting recovery
            expected_exception: Exception types that count as failures
        """
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.expected_exception = expected_exception

        self._state = self.CLOSED
        self._failure_count = 0
        self._last_failure_time = None
        self._success_count = 0
        self._lock = asyncio.Lock()

        logger.info(
            f"CircuitBreaker initialized: "
            f"threshold={failure_threshold}, timeout={recovery_timeout}s"
        )

    async def call(self, func, *args, **kwargs):
        """
        Execute function with circuit breaker protection

        Args:
            func: Async function to execute
            *args, **kwargs: Arguments to pass to function

        Returns:
            Function result

        Raises:
            CircuitBreakerError if circuit is open
        """
        async with self._lock:
            if self._state == self.OPEN:
                if self._should_attempt_reset():
                    self._state = self.HALF_OPEN
                    logger.info("Circuit breaker entering HALF_OPEN state")
                else:
                    raise CircuitBreakerError("Circuit breaker is OPEN")

        try:
            result = await func(*args, **kwargs)
            await self._on_success()
            return result

        except self.expected_exception as e:
            await self._on_failure()
            raise

    async def _on_success(self):
        """Handle successful request"""
        async with self._lock:
            self._failure_count = 0

            if self._state == self.HALF_OPEN:
                self._success_count += 1
                if self._success_count >= 2:  # Require 2 successes to close
                    self._state = self.CLOSED
                    self._success_count = 0
                    logger.info("Circuit breaker reset to CLOSED state")

    async def _on_failure(self):
        """Handle failed request"""
        async with self._lock:
            self._failure_count += 1
            self._last_failure_time = time.time()

            if self._state == self.HALF_OPEN:
                self._state = self.OPEN
                logger.warning("Circuit breaker reopened")

            elif self._failure_count >= self.failure_threshold:
                self._state = self.OPEN
                logger.error(
                    f"Circuit breaker opened after {self._failure_count} failures"
                )

    def _should_attempt_reset(self) -> bool:
        """Check if enough time has passed to attempt recovery"""
        return (
            self._last_failure_time is not None and
            time.time() - self._last_failure_time >= self.recovery_timeout
        )

    @property
    def state(self) -> str:
        """Get current circuit breaker state"""
        return self._state


class CircuitBreakerError(Exception):
    """Raised when circuit breaker is open"""
    pass


class AdaptiveRateLimiter:
    """
    Adaptive rate limiter that adjusts rate based on server responses

    Automatically slows down when receiving rate limit errors (429)
    and speeds up when requests succeed.
    """

    def __init__(
        self,
        initial_rate: float = 1.0,
        min_rate: float = 0.1,
        max_rate: float = 10.0,
        adjustment_factor: float = 0.5
    ):
        """
        Initialize adaptive rate limiter

        Args:
            initial_rate: Starting requests per second
            min_rate: Minimum allowed rate
            max_rate: Maximum allowed rate
            adjustment_factor: Multiplier for rate adjustments
        """
        self.current_rate = initial_rate
        self.min_rate = min_rate
        self.max_rate = max_rate
        self.adjustment_factor = adjustment_factor

        self._limiter = RateLimiter(initial_rate)
        self._lock = asyncio.Lock()

        logger.info(f"AdaptiveRateLimiter initialized: rate={initial_rate} req/s")

    async def acquire(self):
        """Acquire token at current rate"""
        await self._limiter.acquire()

    async def on_success(self):
        """Increase rate on successful request"""
        async with self._lock:
            old_rate = self.current_rate
            self.current_rate = min(
                self.max_rate,
                self.current_rate * (1 + self.adjustment_factor * 0.1)
            )

            if self.current_rate != old_rate:
                self._limiter = RateLimiter(self.current_rate)
                logger.info(f"Rate increased: {old_rate:.2f} -> {self.current_rate:.2f} req/s")

    async def on_rate_limit(self):
        """Decrease rate when rate limited"""
        async with self._lock:
            old_rate = self.current_rate
            self.current_rate = max(
                self.min_rate,
                self.current_rate * (1 - self.adjustment_factor)
            )

            self._limiter = RateLimiter(self.current_rate)
            logger.warning(f"Rate decreased: {old_rate:.2f} -> {self.current_rate:.2f} req/s")

    async def on_error(self):
        """Decrease rate on error"""
        await self.on_rate_limit()
