# Quick Start: LinkedIn Sales Nav → 25 Targets Today

**You can get 25 North Branch targets in the next 30 minutes!**

---

## Step 1: LinkedIn Sales Nav Search (10 min)

### Go to LinkedIn Sales Navigator

1. **Click "Companies" tab**
2. **Set these filters:**

```
Industry:
  - HVAC
  - Heating and Air Conditioning
  - Mechanical or Industrial Engineering
  - Construction
  - Building Materials
  - Industrial Automation

Geography:
  - Illinois
  - Wisconsin
  - Michigan
  - Indiana

Company headcount:
  - 20-50
  - 51-200
  - 201-500

Company type:
  - Privately Held
```

3. **Click "Search"**

### Save the Results

**Option A: Manual (15 min)**
1. Open a spreadsheet
2. For first 25 companies, copy:
   - Company name
   - Industry
   - Location
   - Employee count
   - Website (click company → About → Website)

3. Save as `linkedin_export.csv` with these columns:
   ```
   company_name,industry,location,employees,website
   ABC HVAC Inc,HVAC,Chicago IL,75,https://abchvac.com
   XYZ Construction,Construction,Milwaukee WI,120,https://xyzconstruction.com
   ...
   ```

**Option B: Use Sales Nav Export (5 min)**
- If your plan allows, click "Save to CRM" → Export to CSV
- Columns will include all the data automatically

---

## Step 2: Enrich with Websites (15 min)

### Run the Enrichment Script

```bash
cd "/Users/mikefinneran/Library/CloudStorage/GoogleDrive-mike.finneran@gmail.com/My Drive/Project Database/Current Projects/scrapemaster"

python3 linkedin_enricher.py linkedin_export.csv
```

**What it does:**
- Reads your LinkedIn export
- Visits each company website
- Extracts: phone, email, services, certifications
- Validates data quality
- Exports: `enriched_linkedin_export.csv`

**Time:** ~30 seconds per company = 15 minutes for 25

---

## Step 3: Review Results (5 min)

### Open the Enriched File

```bash
open enriched_linkedin_export.csv
```

**You'll see:**
- ✅ Company name (from LinkedIn)
- ✅ Industry (from LinkedIn)
- ✅ Location (from LinkedIn)
- ✅ Employees (from LinkedIn)
- ✅ Website (from LinkedIn)
- ✅ **Phone** (from website - NEW!)
- ✅ **Email** (from website - NEW!)
- ✅ **Services** (from website - NEW!)
- ✅ **Certifications** (from website - NEW!)
- ✅ **Verification confidence** (85-95%)

---

## Step 4: Find Decision Makers (10 min)

### Back to LinkedIn Sales Nav

1. **Click "Leads" tab**
2. **Set filters:**

```
Title:
  - CEO
  - Owner
  - President
  - Founder

Current company:
  - [Paste company names from your list]

Seniority:
  - Owner
  - C-Level

Geography:
  - Illinois, Wisconsin, Michigan, Indiana
```

3. **For each of your 25 companies:**
   - Search for owner/CEO
   - Copy: Name, Title, LinkedIn URL
   - Add to your spreadsheet

---

## Example Result

After 30 minutes, you'll have:

```csv
company_name,industry,location,employees,website,phone,email,services,certifications,owner_name,owner_title,owner_linkedin
"Midwest HVAC Solutions","HVAC","Milwaukee, WI",85,"https://midwesthvac.com","(414) 555-1234","info@midwesthvac.com","Commercial HVAC | Installation | Maintenance | Repair","NATE Certified | EPA Licensed","James Peterson","Owner","https://linkedin.com/in/jamespeterson"
```

**This is a COMPLETE acquisition target:**
- ✅ Company info (verified)
- ✅ Contact details (verified)
- ✅ Services (verified)
- ✅ Certifications (verified)
- ✅ Decision maker (verified)

---

## North Branch Saved Searches

Create these for quick daily searches:

### Search 1: "NBC - HVAC Midwest"
```
Industry: HVAC, Heating/Air Conditioning
Location: IL, WI, MI, IN
Size: 20-500 employees
Type: Private
```

### Search 2: "NBC - Construction Midwest"
```
Industry: Construction, Commercial Construction
Location: Chicago, Milwaukee metro
Size: 50-250
Type: Private
Keywords: Commercial, Contractor
```

### Search 3: "NBC - Industrial Services"
```
Industry: Industrial Services, Facility Services
Location: IL, WI, MI, IN
Size: 20-500
Type: Private
Growth: Hiring last 90 days
```

**Save these searches → Click "Get alerts" → Daily email with new matches**

---

## Daily Workflow (Once Set Up)

### Morning (30 min)
1. Open Sales Nav saved search
2. Export 25 new companies to CSV
3. Run enrichment script
4. Find decision makers

### Output
- 25 verified targets
- Full contact info
- Decision maker names
- Ready for outreach

### Monthly
- 25/day × 20 days = **500 targets/month**
- Cost: $79.99 (Sales Nav - already have)
- Cost per target: **$0.16**

---

## Troubleshooting

### "No module named 'core.engine'"

```bash
# Make sure you're in the scrapemaster directory
cd "/Users/mikefinneran/Library/CloudStorage/GoogleDrive-mike.finneran@gmail.com/My Drive/Project Database/Current Projects/scrapemaster"

# Try again
python3 linkedin_enricher.py linkedin_export.csv
```

### "File not found: linkedin_export.csv"

```bash
# Make sure CSV is in the scrapemaster directory
ls -l linkedin_export.csv

# Or provide full path
python3 linkedin_enricher.py "/path/to/linkedin_export.csv"
```

### "Website scraping failed"

- Some websites block scrapers
- That's OK - you still have LinkedIn data
- Verification confidence will be 70% instead of 95%
- Still usable for outreach

---

## Tips for Better Results

### LinkedIn Search
- Use Boolean: "HVAC OR Heating OR Cooling"
- Set alerts on saved searches
- Check "Posted jobs" for growth signal
- Exclude Fortune 1000 companies

### Website Enrichment
- Script automatically handles:
  - Different website structures
  - Missing contact info
  - Slow websites
  - SSL certificates

### Decision Makers
- Search variations:
  - "Owner" OR "CEO" OR "President"
  - "Founder" OR "Managing Partner"
- Check LinkedIn profile for:
  - Years at company (succession timing)
  - Previous exits (M&A experience)
  - Network (mutual connections)

---

## Next Steps

### Today: Test the Workflow

1. **Create first saved search** (5 min)
2. **Export 5-10 companies** as test (2 min)
3. **Run enrichment script** (3 min)
4. **Review results** (5 min)

**Total: 15 minutes to validate it works**

### This Week: Scale to 25/day

1. **Refine saved searches** based on test results
2. **Build routine**: Morning Sales Nav → Enrich → Review
3. **First 100 targets** by end of week

### This Month: 500 Targets

1. **Daily habit**: 30 min every morning
2. **Build master database**: All 500 targets
3. **Prioritize**: Top 50 for immediate outreach
4. **Track metrics**: Contact rate, meeting rate

---

## Success Metrics

**Target (After 1 Month):**
- 500 companies identified
- 100 decision makers contacted
- 20 initial conversations
- 5 NDAs signed
- 1-2 LOIs submitted

**Your Setup:**
- LinkedIn Sales Nav: ✅ (already have)
- ScrapeMaster: ✅ (free)
- Time: 30 min/day
- Cost: $79.99/month (just Sales Nav)

**Competitive Advantage:**
- No ZoomInfo needed ($250/month saved)
- No Apollo needed ($99/month saved)
- Higher quality (LinkedIn + verified websites)
- Real decision makers (not just company contacts)

---

## Ready to Start?

**Right now:**

1. Open LinkedIn Sales Navigator
2. Search: HVAC + Illinois
3. Export first 25 companies
4. Run: `python3 linkedin_enricher.py linkedin_export.csv`
5. Review enriched results

**You'll have 25 acquisition targets in 30 minutes!**

---

**Questions? Check:**
- `LINKEDIN_SALES_NAV_INTEGRATION.md` - Full integration guide
- `PROJECT_STATUS.md` - Complete project context
- GitHub: https://github.com/mikefinneran-sudo/scrapemaster
