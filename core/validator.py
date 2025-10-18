#!/usr/bin/env python3
"""
Real Data Validator - Ensures only real, verified data is used
Enforces REAL_DATA_POLICY.md requirements
"""

import re
from datetime import datetime, timedelta
from typing import Dict, List, Tuple
from pathlib import Path


class RealDataValidator:
    """
    Validates that prospect/target data is real and verified
    Prevents mock/demo/fake data from entering production systems
    """

    # Patterns that indicate MOCK data (prohibited)
    PROHIBITED_PATTERNS = {
        'company_name': [
            r'^.*Solutions Inc\.?$',
            r'^.*Capital$',
            r'^.*Group$',
            r'^.*Partners$',
            r'^Global\s+',
            r'^Premier\s+',
            r'^Apex\s+',
            r'^Zenith\s+',
            r'^Summit\s+',
            r'^Vanguard\s+',
            r'^Pinnacle\s+',
            r'^Sterling\s+',
            r'^Quantum\s+',
            r'^\w+\s+(Solutions|Consulting|Advisors|Technologies)$',
        ],
        'email': [
            r'.*@example\.com$',
            r'.*@test\.com$',
            r'.*@demo\.com$',
            r'.*@sample\.com$',
            r'.*@mock\.com$',
        ],
        'phone': [
            r'^\(555\)',
            r'^555-',
            r'^\+1-555-',
            r'^123-456-',
        ],
        'website': [
            r'^https?://example\.',
            r'^https?://test\.',
            r'^https?://demo\.',
            r'^https?://sample\.',
            r'^https?://mock\.',
            r'\.example\.com$',
        ]
    }

    # Approved data sources (real data only)
    APPROVED_SOURCES = [
        'Apollo.io API',
        'ZoomInfo',
        'LinkedIn Sales Navigator',
        'LinkedIn Manual Research',
        'Manual Research',
        'Manual Website Research',
        'Google Places API',
        'Hunter.io',
        'Clearbit',
        'Yellow Pages Verified',
        'Yelp Verified',
        'BBB Directory',
        'Chamber of Commerce',
        'Industry Association Directory',
        'Secretary of State Registry',
    ]

    # Prohibited sources (demo/mock data)
    PROHIBITED_SOURCES = [
        'demo',
        'mock',
        'test',
        'sample',
        'generated',
        'simulated',
        'fake',
    ]

    def __init__(self, strict_mode: bool = True):
        """
        Initialize validator

        Args:
            strict_mode: If True, enforce all requirements. If False, only warn.
        """
        self.strict_mode = strict_mode
        self.validation_results = []

    def validate_prospect(self, prospect: Dict) -> Tuple[bool, List[str]]:
        """
        Validate a single prospect record

        Args:
            prospect: Prospect data dictionary

        Returns:
            (is_valid, error_messages)
        """
        errors = []
        warnings = []

        # 1. Check required fields
        required_fields = [
            'company_name',
            'website',
            'data_source',
            'verified_date'
        ]

        for field in required_fields:
            if not prospect.get(field):
                errors.append(f"❌ Missing required field: {field}")

        # 2. Check for prohibited patterns (MOCK DATA)
        for field, patterns in self.PROHIBITED_PATTERNS.items():
            value = prospect.get(field, '')
            if not value:
                continue

            for pattern in patterns:
                if re.match(pattern, str(value), re.IGNORECASE):
                    errors.append(
                        f"❌ PROHIBITED: {field} matches mock data pattern: '{pattern}'\n"
                        f"   Value: '{value}'\n"
                        f"   This appears to be FAKE/GENERATED data."
                    )

        # 3. Check data source is approved
        data_source = prospect.get('data_source', '')

        # Check for prohibited sources
        for prohibited in self.PROHIBITED_SOURCES:
            if prohibited.lower() in data_source.lower():
                errors.append(
                    f"❌ PROHIBITED DATA SOURCE: '{data_source}'\n"
                    f"   Contains prohibited keyword: '{prohibited}'\n"
                    f"   This is MOCK/DEMO data and cannot be used in production."
                )

        # Check if source is approved
        if data_source and data_source not in self.APPROVED_SOURCES:
            warnings.append(
                f"⚠️  Unknown data source: '{data_source}'\n"
                f"   Approved sources: {', '.join(self.APPROVED_SOURCES[:5])}..."
            )

        # 4. Check verification flags
        if not prospect.get('verified_website'):
            warnings.append("⚠️  Website not verified")

        # 5. Check verified_date is recent (within 6 months)
        verified_date = prospect.get('verified_date')
        if verified_date:
            try:
                date_obj = datetime.fromisoformat(verified_date.replace('Z', '+00:00'))
                age_days = (datetime.now() - date_obj).days

                if age_days > 180:  # 6 months
                    warnings.append(
                        f"⚠️  Data is {age_days} days old (verified: {verified_date})\n"
                        f"   Consider re-verifying."
                    )
            except ValueError:
                warnings.append(f"⚠️  Invalid date format: {verified_date}")

        # 6. Check verification confidence
        confidence = prospect.get('verification_confidence', 0)
        if confidence < 70:
            warnings.append(
                f"⚠️  Low verification confidence: {confidence}/100\n"
                f"   Recommend manual verification."
            )

        # 7. Check contact information completeness
        contact_fields = ['contact_name', 'contact_email', 'contact_title']
        missing_contact = [f for f in contact_fields if not prospect.get(f)]

        if missing_contact:
            warnings.append(
                f"⚠️  Incomplete contact information: missing {', '.join(missing_contact)}"
            )

        # Combine errors and warnings
        all_issues = errors + warnings

        # In strict mode, warnings are also errors
        if self.strict_mode:
            is_valid = len(errors) == 0 and len(warnings) == 0
        else:
            is_valid = len(errors) == 0

        return (is_valid, all_issues)

    def validate_dataset(self, prospects: List[Dict]) -> Dict:
        """
        Validate entire dataset

        Args:
            prospects: List of prospect dictionaries

        Returns:
            Validation results summary
        """
        results = {
            'total': len(prospects),
            'valid': 0,
            'invalid': 0,
            'warnings': 0,
            'errors_by_prospect': [],
            'summary': {}
        }

        for i, prospect in enumerate(prospects):
            is_valid, issues = self.validate_prospect(prospect)

            if is_valid:
                results['valid'] += 1
            else:
                results['invalid'] += 1

                # Separate errors from warnings
                errors = [issue for issue in issues if issue.startswith('❌')]
                warnings = [issue for issue in issues if issue.startswith('⚠️')]

                results['errors_by_prospect'].append({
                    'index': i,
                    'company': prospect.get('company_name', 'Unknown'),
                    'errors': errors,
                    'warnings': warnings
                })

                if warnings:
                    results['warnings'] += 1

        # Calculate summary statistics
        results['summary'] = {
            'pass_rate': (results['valid'] / results['total'] * 100) if results['total'] > 0 else 0,
            'error_rate': (results['invalid'] / results['total'] * 100) if results['total'] > 0 else 0,
            'has_mock_data': any('PROHIBITED' in str(e) for e in results['errors_by_prospect']),
        }

        return results

    def print_validation_report(self, results: Dict) -> None:
        """Print formatted validation report"""

        print("\n" + "=" * 80)
        print("REAL DATA VALIDATION REPORT")
        print("=" * 80)
        print()

        print(f"📊 SUMMARY:")
        print(f"  Total Prospects:     {results['total']}")
        print(f"  ✅ Valid:            {results['valid']}")
        print(f"  ❌ Invalid:          {results['invalid']}")
        print(f"  ⚠️  With Warnings:    {results['warnings']}")
        print()

        print(f"📈 STATISTICS:")
        print(f"  Pass Rate:           {results['summary']['pass_rate']:.1f}%")
        print(f"  Error Rate:          {results['summary']['error_rate']:.1f}%")
        print()

        # Check for mock data
        if results['summary']['has_mock_data']:
            print("🚨 CRITICAL: MOCK/FAKE DATA DETECTED!")
            print("=" * 80)
            print()
            print("⛔ This dataset contains PROHIBITED mock/demo/fake data.")
            print("⛔ Production use is BLOCKED until issues are resolved.")
            print()

        # Show errors
        if results['errors_by_prospect']:
            print("❌ VALIDATION ERRORS:")
            print("-" * 80)

            for error_info in results['errors_by_prospect'][:10]:  # Show first 10
                print(f"\n#{error_info['index'] + 1}: {error_info['company']}")

                for error in error_info['errors']:
                    print(f"  {error}")

                for warning in error_info['warnings']:
                    print(f"  {warning}")

            if len(results['errors_by_prospect']) > 10:
                remaining = len(results['errors_by_prospect']) - 10
                print(f"\n... and {remaining} more prospects with issues")

        else:
            print("✅ All prospects passed validation!")

        print()
        print("=" * 80)

    def enforce_policy(self, prospects: List[Dict]) -> List[Dict]:
        """
        Enforce real data policy - only return valid prospects

        Args:
            prospects: List of prospect dictionaries

        Returns:
            Filtered list containing only valid prospects
        """
        valid_prospects = []

        for prospect in prospects:
            is_valid, issues = self.validate_prospect(prospect)

            if is_valid:
                valid_prospects.append(prospect)
            else:
                # Log rejected prospect
                print(f"⛔ REJECTED: {prospect.get('company_name', 'Unknown')}")
                for issue in issues:
                    if issue.startswith('❌'):
                        print(f"    {issue}")

        print()
        print(f"✅ Kept {len(valid_prospects)}/{len(prospects)} valid prospects")
        print(f"❌ Rejected {len(prospects) - len(valid_prospects)} prospects with policy violations")

        return valid_prospects


# Convenience function for quick validation
def validate_prospects(prospects: List[Dict], strict: bool = True) -> bool:
    """
    Quick validation function

    Args:
        prospects: List of prospect dictionaries
        strict: If True, enforce strict validation

    Returns:
        True if all prospects are valid
    """
    validator = RealDataValidator(strict_mode=strict)
    results = validator.validate_dataset(prospects)
    validator.print_validation_report(results)

    return results['invalid'] == 0


# CLI interface
if __name__ == "__main__":
    import sys
    import json
    import csv

    if len(sys.argv) < 2:
        print("Usage: python validator.py <prospects.csv|prospects.json>")
        sys.exit(1)

    file_path = Path(sys.argv[1])

    # Load prospects
    if file_path.suffix == '.json':
        with open(file_path, 'r') as f:
            prospects = json.load(f)
    elif file_path.suffix == '.csv':
        with open(file_path, 'r') as f:
            reader = csv.DictReader(f)
            prospects = list(reader)
    else:
        print(f"Unsupported file format: {file_path.suffix}")
        sys.exit(1)

    # Validate
    validator = RealDataValidator(strict_mode=True)
    results = validator.validate_dataset(prospects)
    validator.print_validation_report(results)

    # Exit with error code if validation failed
    if results['summary']['has_mock_data']:
        print("\n🚨 VALIDATION FAILED: Mock data detected")
        sys.exit(1)
    elif results['invalid'] > 0:
        print(f"\n⚠️  VALIDATION WARNING: {results['invalid']} prospects have issues")
        sys.exit(0)  # Exit success but with warning
    else:
        print("\n✅ VALIDATION PASSED: All prospects are real and verified")
        sys.exit(0)
