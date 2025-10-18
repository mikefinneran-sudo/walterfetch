# ScrapeMaster - REAL DATA ONLY Policy

**Effective Date:** October 18, 2025
**Status:** MANDATORY for all prospect/target generation

---

## Core Principle

**ALL prospect and target data MUST be real, verified, and sourced from actual businesses.**

Mock data, simulated contacts, and generated information are **STRICTLY PROHIBITED** for production use.

---

## What This Means

### ✅ ALLOWED - Real Data Sources

1. **Manual Research & Verification**
   - Google search → Company website verification
   - LinkedIn manual lookup
   - Direct phone verification
   - Business directory cross-reference
   - Website contact form verification

2. **Paid API Services** (Verified Data)
   - Apollo.io ($49-99/month) - 10,000+ verified B2B contacts
   - ZoomInfo (Enterprise) - Most comprehensive
   - LinkedIn Sales Navigator API ($80/month)
   - Google Places API - Business listings with verification
   - Hunter.io - Email verification
   - Clearbit - Company enrichment

3. **Web Scraping** (With Verification)
   - Only if data can be verified through multiple sources
   - Must include manual spot-check of 10% of results
   - Requires anti-bot measures (proxies, CAPTCHA solving)
   - Must respect robots.txt and terms of service

4. **Public Business Registries**
   - Secretary of State business filings
   - BBB (Better Business Bureau) listings
   - Chamber of Commerce directories
   - Industry association member directories

### ❌ PROHIBITED - Mock/Fake Data

1. **Programmatically Generated Data**
   - Random name generation (e.g., "John Smith at Global Capital")
   - Template-based company names (e.g., "Apex Solutions Inc")
   - Fabricated email addresses
   - Fake phone numbers
   - Estimated/guessed revenue numbers

2. **Demo/Placeholder Data**
   - Any data marked "demo", "example", "mock", or "test"
   - Hardcoded company lists in scripts
   - Sample data for demonstrations
   - Placeholder contact information

3. **Unverified Web Scraping**
   - Data scraped but not verified
   - Duplicate/low-quality scraping results
   - Data from blocked/forbidden sources

---

## Implementation Requirements

### For ALL Target/Prospect Finder Scripts

Every script that generates prospect lists MUST:

1. **Display Data Source Warning**
   ```
   ⚠️  DATA SOURCE VERIFICATION

   This script will only provide REAL, VERIFIED prospects.

   Sources:
   - [ ] Manual Research
   - [ ] Paid API (Apollo.io, ZoomInfo, etc.)
   - [ ] Verified Web Scraping
   - [ ] Public Business Registries

   ❌ Mock/demo data is PROHIBITED
   ```

2. **Require Source Documentation**
   - Every prospect must include `data_source` field
   - Every prospect must include `verified_date` field
   - Every prospect must include `verification_method` field

3. **Include Verification Status**
   - `verified_phone`: true/false
   - `verified_email`: true/false
   - `verified_website`: true/false
   - `verification_confidence`: 0-100 score

4. **Manual Verification Prompts**
   - For lists >100 contacts, require manual spot-check
   - Script must pause and show 10 random contacts for verification
   - User must confirm: "Are these real companies? (yes/no)"

### Required Data Fields

Every prospect record MUST include:

```json
{
  "company_name": "Real Company Name",
  "website": "https://realcompany.com",
  "verified_website": true,

  "address": "123 Real Street, City, ST 12345",
  "phone": "(123) 456-7890",
  "verified_phone": true,

  "contact_name": "John Smith",
  "contact_title": "CFO",
  "contact_email": "john.smith@realcompany.com",
  "verified_email": true,

  "data_source": "Apollo.io API",
  "source_url": "https://app.apollo.io/...",
  "verified_date": "2025-10-18",
  "verification_method": "API + Manual Website Check",
  "verification_confidence": 95
}
```

---

## Workflow: Manual Research Protocol

### For High-Value Targets (North Branch Style)

**Time Investment:** 15-30 minutes per target
**Quality Level:** Very High (95%+ accuracy)

#### Step 1: Target Identification (5 min)
1. Google search: "[Industry] companies [Location]"
2. Filter for companies matching ICP criteria
3. Create shortlist of 10-20 potential targets

#### Step 2: Company Verification (5 min per company)
1. Visit company website
2. Verify:
   - Still in business (recent news/updates)
   - Services match ICP
   - Location confirmed
   - Size indicators (team page, facilities)

#### Step 3: Contact Discovery (10 min per company)
1. Find decision maker:
   - LinkedIn manual search
   - "About Us" / "Team" page
   - Press releases
   - Industry directories

2. Verify contact details:
   - Email format from website
   - Phone from website footer
   - LinkedIn profile confirmation

#### Step 4: Enrichment (5 min per company)
1. Gather additional data:
   - Recent news/press releases
   - Financial indicators (if public)
   - Key partnerships/certifications
   - Industry reputation

#### Step 5: Documentation (5 min per company)
1. Create detailed profile (like North Branch doc)
2. Include all verified contacts
3. Write acquisition rationale
4. Draft outreach strategy

**Output:** 3-5 deeply researched targets per day

---

## Workflow: API-Powered Research

### For Higher Volume (Fly Flat Style)

**Time Investment:** 2-5 minutes per target
**Quality Level:** High (85%+ accuracy with verification)

#### Step 1: API Query
```python
# Using Apollo.io as example
import apollo

# Search for targets
results = apollo.search_people({
    'person_titles': ['CFO', 'VP Finance', 'Travel Manager'],
    'organization_locations': ['New York, NY', 'Chicago, IL'],
    'organization_num_employees_ranges': ['50-200', '201-500'],
    'person_seniority': ['manager', 'director', 'vp', 'c_suite']
})
```

#### Step 2: Automated Enrichment
```python
# Enrich with company data
for contact in results:
    company_data = apollo.get_organization(contact.org_id)
    contact.update({
        'revenue': company_data.revenue,
        'employees': company_data.employees,
        'industry': company_data.industry,
        'verified_email': company_data.email_verified,
        'data_source': 'Apollo.io API',
        'verified_date': datetime.now().isoformat()
    })
```

#### Step 3: Manual Spot Check (10%)
- Randomly sample 10% of results
- Verify websites exist and match
- Check LinkedIn profiles
- Validate email formats

#### Step 4: Export with Verification Metadata
- Include all verification flags
- Document API source and date
- Add confidence scores

**Output:** 50-200 verified targets per day

---

## Hybrid Approach (RECOMMENDED)

### Best of Both Worlds

**Phase 1: API Volume (Week 1)**
- Use Apollo.io/ZoomInfo to get 500-1000 contacts
- Apply ICP filters
- Export top 100 by fit score

**Phase 2: Manual Verification (Week 2)**
- Manually verify top 50 prospects
- Deep research on top 10
- Create detailed profiles (North Branch style)

**Phase 3: Outreach (Week 3+)**
- Personalized outreach to top 10 (manual research)
- Templated outreach to next 40 (API data)
- Automated nurture for remaining 50

---

## Code Template: Real Data Enforcer

```python
#!/usr/bin/env python3
"""
Real Data Enforcer - Prevents mock data in production
"""

class RealDataValidator:
    """Validates that prospect data is real and verified"""

    PROHIBITED_PATTERNS = [
        # Mock company names
        r'.*Solutions Inc$',
        r'.*Capital$',
        r'.*Group$',
        r'Global.*',
        r'Premier.*',
        r'Apex.*',

        # Mock emails
        r'.*@example\.com',
        r'.*@test\.com',
        r'.*@demo\.com',

        # Mock phones
        r'\(555\)',
        r'555-',

        # Mock websites
        r'https?://example\.',
        r'https?://test\.',
    ]

    def validate_prospect(self, prospect: dict) -> tuple[bool, list[str]]:
        """
        Validate a prospect record

        Returns:
            (is_valid, error_messages)
        """
        errors = []

        # Check for required fields
        required = ['company_name', 'website', 'data_source', 'verified_date']
        for field in required:
            if not prospect.get(field):
                errors.append(f"Missing required field: {field}")

        # Check for mock data patterns
        import re
        for pattern in self.PROHIBITED_PATTERNS:
            if re.match(pattern, prospect.get('company_name', '')):
                errors.append(f"Company name matches mock pattern: {pattern}")
            if re.match(pattern, prospect.get('email', '')):
                errors.append(f"Email matches mock pattern: {pattern}")
            if re.match(pattern, prospect.get('phone', '')):
                errors.append(f"Phone matches mock pattern: {pattern}")
            if re.match(pattern, prospect.get('website', '')):
                errors.append(f"Website matches mock pattern: {pattern}")

        # Check verification flags
        if not prospect.get('verified_website'):
            errors.append("Website not verified")

        # Check data source is approved
        approved_sources = [
            'Apollo.io API',
            'ZoomInfo',
            'LinkedIn Sales Navigator',
            'Manual Research',
            'Google Places API',
            'Hunter.io'
        ]

        if prospect.get('data_source') not in approved_sources:
            if 'demo' in prospect.get('data_source', '').lower():
                errors.append("PROHIBITED: Demo/mock data source")
            elif not prospect.get('data_source'):
                errors.append("Data source not specified")

        return (len(errors) == 0, errors)

    def validate_dataset(self, prospects: list[dict]) -> dict:
        """Validate entire dataset"""

        results = {
            'total': len(prospects),
            'valid': 0,
            'invalid': 0,
            'errors': []
        }

        for i, prospect in enumerate(prospects):
            is_valid, errors = self.validate_prospect(prospect)

            if is_valid:
                results['valid'] += 1
            else:
                results['invalid'] += 1
                results['errors'].append({
                    'index': i,
                    'company': prospect.get('company_name', 'Unknown'),
                    'errors': errors
                })

        return results
```

---

## Testing & Compliance

### Before Each Production Run

1. **Run Data Validator**
   ```bash
   python3 validate_real_data.py prospects.csv
   ```

2. **Manual Spot Check**
   - Review 10 random prospects
   - Verify websites load
   - Check LinkedIn profiles exist

3. **Documentation**
   - Document data sources used
   - Record verification date
   - Note any data quality issues

### Quarterly Audit

- Review all prospect data generated in past quarter
- Verify data sources are still active/valid
- Update validation rules based on findings
- Archive old/stale data

---

## Migration Plan

### Immediate (Today)

1. ✅ Create this policy document
2. ⏳ Update all existing scripts with validation
3. ⏳ Add data source tracking to all exports

### This Week

1. Add RealDataValidator to core/
2. Update find_targets.py with validation
3. Update flyflat_live_scraper.py with validation
4. Create manual research template

### This Month

1. Integrate Apollo.io API
2. Set up LinkedIn Sales Navigator
3. Create hybrid workflow tools
4. Train team on new processes

---

## Support & Resources

### Questions?

**"How do I get started with real data?"**
- Start with manual research (North Branch approach)
- 15-30 min per target = high quality
- 3-5 targets per day is excellent

**"What if I need high volume?"**
- Use Apollo.io or ZoomInfo API
- Budget $100-500/month for data
- Still requires 10% manual verification

**"Can I ever use mock data?"**
- Only for testing code functionality
- Must be clearly labeled "TEST DATA"
- Never for production prospect lists

**"What about web scraping?"**
- Only with verification (see policy above)
- Respect robots.txt and ToS
- Use proxies and rate limiting
- Manual spot-check required

---

## Enforcement

**This policy is MANDATORY for all ScrapeMaster usage.**

Any script that generates mock/fake prospect data will:
1. Display prominent warning
2. Require explicit --allow-mock-data flag
3. Tag all exports with "DEMO DATA - NOT FOR PRODUCTION"

All production prospect lists must pass RealDataValidator before export.

---

**Document Owner:** Mike Finneran
**Last Updated:** October 18, 2025
**Next Review:** January 2026
