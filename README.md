# ScrapeMaster

**Web scraping framework with proxy rotation, real data validation, and zero API dependencies**

---

## What Is This?

ScrapeMaster is a complete web scraping framework that can extract real business data from public sources **without expensive API subscriptions**.

**Instead of paying $250/month for ZoomInfo or Apollo.io**, use ScrapeMaster with a $50/month proxy service to scrape:
- Google Maps
- Yellow Pages
- Yelp
- Industry directories
- Company websites
- Secretary of State registries

## Key Features

✅ **Complete Scraping Engine**
- Static & dynamic scraping (httpx + Playwright)
- Automatic JavaScript detection
- Smart caching with TTL

✅ **Enterprise Proxy Support**
- Built-in proxy rotation (round-robin, random, health-based)
- Automatic health monitoring
- Performance tracking
- No proxy service needed for testing, add when scaling

✅ **Real Data Validation**
- Detects and blocks mock/fake data
- Enforces verification requirements
- Confidence scoring
- Source documentation

✅ **Production Ready**
- Rate limiting
- Retry logic with exponential backoff
- Concurrent request handling
- Export to CSV/JSON/Excel

## Quick Start

```bash
# Clone the repo
git clone https://github.com/mikefinneran-sudo/scrapemaster.git
cd scrapemaster

# Install dependencies
pip3 install httpx playwright beautifulsoup4 lxml pandas

# Install browser for dynamic scraping
python3 -m playwright install chromium

# Read the status (IMPORTANT - start here!)
cat PROJECT_STATUS.md
```

## What's Already Built

**Read `PROJECT_STATUS.md` first!** It contains:
- Complete inventory of what exists
- What's built vs what's needed
- How to avoid rebuilding existing components
- Next steps for configuration

**Core Components:**
- `core/engine.py` - Main scraping engine
- `middleware/proxy_manager.py` - Proxy rotation system
- `core/validator.py` - Real data validation
- `processing/pipeline.py` - Data processing
- `middleware/rate_limiter.py` - Rate limiting

## Usage Examples

### Example 1: Scrape Without Proxies (Testing)

```python
from core.engine import ScraperEngine, ScrapeOptions

engine = ScraperEngine()

# Scrape a company website
result = await engine.scrape(
    url="https://example-company.com",
    selectors={
        'company_name': 'h1.company-name',
        'phone': '[href^="tel:"]',
        'email': '[href^="mailto:"]'
    }
)

print(result.data)
```

### Example 2: Scrape With Proxies (Production)

```python
from core.engine import ScraperEngine
from middleware.proxy_manager import ProxyManager

# Configure proxies
proxy_mgr = ProxyManager(
    proxies=[
        'http://user:pass@proxy1.provider.com:10000',
        'http://user:pass@proxy2.provider.com:10000',
    ],
    rotation_strategy='health_based'
)

# Create engine with proxy support
engine = ScraperEngine(proxy_manager=proxy_mgr)

# Scrape with automatic proxy rotation
result = await engine.scrape(url, selectors)
```

### Example 3: Validate Data Quality

```python
from core.validator import RealDataValidator

validator = RealDataValidator(strict_mode=True)

prospects = [
    {
        'company_name': 'Real Company Inc',
        'website': 'https://realcompany.com',
        'verified_website': True,
        'data_source': 'Manual Research',
        'verification_confidence': 95
    }
]

results = validator.validate_dataset(prospects)
validator.print_validation_report(results)
```

## Real Data Policy

**ScrapeMaster enforces real, verified data only.**

See `REAL_DATA_POLICY.md` for complete requirements.

**Key rules:**
- ❌ NO mock/fake/demo data in production
- ✅ All prospects must be verified
- ✅ Must include data_source and verification_confidence
- ✅ Validator blocks export of fake data

## Use Cases

### North Branch Capital (Example)

**Goal:** Find 25 acquisition targets per day

**Approach:**
1. Configure proxy manager with proxy service
2. Scrape Google Maps for HVAC/Construction companies in Midwest
3. Enrich with company websites
4. Validate and export

**Result:** 500 real targets/month for $50/month (vs $250/month for ZoomInfo)

### Fly Flat Travel (Example)

**Goal:** 1000 travel industry prospects

**Approach:**
1. Scrape Yellow Pages and Yelp for finance/tech companies
2. Filter by employee count and location
3. Find decision makers (CFO, Travel Manager)
4. Export to CRM

**Result:** Real contact data without API subscriptions

## Cost Comparison

| Approach | Cost/Month | Targets/Month | Quality |
|----------|------------|---------------|---------|
| **ScrapeMaster + Proxies** | $50 | 500+ | 85-95% |
| ZoomInfo | $250 | 500+ | 90% |
| Apollo.io | $99 | 500+ | 85% |
| Manual Research | $0 | 100 | 95% |

**Why ScrapeMaster:**
- 80% cheaper than ZoomInfo
- 50% cheaper than Apollo.io
- 5x faster than manual research
- You own the data forever

## File Structure

```
scrapemaster/
├── core/
│   ├── engine.py              # Main scraping engine
│   ├── validator.py           # Data validation
│   └── cache.py              # Response caching
├── middleware/
│   ├── proxy_manager.py      # Proxy rotation
│   ├── rate_limiter.py       # Rate limiting
│   └── captcha_solver.py     # CAPTCHA handling
├── processing/
│   ├── pipeline.py           # Data pipeline
│   └── extractors.py         # Data extraction
├── config/
│   ├── north_branch_config.json  # Example: North Branch ICP
│   └── flyflat_config.json       # Example: Fly Flat ICP
├── PROJECT_STATUS.md         # **READ THIS FIRST**
├── REAL_DATA_POLICY.md       # Data quality policy
└── README.md                 # This file
```

## Documentation

**Start here:**
1. `PROJECT_STATUS.md` - Current state, what's built, next steps
2. `REAL_DATA_POLICY.md` - Data quality requirements
3. `ACQUISITION_TARGETS_CONTACTS.md` - Example real targets

**Examples:**
- `find_targets.py` - North Branch acquisition scraper
- `flyflat_live_scraper.py` - Travel industry scraper
- `flyflat_manual_research_template.py` - Manual research workflow

## Next Steps

### Without Proxies (Free)

**Manual research:**
```bash
python3 flyflat_manual_research_template.py
```

Follow the guide to manually research 3-5 prospects/day.

### With Proxies ($50/month)

1. **Get proxy service:**
   - SmartProxy: $50/month
   - Bright Data: $50-100/month
   - Oxylabs: $75/month

2. **Configure ScrapeMaster:**
   ```python
   proxy_mgr = ProxyManager(proxies=['http://...'])
   ```

3. **Run scraper:**
   ```bash
   python3 find_targets.py --proxies
   ```

4. **Result:** 25+ targets/day

## Contributing

This is a personal project, but feel free to fork and adapt for your needs.

## License

MIT License - Use freely for commercial or personal projects.

## Support

Questions? Read the docs:
- `PROJECT_STATUS.md` - Project state and context
- `REAL_DATA_POLICY.md` - Data quality standards

## Why This Exists

**Problem:** ZoomInfo ($250/month) and Apollo.io ($99/month) are expensive for small businesses and individual entrepreneurs.

**Solution:** ScrapeMaster scrapes the same public data these APIs use, but directly from the source for just the cost of proxies ($50/month).

**Built for:**
- Private equity firms sourcing acquisition targets
- Sales teams building prospect lists
- Entrepreneurs validating business ideas
- Anyone who needs real B2B contact data

---

**Read `PROJECT_STATUS.md` to get started!**
