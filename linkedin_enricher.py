#!/usr/bin/env python3
"""
LinkedIn Sales Navigator Enricher

Takes LinkedIn Sales Nav export and enriches with website data.

Usage:
    python3 linkedin_enricher.py linkedin_export.csv

Input CSV (from Sales Nav):
    - company_name
    - industry
    - location
    - employees
    - website
    - linkedin_url (optional)

Output:
    - All input fields
    - phone (from website)
    - email (from website)
    - services (from website)
    - certifications (from website)
    - verification_confidence (0-100)
"""

import asyncio
import csv
import sys
from pathlib import Path
from datetime import datetime
from typing import List, Dict

# Add core to path
sys.path.insert(0, str(Path(__file__).parent))

from core.engine import ScraperEngine, ScrapeOptions
from core.validator import RealDataValidator


async def enrich_company(engine: ScraperEngine, company: Dict) -> Dict:
    """
    Enrich a single company with website data

    Args:
        engine: ScraperEngine instance
        company: Company data from LinkedIn

    Returns:
        Enriched company data
    """
    # Start with LinkedIn data
    prospect = {
        'company_name': company.get('company_name', ''),
        'industry': company.get('industry', ''),
        'location': company.get('location', ''),
        'employees': company.get('employees', ''),
        'website': company.get('website', ''),
        'linkedin_url': company.get('linkedin_url', ''),

        # Enrichment fields (to be filled)
        'phone': '',
        'email': '',
        'services': '',
        'certifications': '',
        'address': '',

        # Metadata
        'data_source': 'LinkedIn Sales Navigator + Website Enrichment',
        'verified_date': datetime.now().isoformat(),
        'verified_website': False,
        'verification_confidence': 70  # Base score from LinkedIn
    }

    website = prospect['website']

    if not website:
        print(f"  ⚠️  No website - skipping enrichment")
        return prospect

    # Ensure website has protocol
    if not website.startswith('http'):
        website = f'https://{website}'
        prospect['website'] = website

    try:
        # Define selectors for common website elements
        selectors = {
            # Phone numbers
            'phone': '[href^="tel:"]::attr(href), .phone, .contact-phone, footer a[href^="tel:"]',

            # Email addresses
            'email': '[href^="mailto:"]::attr(href), .email, .contact-email',

            # Address
            'address': '.address, [itemprop="address"], .contact-address, footer .address',

            # Services/capabilities
            'services': '.services, .capabilities, .what-we-do, .solutions, main h2, main h3',

            # Certifications/licenses
            'certifications': '.certifications, .licenses, .accreditations, .memberships, .awards',
        }

        options = ScrapeOptions(
            timeout=15,
            retry_count=2,
            wait_time=1.0
        )

        print(f"  🔍 Scraping: {website}")
        result = await engine.scrape(website, selectors, options)

        if result.success:
            # Clean and add scraped data
            data = result.data

            # Phone - clean tel: prefix
            if data.get('phone'):
                phone = data['phone']
                if isinstance(phone, list):
                    phone = phone[0] if phone else ''
                phone = phone.replace('tel:', '').strip()
                prospect['phone'] = phone

            # Email - clean mailto: prefix
            if data.get('email'):
                email = data['email']
                if isinstance(email, list):
                    email = email[0] if email else ''
                email = email.replace('mailto:', '').strip()
                prospect['email'] = email

            # Address
            if data.get('address'):
                address = data['address']
                if isinstance(address, list):
                    address = ' '.join(address)
                prospect['address'] = address.strip()

            # Services - take first few
            if data.get('services'):
                services = data['services']
                if isinstance(services, list):
                    services = ' | '.join(services[:5])  # First 5 services
                prospect['services'] = services.strip()

            # Certifications
            if data.get('certifications'):
                certs = data['certifications']
                if isinstance(certs, list):
                    certs = ' | '.join(certs)
                prospect['certifications'] = certs.strip()

            prospect['verified_website'] = True
            prospect['verification_confidence'] = 95  # High confidence

            print(f"  ✅ Enriched successfully")
            print(f"     Phone: {prospect['phone'][:20] if prospect['phone'] else 'N/A'}")
            print(f"     Email: {prospect['email'][:30] if prospect['email'] else 'N/A'}")

        else:
            print(f"  ❌ Scraping failed: {result.error}")
            prospect['verification_confidence'] = 70  # LinkedIn only

    except Exception as e:
        print(f"  ⚠️  Error enriching: {e}")
        prospect['verification_confidence'] = 70  # LinkedIn only

    # Add rate limit delay
    await asyncio.sleep(2)

    return prospect


async def enrich_from_linkedin_export(input_csv: str, output_csv: str = None):
    """
    Enrich LinkedIn Sales Nav export with website data

    Args:
        input_csv: Path to LinkedIn export CSV
        output_csv: Path for output (defaults to enriched_[input].csv)
    """
    input_path = Path(input_csv)

    if not input_path.exists():
        print(f"❌ Input file not found: {input_csv}")
        return

    if output_csv is None:
        output_csv = input_path.parent / f"enriched_{input_path.name}"

    print("\n" + "="*80)
    print("LINKEDIN SALES NAVIGATOR ENRICHER")
    print("="*80)
    print()
    print(f"📂 Input:  {input_csv}")
    print(f"📂 Output: {output_csv}")
    print()

    # Read LinkedIn export
    with open(input_csv, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        linkedin_data = list(reader)

    print(f"📊 Found {len(linkedin_data)} companies from LinkedIn Sales Nav")
    print()

    # Initialize scraper
    engine = ScraperEngine()

    # Enrich each company
    prospects = []

    for i, company in enumerate(linkedin_data, 1):
        print(f"\n[{i}/{len(linkedin_data)}] {company.get('company_name', 'Unknown')}")
        print("-" * 80)

        enriched = await enrich_company(engine, company)
        prospects.append(enriched)

    await engine.close()

    print("\n" + "="*80)
    print("ENRICHMENT COMPLETE")
    print("="*80)
    print()

    # Validate
    print("🔍 Validating data quality...\n")
    validator = RealDataValidator(strict_mode=False)
    results = validator.validate_dataset(prospects)
    validator.print_validation_report(results)

    # Export
    print(f"\n💾 Exporting to {output_csv}...\n")

    with open(output_csv, 'w', newline='', encoding='utf-8') as f:
        if prospects:
            fieldnames = [
                'company_name', 'industry', 'location', 'employees',
                'website', 'phone', 'email', 'address',
                'services', 'certifications', 'linkedin_url',
                'data_source', 'verified_date', 'verified_website',
                'verification_confidence'
            ]

            writer = csv.DictWriter(f, fieldnames=fieldnames, extrasaction='ignore')
            writer.writeheader()
            writer.writerows(prospects)

    print(f"✅ Exported {len(prospects)} enriched prospects")
    print()

    # Summary stats
    with_phone = len([p for p in prospects if p.get('phone')])
    with_email = len([p for p in prospects if p.get('email')])
    with_services = len([p for p in prospects if p.get('services')])
    avg_confidence = sum(p.get('verification_confidence', 0) for p in prospects) / len(prospects)

    print("📊 ENRICHMENT STATS:")
    print(f"  Total prospects:       {len(prospects)}")
    print(f"  With phone numbers:    {with_phone} ({with_phone/len(prospects)*100:.1f}%)")
    print(f"  With emails:           {with_email} ({with_email/len(prospects)*100:.1f}%)")
    print(f"  With services:         {with_services} ({with_services/len(prospects)*100:.1f}%)")
    print(f"  Avg confidence score:  {avg_confidence:.1f}/100")
    print()

    print("✅ Done! Ready to import into CRM.")
    print()


def print_usage():
    """Print usage instructions"""
    print("""
LinkedIn Sales Navigator Enricher

USAGE:
    python3 linkedin_enricher.py <input.csv> [output.csv]

INPUT CSV FORMAT (from LinkedIn Sales Navigator):
    Required columns:
    - company_name
    - website

    Optional columns:
    - industry
    - location
    - employees
    - linkedin_url

OUTPUT:
    Enriched CSV with additional fields:
    - phone (from website)
    - email (from website)
    - services (from website)
    - certifications (from website)
    - verification_confidence (0-100)

EXAMPLE:
    1. Export companies from LinkedIn Sales Nav to CSV
    2. Run: python3 linkedin_enricher.py linkedin_export.csv
    3. Import enriched_linkedin_export.csv into CRM

WORKFLOW:
    LinkedIn Sales Nav → Export CSV → Enrich → Validate → CRM

    Sales Nav gives you:
    - Company names
    - Industries
    - Locations
    - Employee counts
    - Websites
    - Decision makers

    This script adds:
    - Phone numbers
    - Email addresses
    - Services offered
    - Certifications
    - Verification scores
""")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print_usage()
        sys.exit(1)

    input_file = sys.argv[1]
    output_file = sys.argv[2] if len(sys.argv) > 2 else None

    asyncio.run(enrich_from_linkedin_export(input_file, output_file))
