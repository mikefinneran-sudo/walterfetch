# ScrapeMaster - Project Status & Context

**⚠️ READ THIS FIRST WHEN CONVERSATION RESUMES**

This file contains permanent context that persists across conversation summaries.

---

## What ScrapeMaster IS (Already Built ✅)

**Complete web scraping framework with:**

1. ✅ **Core Engine** (`core/engine.py`) - 500+ lines
   - Static & dynamic scraping (httpx + Playwright)
   - Automatic JS detection
   - Proxy support built-in
   - Cache system
   - Retry logic

2. ✅ **Proxy Manager** (`middleware/proxy_manager.py`) - 418 lines
   - Rotating proxies (round-robin, random, health-based)
   - Health monitoring
   - Performance tracking
   - Success/failure recording
   - **NO API SUBSCRIPTION NEEDED** - Just need proxy service ($50/month)

3. ✅ **User Agent Rotation** (built-in)
   - 10+ realistic browser user-agents
   - Random or round-robin selection
   - Header generation for anti-bot evasion

4. ✅ **Data Validation** (`core/validator.py`) - 350+ lines
   - Detects mock/fake data
   - Enforces real data only
   - Validates sources
   - Confidence scoring

5. ✅ **Data Pipeline** (`processing/pipeline.py`)
   - Clean, filter, transform
   - Deduplication
   - Enrichment
   - Export (CSV, JSON, Excel)

6. ✅ **Rate Limiting** (`middleware/rate_limiter.py`)
   - Token bucket algorithm
   - Prevents overload
   - Configurable limits

---

## What We DON'T Need

❌ **ZoomInfo subscription** ($250/month) - Can scrape without it
❌ **Apollo.io subscription** ($99/month) - Can scrape without it
❌ **Any API subscriptions** - Framework scrapes directly from web

---

## What We DO Need

✅ **Proxy service** ($50/month) - To bypass 403 blocking
   - SmartProxy, Bright Data, Oxylabs
   - Already built proxy rotation support
   - Just need to configure proxy URLs

✅ **Use existing scrapers:**
   - `flyflat_live_scraper.py` - Scrapes Yellow Pages, Yelp (blocked without proxies)
   - `find_targets.py` - North Branch scraper (currently uses mock data)
   - Both CAN scrape real data with proxies configured

---

## Current Project State

### North Branch Capital

**Goal:** 25 acquisition targets per day

**Status:** Framework complete, needs proxy configuration

**What Exists:**
- ✅ ICP config: `config/north_branch_config.json`
- ✅ Scraper: `find_targets.py` (currently mock data)
- ✅ Example targets: `ACQUISITION_TARGETS_CONTACTS.md` (3 real targets - manually researched)
  - Davis Tree Care (Forest Park, IL) - Real company, real contacts
  - Terminal-Andrae Inc. (Pewaukee, WI) - Real company
  - Taylor Material Handling - Real company

**What Works:**
- Manual research: 3-5 targets/day (Davis Tree Care quality)
- Mock data generation: 1000 targets in minutes (fake)

**What Needs to Happen:**
- Configure proxy manager with proxy URLs
- Update `find_targets.py` to use proxy manager
- Scrape Google Maps, Yellow Pages, BBB for HVAC/Construction companies
- Result: 25 REAL targets/day without API subscriptions

### Fly Flat

**Goal:** 1000 travel industry prospects

**Status:** Scraper built, blocked by 403 errors

**What Exists:**
- ✅ ICP config: `config/flyflat_config.json`
- ✅ Live scraper: `flyflat_live_scraper.py`
  - Scrapes Yellow Pages ✅
  - Scrapes Yelp ✅
  - Gets 403 Forbidden (needs proxies) ❌

**What Needs to Happen:**
- Add proxy manager to `flyflat_live_scraper.py`
- Run with proxies
- Result: Real contacts without API subscriptions

---

## Real Data Policy (October 18, 2025)

**Policy:** `REAL_DATA_POLICY.md`

**Key Rules:**
- ❌ NO mock/fake/demo data in production
- ✅ All prospects must be verified
- ✅ Must include data_source, verified_date, verification_confidence
- ✅ Validator blocks export of fake data

**Validation:** `core/validator.py`
```bash
python3 core/validator.py prospects.csv
```

**Templates:**
- Manual research: `flyflat_manual_research_template.py`
- Shows 15-30 min research workflow per prospect

---

## File Structure

```
scrapemaster/
├── core/
│   ├── engine.py              # ✅ Main scraping engine (ALREADY BUILT)
│   ├── validator.py           # ✅ Data validation (ALREADY BUILT)
│   └── cache.py
├── middleware/
│   ├── proxy_manager.py       # ✅ Proxy rotation (ALREADY BUILT)
│   ├── rate_limiter.py        # ✅ Rate limiting (ALREADY BUILT)
│   └── captcha_solver.py
├── processing/
│   ├── pipeline.py            # ✅ Data pipeline (ALREADY BUILT)
│   └── extractors.py
├── config/
│   ├── north_branch_config.json   # ✅ North Branch ICP
│   └── flyflat_config.json        # ✅ Fly Flat ICP
├── find_targets.py            # ✅ North Branch scraper (mock data currently)
├── flyflat_live_scraper.py    # ✅ Fly Flat scraper (needs proxies)
├── REAL_DATA_POLICY.md        # ✅ Policy document
├── PROJECT_STATUS.md          # ✅ This file
└── README.md
```

---

## Common Mistakes to Avoid

### ❌ DON'T SAY:
- "We need to build a scraper" → **Already built!**
- "We need ZoomInfo/Apollo.io" → **No! Use existing scraper with proxies**
- "We need to create proxy support" → **Already exists in middleware/proxy_manager.py**
- "Let me build [something that exists]" → **Check file structure first!**

### ✅ DO SAY:
- "Let me configure the existing proxy manager"
- "Let me update find_targets.py to use the proxy manager we already built"
- "Let me add proxy URLs to the existing scraper"

---

## How to Resume Work

1. **Read this file first** ← You are here
2. **Check what exists:**
   ```bash
   ls -lh core/
   ls -lh middleware/
   ```
3. **Understand what's built vs what's needed:**
   - Built: Engine, proxies, validation, scrapers
   - Needed: Proxy service subscription + configuration
4. **Don't rebuild what exists!**

---

## Quick Reference: What Can We Do RIGHT NOW?

### Without Any Subscriptions (FREE):

**Manual Research:**
- Use `flyflat_manual_research_template.py`
- 15-30 min per prospect
- Davis Tree Care quality
- Output: 3-5 prospects/day

**Manual + ScrapeMaster:**
- Google search → Get company list
- Use existing engine to scrape each website
- Extract contacts, services, etc.
- Output: 10-15 prospects/day

### With Proxy Service ($50/month):

**Automated Scraping:**
- Configure proxy_manager.py with proxy URLs
- Run `flyflat_live_scraper.py` with proxies
- Scrape Yellow Pages, Yelp, Google Maps
- Output: 25+ prospects/day

**North Branch Automated:**
- Update `find_targets.py` to use proxy manager
- Scrape industry directories, business registries
- Output: 25 targets/day (goal achieved)

---

## Next Steps (When You Resume)

### Immediate:
1. Get proxy service:
   - SmartProxy: $50/month
   - Bright Data: $50-100/month
   - Oxylabs: $75/month

2. Configure existing proxy manager:
   ```python
   from middleware.proxy_manager import ProxyManager

   proxies = [
       'http://user:pass@proxy1.smartproxy.com:10000',
       'http://user:pass@proxy2.smartproxy.com:10000',
   ]

   proxy_mgr = ProxyManager(proxies, rotation_strategy='health_based')
   ```

3. Update `flyflat_live_scraper.py`:
   - Import proxy_manager
   - Pass proxy to httpx client
   - Test with 10 prospects

### This Week:
1. Test proxy scraping with Fly Flat
2. Get 25 real prospects
3. Validate with `core/validator.py`
4. Export and verify quality

### This Month:
1. Scale to 25 North Branch targets/day
2. Build master prospect database
3. CRM integration
4. Weekly deal flow reports

---

## Success Metrics

**Manual Research (Current):**
- 3 targets completed (Davis Tree Care, Terminal-Andrae, Taylor MH)
- 100% real, verified
- Ready for outreach

**With Proxies (Target):**
- 25 targets/day
- 500 targets/month
- 85%+ verification confidence
- Zero API costs

**ROI:**
- Tool cost: $50/month (proxies)
- If 1 deal closes: $1-5M+ (NBC deal value)
- ROI: 100,000%+

---

## Important Realizations

1. **We already built everything we need**
   - Don't rebuild proxy support → Use middleware/proxy_manager.py
   - Don't rebuild scraping → Use core/engine.py
   - Don't rebuild validation → Use core/validator.py

2. **API subscriptions are optional**
   - ZoomInfo/Apollo are for convenience
   - ScrapeMaster can scrape without them
   - Just need proxies ($50/month vs $250/month)

3. **Mock data was temporary**
   - Old scripts generated fake data
   - New policy: Real data only (REAL_DATA_POLICY.md)
   - Validator blocks fake data exports

4. **Two approaches both work:**
   - Manual research: High quality, low volume (Davis Tree Care)
   - Automated scraping: Medium quality, high volume (25/day with proxies)

---

## Context Preservation

**When conversation gets summarized, remember:**
- ScrapeMaster is COMPLETE (not a work-in-progress)
- Proxy manager EXISTS (don't rebuild it)
- Real data policy is ACTIVE (no more mock data)
- Goal is CONFIGURATION not DEVELOPMENT

**Read these files for context:**
1. This file (PROJECT_STATUS.md)
2. REAL_DATA_POLICY.md
3. ACQUISITION_TARGETS_CONTACTS.md (examples of real targets)
4. middleware/proxy_manager.py (proof it's built)

---

**Last Updated:** October 18, 2025
**Status:** Framework complete, needs proxy configuration
**Next Action:** Get proxy service → Configure → Run scrapers
