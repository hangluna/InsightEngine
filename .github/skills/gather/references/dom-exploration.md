# DOM Exploration Reference — Source Structure Discovery

## Overview

DOM exploration is triggered when `site:source.com` search returns **thin results**
(below the quality threshold). Instead of giving up, the gather skill fetches the source
homepage and extracts the site's internal structure to construct better queries or navigate
directly to item pages.

**Thin results threshold:** < 3 quality item URLs from site-specific search.

---

## Why DOM Exploration?

Some platforms are poorly indexed by Google, have anti-crawl measures, or serve most
content behind their own search infrastructure. For these, the platform's own navigation
and search tools outperform Google site-search.

Examples:
- LinkedIn: Google `site:linkedin.com jobs` returns limited results; LinkedIn's own
  job search API (`/jobs/search?keywords=...`) returns far more.
- Specialized B2B directories: Rarely indexed; their own site search is the only path.
- Regional platforms: Google may not have indexed recent postings; platform-native
  search is always up-to-date.

---

## Step-by-Step Protocol

### Step 1: Fetch Source Homepage

```python
# Use standard 3-tier fallback (Tier 1 first, Playwright if blocked)
homepage_url = f"https://{source_domain}"
content = fetch_webpage(url=homepage_url, query="navigation search links")
```

If homepage is behind login/paywall → use search page URL instead:
```python
search_page_candidates = [
    f"https://{source_domain}/search",
    f"https://{source_domain}/jobs",
    f"https://{source_domain}/find",
    f"https://{source_domain}/browse",
]
# Try each until one returns content
```

### Step 2: Extract DOM Structure

Parse the fetched HTML to find navigation and search elements:

```python
# Run via terminal (scripts/dom_explorer.py)
python3 .github/skills/gather/scripts/dom_explorer.py "{url}" --extract nav,search,links
```

**What to extract:**

| Element | Look for | Example output |
|---------|----------|----------------|
| Nav links | `<nav>`, `<header>` anchor tags | `/jobs/frontend`, `/products/mobile` |
| Search forms | `<form>`, `input[type=search]`, `input[name*=query]` | `action="/search"`, `name="q"` |
| Search API hints | `fetch()`, `XMLHttpRequest`, `axios` in inline JS | `/api/search?q=` |
| URL patterns | Anchor href values on listing/item cards | `/jobs/senior-dev-at-grab-12345` |
| Pagination | "Load more", `?page=2` patterns | Reveals item URL structure |

### Step 3: Build Targeted Queries

From extracted structure, construct better search strategies:

```yaml
# If nav links found → target specific category pages
STRATEGY_A_NAV:
  found: "/jobs/it-jobs" link in nav
  action: Fetch "https://source.com/jobs/it-jobs?query={keyword}"
  reason: Direct listing page bypass Google indexing limits

# If search form found → construct form submit URL
STRATEGY_B_FORM:
  found: <form action="/search"> with input name="q"
  action: Fetch "https://source.com/search?q={keyword}&type=jobs"
  reason: Uses platform's own full-text search

# If URL patterns found → extract item slug format
STRATEGY_C_PATTERNS:
  found: href="/it-jobs/frontend-developer-at-fpt-12345" pattern
  action: Use regex to find similar hrefs in listing pages
  reason: Identifies item URL format for Phase 2 fetch validation
```

### Step 4: Report and Proceed

After DOM exploration, report to the pipeline:

```
🔍 DOM exploration: {source_domain}
  - Nav links found: {N} category pages
  - Search form: {found/not found} → {action URL if found}
  - URL pattern: {example item URL pattern}
→ Switching to: {chosen strategy}
```

Then continue with the improved search strategy in DC-1/DC-2.

---

## Playwright for DOM Extraction

When `fetch_webpage` returns insufficient HTML (SPA/JS-rendered), use Playwright to
extract the fully-rendered DOM:

```bash
python3 .github/skills/gather/scripts/dom_explorer.py "{url}" --use-playwright
```

The script:
1. Launches Chromium in stealth mode
2. Waits for `DOMContentLoaded` + 2 seconds for JS rendering
3. Extracts nav, forms, links, and API calls from rendered page
4. Returns structured JSON: `{nav_links: [...], search_forms: [...], url_patterns: [...]}`

---

## Quality Check for DOM Exploration

After DOM exploration, verify the result is actionable:

```yaml
DOM_RESULT_QUALITY:
  useful_if_any:
    - Found ≥1 nav link pointing to a relevant category
    - Found ≥1 search form with a usable action URL
    - Found ≥3 item URL patterns with IDs/slugs
    
  not_useful:
    - Homepage is a login wall (< 100 chars of nav content)
    - All nav links point to external domains
    - No search input found anywhere
    
  if_not_useful:
    action: Skip to DC-3 (Company/Entity Research) or DC-6 (Adaptive Flow Advisor)
    reason: "DOM exploration returned no usable structure for {source_domain}"
```

---

## Known Platform Search Patterns

| Platform | Direct Search URL | Notes |
|----------|------------------|-------|
| ITViec | `/it-jobs?query={q}&city={city}` | Filter: `?level=fresher` |
| TopCV | `/tim-viec-lam?keyword={q}&city_ids={id}` | City IDs: HCM=1, HN=24 |
| LinkedIn | `/jobs/search/?keywords={q}&location={city}` | Auth required for full results |
| VietnamWorks | `/viec-lam/tim-viec?query={q}` | Also: `/job-search/q-{slug}` |
| Shopee | `/search?keyword={q}&page=0&sortBy=relevancy` | API: `/api/v2/search_items` |
| Lazada | `/catalog/?q={q}&_keyori=ss&from=input&spm=...` | |
| Indeed (VN) | `/jobs?q={q}&l={city}&lang=vi` | |

---

## Integration with DC-0 Sub-Flow

DOM exploration is Step 3 of the strategist-generated sub-flow:
```
Sub-flow: source-plan → site-search → [dom-explore if thin] → internal-search
                                              ↑
                                     This reference covers Step 3
```

It is triggered automatically when `site-search` (Step 2) returns thin results.
It feeds its findings into `internal-search` (Step 4).
