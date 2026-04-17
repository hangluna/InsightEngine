---
name: thu-thap
description: |
  Gather content from any source: local files (docx/xlsx/pdf/pptx/txt), URLs, and web search.
  Uses markitdown as primary reader with format-specific fallbacks for garbled output.
  Web search via vscode-websearchforcopilot_webSearch for online research.
  Always use this skill when the user mentions any file to read, URL to fetch, or topic to search
  online — even casual requests like "đọc file này", "lấy thông tin từ trang web đó", "tìm hiểu
  về X", "search Google giúp tôi", or when a file path or URL is dropped into the chat, even
  without saying "/thu-thap".
argument-hint: "[file paths or URLs]"
version: 1.1
compatibility:
  requires:
    - Python >= 3.10
    - markitdown[all]
    - httpx, beautifulsoup4 (URL fallback)
  tools:
    - run_in_terminal
    - fetch_webpage (primary URL reader)
    - vscode-websearchforcopilot_webSearch (web search)
---

# Thu Thập — Content Gathering Skill

**References:** `references/code-patterns.md` | `references/web-search-enrichment.md`

This skill reads content from any source — local files, URLs, or web search — and returns
clean Markdown text. It runs in two contexts: standalone (user asks to read something) or as
the first step in the tong-hop pipeline. The key design choice is "markitdown first, fallback
second" — markitdown handles most formats well, and format-specific readers only kick in when
markitdown produces garbled or empty output.

All responses to the user are in Vietnamese.

---

---

## Supported Formats

```yaml
LOCAL_FILES:
  primary_reader: markitdown
  supported: .docx, .xlsx, .pdf, .pptx, .txt, .md, .csv, .html, .jpg, .png

URLS:
  primary: Copilot fetch_webpage tool
  secondary: httpx + beautifulsoup4 (fallback)

WEB_SEARCH:
  tool: vscode-websearchforcopilot_webSearch
  trigger: No files/URLs provided OR user says "tìm kiếm về..."
  see: references/web-search-enrichment.md
```

---

## Step 1: Identify Sources

1. Extract file paths from user request (absolute or relative)
2. Extract URLs (http:// or https://)
3. Detect if web search is needed (no specific sources given)
4. Validate: check each file exists and format is supported; validate URL format
5. Report:
   ```
   📂 Nguồn dữ liệu:
   - File: {N} file ({formats})
   - URL: {M} đường dẫn
   - Tìm kiếm web: "{query}" → {K} kết quả
   ```

---

## Step 2: Read Local Files

For each file:
1. Check file size first — skip files larger than 50 MB with a warning (large files exhaust
   context and slow processing; the user can split them or provide specific pages/sheets)
2. Try markitdown first (see `references/code-patterns.md`)
3. If output < 100 chars → use format-specific fallback reader
4. Report: "  ✅ {filename} — {char_count} ký tự ({format})"
5. On error: "  ❌ {filename} — Lỗi: {error_message}" → skip file, continue with others

---

## Step 3: Fetch URL Content

For each URL:
1. Use `fetch_webpage` tool with `query: "main content"` — set a 30-second mental timeout:
   if fetch_webpage hangs or returns nothing after ~30s, fall back to httpx immediately
   rather than waiting indefinitely (unresponsive servers should not block the whole pipeline)
2. If unavailable or empty → use httpx + BeautifulSoup fallback (with `timeout=15` seconds)
3. Clean content: remove nav/footer/cookie boilerplate, limit to 50,000 chars
4. Report: "  ✅ {page_title} ({url_domain}) — {char_count} ký tự"
5. Rate limiting: when fetching multiple URLs, pause briefly between requests to avoid
   triggering rate limits on the same domain

For error messages and URL error types, see `references/code-patterns.md`.

For web search workflow, see `references/web-search-enrichment.md`.

---

## Step 4: Combine & Return

1. Structure each source as:
   ```
   ## Nguồn: {source_name}
   > File: {path_or_url}
   > Kích thước: {char_count} ký tự

   {extracted_content}

   ---
   ```
2. Return combined Markdown to pipeline OR show summary to user:
   ```
   📋 Thu thập hoàn tất:
   - Tổng cộng: {total_sources} nguồn
   - Thành công: {success_count}, Lỗi: {error_count}
   - Tổng nội dung: {total_chars} ký tự (~{total_words} từ)
   ```

---

## CLI Script (Recommended for batch sources)

```yaml
SCRIPT: scripts/gather.py
USAGE: |
  python3 scripts/gather.py --files doc.pdf report.docx --output collected.md
  python3 scripts/gather.py --urls "https://example.com" --output collected.md
  python3 scripts/gather.py --sources sources.json --output collected.md
JSON_FORMAT: |
  {"files": ["a.pdf", "b.docx"], "urls": ["https://example.com"]}
OUTPUT: Combined Markdown file with source headers
```

Use gather.py when processing multiple files or URLs in batch. For single files, direct
markitdown or fetch_webpage is simpler. The script handles markitdown-first-fallback-second
logic, URL rate limiting, and structured output automatically.

---

## Examples

**Example 1:**
Input: "Đọc 2 file: input/report.pdf và input/data.xlsx"
Output: Combined Markdown (~5,000 ký tự) with source headers, tables preserved from Excel

**Example 2:**
Input: "Tìm kiếm về 'machine learning trends 2026' rồi lấy nội dung top 3 kết quả"
Output: Web search → fetch 3 URLs → Combined Markdown (~15,000 ký tự) with source attribution

**Example 3:**
Input: URL "https://example.com/blog/ai-report" dropped into chat
Output: Fetched page content → cleaned Markdown (~3,000 ký tự), nav/footer removed

---

## What This Skill Does NOT Do

- Does NOT synthesize or merge content — that's bien-soan
- Does NOT translate content — that's bien-soan
- Does NOT generate output files — that's tao-* skills
- Does NOT install dependencies — redirects to /cai-dat
