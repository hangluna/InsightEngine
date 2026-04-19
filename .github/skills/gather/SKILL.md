---
name: gather
description: |
  Gather content from any source: local files (docx/xlsx/pdf/pptx/txt), URLs, and web search.
  Uses markitdown as primary reader with format-specific fallbacks for garbled output.
  Web search via vscode-websearchforcopilot_webSearch for online research.
  3-tier URL fetching: fetch_webpage → httpx → Playwright stealth mode (for bot-protected sites).
  Auto-reviews gathered content quality: checks volume, coverage, specificity, and source diversity.
  If content is insufficient, automatically expands search queries and does additional rounds.
  Always use this skill when the user mentions any file to read, URL to fetch, or topic to search
  online — even casual requests like "đọc file này", "lấy thông tin từ trang web đó", "tìm hiểu
  về X", "search Google giúp tôi", or when a file path or URL is dropped into the chat, even
  without saying "gather". For bot-protected sites (Cloudflare, CAPTCHA walls, JS-heavy SPAs),
  automatically escalates to Playwright with anti-detection stealth mode.
argument-hint: "[file paths or URLs]"
version: 2.0
compatibility:
  requires:
    - Python >= 3.10
    - markitdown[all]
    - httpx, beautifulsoup4 (URL fallback)
    - playwright (bot-protected URL fallback)
  tools:
    - run_in_terminal
    - fetch_webpage (primary URL reader)
    - vscode-websearchforcopilot_webSearch (web search)
---

# Thu Thập — Content Gathering Skill

**References:** `references/code-patterns.md` | `references/web-search-enrichment.md` | `references/deep-research.md` | `references/playwright-stealth.md` | `references/data-collection.md`

This skill reads content from any source — local files, URLs, or web search — and returns
clean Markdown text. It runs standalone or as the first step in the synthesize pipeline.
**Quality-driven:** after gathering, auto-reviews content against the request; if too thin,
expands search and fetches more (max 2 supplementary rounds).

**Core principle:** Never rely solely on training knowledge for time-sensitive or region-specific
sources. Training data goes stale — platforms launch and shut down, prices change, availability
shifts. Always search at runtime to discover what currently exists, then combine those runtime
findings with relevant training knowledge for best coverage.

---

## Supported Formats

```yaml
LOCAL_FILES:
  primary_reader: markitdown
  supported: .docx, .xlsx, .pdf, .pptx, .txt, .md, .csv, .html, .jpg, .png
  fallback: format-specific library if markitdown returns < 100 chars

URLS:
  tier_1: Copilot fetch_webpage tool (fast, default)
  tier_2: httpx + beautifulsoup4 (fallback for failures)
  tier_3: Playwright stealth mode (bot-protected / JS-rendered sites)
  bot_signals: 403/429, Cloudflare challenge, empty JS content → auto-escalate to Tier 3

WEB_SEARCH:
  tool: vscode-websearchforcopilot_webSearch
  trigger: No files/URLs provided OR user says "tìm kiếm về..."
  see: references/web-search-enrichment.md
```

---

## Step 1: Choose Collection Mode

```yaml
standard:
  when: Single topic, quick overview, file reading, or user provides specific URLs
  flow: Steps 2 → 6

deep_research:
  when: >
    Multiple dimensions, temporal range, exhaustive coverage, comparison/classification,
    or synthesize passes research_depth: deep
  flow: Deep Research Protocol (below)

data_collection:
  when: >
    User wants a structured list of items with specific fields (jobs, products, companies,
    listings, reviews). synthesize passes mode: data_collection.
    Must return individual item detail URLs — listing/search page URLs are never acceptable.
  flow: Source Intelligence Protocol → Data Collection Protocol (below)
```

---

## Source Intelligence Protocol

**Purpose:** Identify which sources are currently active and accessible for the target domain
and region. Run this before data collection whenever sources are not universally known.

**When to run (all three must be true):**
1. Mode is `data_collection`
2. Item type relies on region-specific or domain-specific platforms — sources whose existence
   and accessibility depend on country, domain, or time (job boards, review platforms, local
   marketplaces, regional directories). These change: new platforms launch, old ones close.
3. No explicit source list was provided by the user or orchestrator

**When to skip:** User provides explicit URLs, or item type targets universally-known stable
platforms (LinkedIn, Amazon, GitHub, Shopee, YouTube, Glassdoor for global, etc.)

### Phase 1: Discover sources at runtime

Search for currently active platforms for the relevant domain + region + current year.
Use English queries for broader index coverage regardless of the user's request language.
Run ≥2 different queries to increase candidate diversity.

Parse results into candidate sources: `{name, url, type}`.
Types: `review_platform | job_board | directory | aggregator` — exclude `news/blog` sites
(they publish articles, not structured platform data).

Aggregator sources (sites that republish others' listings) are valid candidates — keep them,
but tag as aggregator so the collection step extracts original-source item URLs, not aggregator links.

Target: ≥3 candidates. If fewer found after a second broader round, proceed with available.
Report to user (friendly, no internal jargon): "🔍 Tìm thấy {N} nền tảng: {list}"

### Phase 2: Test and rank sources

Test each candidate with standard 3-tier fetch (fetch_webpage → httpx → Playwright).
For each source, assess three things:
- **Accessible**: HTTP 200, content received, no login/paywall blocking
- **Data present**: visible entity listings (cards, rows, reviews) — not just marketing text
- **Playwright required**: needed browser automation to retrieve useful content

Assign priority:
- **Primary:** accessible without Playwright + data visible → collect directly
- **Fallback:** accessible via Playwright only, OR partial data → collect with Playwright
- **Skip:** login wall, paywall, 4xx/timeout after all tiers, or no relevant data found

If no primary or fallback sources exist: report failure clearly with next-step options
(e.g., user provides URL directly, or switch to a global platform). Never proceed to
collection with zero viable sources.

**Language for user reports:** "nguồn chính" not "Tier 1", "nguồn dự phòng" not "Tier 2",
"cần trình duyệt đặc biệt" not "Playwright", "không truy cập được" not "403 Forbidden".

### Phase 3: Present plan and proceed

Present the verified source plan as **information, not a question**:
- Success: show primary sources, fallback sources, skipped sources with plain-language reasons
- Failure: list what was tested, offer concrete next-step options

**Auto-proceed to data collection immediately** after showing the plan.
In autonomous pipeline mode: skip any override window, do not wait for user confirmation.
If the user responds with an override (add/remove a source) before the pipeline continues:
apply it and proceed.

---

## Data Collection Protocol

**Rule:** Every collected item MUST have a `direct_url` pointing to its own detail page.
Search result pages, listing pages, and aggregator hub pages are never acceptable as output URLs.

### Per-source collection loop

For each source in the verified plan (primary first, fallback if needed), run this loop:

**1. Search** — Use `site:{source}` queries via the web search tool to find item-level URLs.
If site-search returns < 3 items: fetch the source homepage, explore DOM structure (nav links,
search forms, URL patterns, JS-rendered content) to discover the real internal search path,
then retry. See `references/data-collection.md` for DOM exploration and known platform patterns.

**2. Extract** — Fetch each item's detail URL. Extract required fields.
Missing fields → "Không rõ". Validate every URL: must contain a unique ID or slug — reject
URLs matching `?q=`, `?page=`, `/search?`, or listing-page patterns.
For sources where items appear inline or in a popup (no dedicated page per item), use the
detail URL extractor. See `references/data-collection.md` for the extractor implementation.

**3. Verify quality** after each attempt:
- ≥3 items collected from this source
- >60% of required fields present across collected items
- All `direct_url` values are item-page URLs (not listing/search pages)

**4. Retry on failure** (max 2 retries per source):
Adjust the search query → try a different URL pattern → escalate to Playwright →
run the detail URL extractor. Use a different strategy on each retry. Log each attempt.

**5. Mark and move on:** if still insufficient after max retries, mark source as failed with
a plain-language reason. **Never stop the pipeline for a single source failure** — partial
results across multiple sources are always acceptable and often sufficient.

### After all sources processed

Combine items from all succeeded sources. Report summary to user:
"✅ Thu thập hoàn tất: {N} nguồn / {total} kết quả"
List each succeeded source with item count; list each failed source with friendly reason.

If zero sources succeeded: report failure clearly — do NOT fabricate items.

**Adaptive fallback:** When multiple sources fail, call the advisory agent to suggest
alternative approaches (different search strategy, different platforms, different scope).
Present 2–3 concrete options to the user. Full spec: `references/data-collection.md`.

---

## Deep Research Protocol

For exhaustive multi-source coverage. Full protocol: `references/deep-research.md`.

1. **Decompose** — identify distinct information dimensions in the request → 1-2 queries each
2. **Round 1** — broad search across all dimensions, fetch 2-3 sources per dimension
3. **Gap analysis** — which dimensions are thin? Missing specifics? Temporal gaps?
4. **Round 2+** — targeted searches for each gap (max 3 rounds total, max 15 URL fetches)
5. **Consolidate** — structured output with dimension headers + honest coverage assessment

Report gaps honestly. If a dimension couldn't be fully covered, state it clearly.

---

## Step 2: Identify Sources

1. Extract file paths from the user request (absolute or relative)
2. Extract URLs (http:// or https://)
3. Detect if web search is needed (no specific sources given)
4. Report: "📂 Nguồn: {N} file / {M} URL / web: '{query}'"

---

## Step 3: Read Local Files

For each file:
1. Skip files > 50 MB with a warning (too large for context)
2. Try `markitdown {file}` first
3. If output < 100 chars → use format-specific fallback reader (see `references/code-patterns.md`)
4. Report: "✅ {filename} — {chars} ký tự" or "❌ {filename} — {error}"

---

## Step 4: Fetch URL Content (3-Tier Fallback)

Try tiers in order — escalate on failure or bot-detection:

1. **fetch_webpage** (default) — if content ≥ 50 chars: done
2. **httpx + BeautifulSoup** — if Tier 1 fails (see `references/code-patterns.md`)
3. **Playwright stealth** — if bot-detection signals (403, Cloudflare challenge, empty JS
   content): `python3 scripts/playwright_fetch.py "{url}" --wait 3`

**After each fetch:** read first 200–500 chars. Reject error pages, login walls, empty stubs,
or wrong page type (e.g., got a listing page when you need a detail page). If bad → next tier.

Skip directly to Playwright when: domain is known bot-protected, a previous request from the
same domain returned 403/429, or the URL pattern clearly indicates a JS-rendered SPA.

---

## Step 5: Quality Review & Auto-Expansion

Before returning content, check:
- **Volume**: ≥5,000 chars total (standard) / ≥15,000 (deep research)
- **Specificity**: contains numbers, named entities, dates — not just generic descriptions
- **Coverage**: all requested dimensions have ≥500 chars of relevant content
- **Diversity**: ≥3 unique domains for web searches

If any check fails: generate 2–3 targeted supplementary queries, fetch, re-check.
Max 2 supplementary rounds. If still insufficient, proceed with an honest coverage report.

---

## Step 6: Combine & Return

Structure each source:

```
## Nguồn: {source_name}
> {path_or_url} | {char_count} ký tự

{content}

---
```

Final summary: "📋 Thu thập hoàn tất: {N} nguồn / {total_chars} ký tự / {quality_assessment}"

---

## Examples

- "Đọc file report.pdf và data.xlsx" → markitdown both → combined Markdown
- "Tìm AI trends 2026, lấy top 3 kết quả" → web search → fetch 3 URLs → combined Markdown
- "Danh sách việc làm Python tại Hà Nội" → Source Intelligence → Data Collection → structured items

---

## What This Skill Does NOT Do

- Does NOT synthesize or translate content → compose
- Does NOT generate output files → gen-* skills
- Does NOT install dependencies → setup
