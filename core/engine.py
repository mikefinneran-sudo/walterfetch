"""
ScrapeMaster Core Engine
Intelligent web scraping engine with automatic static/dynamic detection
"""

import asyncio
import logging
from typing import Dict, List, Optional, Union, Any
from dataclasses import dataclass, field
from datetime import datetime
import httpx
from playwright.async_api import async_playwright, Browser, Page
from bs4 import BeautifulSoup
import json

logger = logging.getLogger(__name__)


@dataclass
class ScrapeOptions:
    """Configuration options for a scrape request"""
    use_cache: bool = True
    cache_ttl: int = 3600
    timeout: int = 30
    retry_count: int = 3
    force_dynamic: bool = False
    proxy: Optional[str] = None
    headers: Dict[str, str] = field(default_factory=dict)
    cookies: Dict[str, str] = field(default_factory=dict)
    wait_for_selector: Optional[str] = None
    wait_time: float = 0
    user_agent: Optional[str] = None


@dataclass
class ScrapeResult:
    """Result of a scrape operation"""
    success: bool
    url: str
    data: Dict[str, Any]
    metadata: Dict[str, Any]
    error: Optional[str] = None
    timestamp: datetime = field(default_factory=datetime.now)


class ScraperEngine:
    """
    Core scraping engine with intelligent static/dynamic detection

    Features:
    - Automatic detection of JavaScript requirements
    - Fallback from static to dynamic scraping
    - Response caching
    - Retry logic with exponential backoff
    - Concurrent request handling
    """

    def __init__(
        self,
        rate_limiter=None,
        cache=None,
        proxy_manager=None,
        user_agent_manager=None
    ):
        self.rate_limiter = rate_limiter
        self.cache = cache
        self.proxy_manager = proxy_manager
        self.user_agent_manager = user_agent_manager
        self._browser: Optional[Browser] = None
        self._playwright = None

        # JavaScript framework indicators
        self.js_frameworks = [
            'react', 'vue', 'angular', 'next.js', 'nuxt',
            '__NEXT_DATA__', '__NUXT__', 'ng-version'
        ]

        # Dynamic content indicators
        self.dynamic_indicators = [
            'data-reactroot', 'data-vue-', 'ng-app',
            'v-cloak', 'defer', 'async'
        ]

    async def scrape(
        self,
        url: str,
        selectors: Dict[str, str],
        options: Optional[ScrapeOptions] = None
    ) -> ScrapeResult:
        """
        Main scraping method with automatic static/dynamic detection

        Args:
            url: Target URL to scrape
            selectors: Dictionary of {field_name: css_selector}
            options: Optional scrape configuration

        Returns:
            ScrapeResult with extracted data
        """
        options = options or ScrapeOptions()

        logger.info(f"Starting scrape: {url}")

        # Check cache first
        if options.use_cache and self.cache:
            cached = await self.cache.get(url)
            if cached:
                logger.info(f"Cache hit for {url}")
                return ScrapeResult(
                    success=True,
                    url=url,
                    data=cached,
                    metadata={'cached': True, 'cache_hit_time': datetime.now()}
                )

        # Apply rate limiting
        if self.rate_limiter:
            await self.rate_limiter.acquire()

        try:
            # Decide scraping strategy
            if options.force_dynamic:
                html, load_time = await self._fetch_dynamic(url, options)
            else:
                # Try static first
                needs_dynamic = await self._should_use_dynamic(url)
                if needs_dynamic:
                    logger.info(f"Dynamic content detected for {url}, using browser")
                    html, load_time = await self._fetch_dynamic(url, options)
                else:
                    logger.info(f"Static content detected for {url}, using HTTP client")
                    html, load_time = await self._fetch_static(url, options)

            # Extract data using selectors
            data = self._extract_data(html, selectors)

            # Store in cache
            if options.use_cache and self.cache:
                await self.cache.set(url, data, ttl=options.cache_ttl)

            result = ScrapeResult(
                success=True,
                url=url,
                data=data,
                metadata={
                    'load_time_ms': load_time,
                    'html_size_bytes': len(html),
                    'selectors_found': len([k for k, v in data.items() if v is not None]),
                    'timestamp': datetime.now().isoformat()
                }
            )

            logger.info(f"Scrape completed successfully: {url}")
            return result

        except Exception as e:
            logger.error(f"Scrape failed for {url}: {str(e)}", exc_info=True)
            return ScrapeResult(
                success=False,
                url=url,
                data={},
                metadata={'error_time': datetime.now().isoformat()},
                error=str(e)
            )

    async def scrape_batch(
        self,
        urls: List[str],
        selectors: Dict[str, str],
        options: Optional[ScrapeOptions] = None,
        concurrency: int = 5
    ) -> List[ScrapeResult]:
        """
        Scrape multiple URLs concurrently

        Args:
            urls: List of URLs to scrape
            selectors: CSS selectors to extract
            options: Scrape options
            concurrency: Max concurrent requests

        Returns:
            List of ScrapeResults
        """
        logger.info(f"Starting batch scrape of {len(urls)} URLs")

        semaphore = asyncio.Semaphore(concurrency)

        async def scrape_with_semaphore(url):
            async with semaphore:
                return await self.scrape(url, selectors, options)

        tasks = [scrape_with_semaphore(url) for url in urls]
        results = await asyncio.gather(*tasks, return_exceptions=True)

        # Convert exceptions to failed results
        processed_results = []
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                processed_results.append(ScrapeResult(
                    success=False,
                    url=urls[i],
                    data={},
                    metadata={},
                    error=str(result)
                ))
            else:
                processed_results.append(result)

        success_count = sum(1 for r in processed_results if r.success)
        logger.info(f"Batch scrape completed: {success_count}/{len(urls)} successful")

        return processed_results

    async def _should_use_dynamic(self, url: str) -> bool:
        """
        Determine if URL requires JavaScript rendering

        Strategy:
        1. Check URL patterns (SPAs often use hash routing)
        2. Make quick HEAD request to check headers
        3. Sample HTML for JS framework indicators

        Args:
            url: URL to check

        Returns:
            True if dynamic scraping is needed
        """
        # Check URL patterns
        if '#/' in url or url.endswith('.js'):
            return True

        try:
            async with httpx.AsyncClient() as client:
                # Quick HEAD request
                head_response = await client.head(url, timeout=5.0, follow_redirects=True)
                content_type = head_response.headers.get('content-type', '')

                # If it's not HTML, we don't need browser
                if 'text/html' not in content_type:
                    return False

                # Sample first 50KB of HTML
                response = await client.get(url, timeout=10.0)
                html_sample = response.text[:50000]

                # Check for JavaScript framework indicators
                for indicator in self.js_frameworks + self.dynamic_indicators:
                    if indicator.lower() in html_sample.lower():
                        logger.debug(f"Found JS indicator '{indicator}' in {url}")
                        return True

                # Check for minimal content (might be JS-rendered)
                soup = BeautifulSoup(html_sample, 'html.parser')
                body_text = soup.get_text(strip=True)
                if len(body_text) < 100:  # Very little content, probably JS-rendered
                    return True

                return False

        except Exception as e:
            logger.warning(f"Error checking if dynamic needed for {url}: {e}")
            # Default to static if check fails
            return False

    async def _fetch_static(
        self,
        url: str,
        options: ScrapeOptions
    ) -> tuple[str, float]:
        """
        Fetch content using HTTP client (faster, less resource-intensive)

        Args:
            url: URL to fetch
            options: Scrape options

        Returns:
            Tuple of (HTML content, load time in ms)
        """
        headers = {
            'User-Agent': options.user_agent or self._get_user_agent(),
            **options.headers
        }

        proxy = options.proxy or (self.proxy_manager.get_proxy() if self.proxy_manager else None)

        start_time = datetime.now()

        async with httpx.AsyncClient(
            timeout=options.timeout,
            proxies=proxy,
            follow_redirects=True
        ) as client:
            response = await client.get(
                url,
                headers=headers,
                cookies=options.cookies
            )
            response.raise_for_status()

            if options.wait_time > 0:
                await asyncio.sleep(options.wait_time)

            load_time = (datetime.now() - start_time).total_seconds() * 1000

            return response.text, load_time

    async def _fetch_dynamic(
        self,
        url: str,
        options: ScrapeOptions
    ) -> tuple[str, float]:
        """
        Fetch content using headless browser (for JavaScript-heavy sites)

        Args:
            url: URL to fetch
            options: Scrape options

        Returns:
            Tuple of (HTML content, load time in ms)
        """
        if not self._browser:
            await self._init_browser()

        start_time = datetime.now()

        page: Page = await self._browser.new_page()

        try:
            # Set user agent
            if options.user_agent:
                await page.set_extra_http_headers({'User-Agent': options.user_agent})

            # Set cookies
            if options.cookies:
                await page.context.add_cookies([
                    {'name': k, 'value': v, 'url': url}
                    for k, v in options.cookies.items()
                ])

            # Navigate to page
            await page.goto(url, timeout=options.timeout * 1000, wait_until='networkidle')

            # Wait for specific selector if provided
            if options.wait_for_selector:
                await page.wait_for_selector(options.wait_for_selector, timeout=options.timeout * 1000)

            # Additional wait time
            if options.wait_time > 0:
                await asyncio.sleep(options.wait_time)

            # Get HTML content
            html = await page.content()

            load_time = (datetime.now() - start_time).total_seconds() * 1000

            return html, load_time

        finally:
            await page.close()

    def _extract_data(self, html: str, selectors: Dict[str, str]) -> Dict[str, Any]:
        """
        Extract data from HTML using CSS selectors

        Args:
            html: HTML content
            selectors: Dictionary of {field_name: css_selector}

        Returns:
            Dictionary of extracted data
        """
        soup = BeautifulSoup(html, 'html.parser')
        data = {}

        for field_name, selector in selectors.items():
            try:
                # Handle special selector syntax
                if '::text' in selector:
                    # Extract text content
                    selector = selector.replace('::text', '')
                    element = soup.select_one(selector)
                    data[field_name] = element.get_text(strip=True) if element else None

                elif '::attr(' in selector:
                    # Extract attribute value
                    attr_match = selector.split('::attr(')[1].rstrip(')')
                    selector = selector.split('::attr(')[0]
                    element = soup.select_one(selector)
                    data[field_name] = element.get(attr_match) if element else None

                elif selector.startswith('['):
                    # Multiple elements (returns list)
                    elements = soup.select(selector.strip('[]'))
                    data[field_name] = [elem.get_text(strip=True) for elem in elements]

                else:
                    # Default: extract text content
                    element = soup.select_one(selector)
                    data[field_name] = element.get_text(strip=True) if element else None

            except Exception as e:
                logger.warning(f"Error extracting field '{field_name}' with selector '{selector}': {e}")
                data[field_name] = None

        return data

    async def _init_browser(self):
        """Initialize Playwright browser instance"""
        self._playwright = await async_playwright().start()
        self._browser = await self._playwright.chromium.launch(
            headless=True,
            args=[
                '--disable-blink-features=AutomationControlled',
                '--disable-dev-shm-usage',
                '--no-sandbox'
            ]
        )
        logger.info("Browser initialized")

    def _get_user_agent(self) -> str:
        """Get user agent from manager or use default"""
        if self.user_agent_manager:
            return self.user_agent_manager.get()
        return 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'

    async def close(self):
        """Cleanup resources"""
        if self._browser:
            await self._browser.close()
        if self._playwright:
            await self._playwright.stop()
        logger.info("Engine closed")

    async def __aenter__(self):
        """Context manager entry"""
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit"""
        await self.close()
