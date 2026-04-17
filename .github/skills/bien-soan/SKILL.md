---
name: bien-soan
description: |
  Synthesize and merge multi-source content into coherent documents.
  4 modes: standard (concise), comprehensive (3-5x richer), translation (Vietnamese↔English), summary.
  Identifies overlapping content, resolves conflicts, proposes outline before writing.
  Always use this skill when the user has multiple pieces of content to combine, wants to translate,
  wants to expand brief notes into a full document, or says things like "gộp lại", "tổng hợp nội
  dung", "dịch sang tiếng Anh/Việt", "viết lại đầy đủ hơn", "biên soạn", "synthesize",
  "merge content" — even if they don't say "/bien-soan" explicitly.
argument-hint: "[content from thu-thap or direct text] [mode: standard|comprehensive]"
version: 1.1
compatibility:
  requires:
    - Python >= 3.10
  tools:
    - run_in_terminal (for deduplicate.py)
---

# Biên Soạn — Content Synthesis Skill

**References:** `references/comprehensive-mode.md` | `references/translation-mode.md` | `references/extra-modes.md`

This skill takes raw content from multiple sources and produces a unified, coherent document.
The key challenge is merging overlapping information without losing important details or
creating contradictions. The skill proposes an outline first (so the user can adjust structure
before writing begins), then synthesizes content section by section.

Four modes: **synthesis** (default — merge sources), **comprehensive** (3-5x richer depth),
**translation** (Vietnamese↔English), and **summary** (extract key points and condense).

All responses to the user are in Vietnamese.

---

---

## Mode Selection

Detect mode from user keywords:
- **synthesis** (default): merge multiple sources into one document
- **comprehensive**: triggered by "chi tiết", "comprehensive", "đầy đủ", or `--mode=comprehensive`.
  See `references/comprehensive-mode.md` for the full spec on how to produce 3-5x richer content.
- **translation**: triggered by "dịch", "translate", "dịch sang".
  See `references/translation-mode.md` for language detection and translation workflow.
- **summary**: triggered by "tóm tắt", "summarize" — extract key points and condense.

In interactive mode, ask the user which mode they prefer. In pipeline mode, default to
standard synthesis unless tong-hop specifies otherwise.

---

## Step 1: Analyze Sources

1. For each source: identify main topics, extract key facts, detect language
2. Cross-source: identify overlapping content, flag contradictions
3. If combined input > 50,000 words → switch to chunking mode (see `references/extra-modes.md`)
4. If thin sections detected → trigger enrichment callback (see `references/extra-modes.md`)
5. **Deep research gap check** — when input comes from thu-thap's Deep Research mode
   (content has dimension headers and coverage assessment):
   - Review each dimension's coverage assessment
   - Identify dimensions marked as ⚠️ (weak coverage)
   - Check if the user's original request requires data that isn't present
   - For each critical gap, generate a specific follow-up search query
   - Report gaps back to tong-hop pipeline for supplementary thu-thap round:
     ```
     📊 Phân tích nội dung thu thập:
     - ✅ Đủ dữ liệu: {covered_dimensions}
     - ⚠️ Thiếu dữ liệu quan trọng:
       - {gap_1}: cần tìm thêm "{suggested_query_1}"
       - {gap_2}: cần tìm thêm "{suggested_query_2}"
     → Đề xuất: tìm kiếm bổ sung trước khi tổng hợp
     ```
   - If gaps are non-critical (nice-to-have, not essential), proceed without supplementary
     search and note the gaps in the output
6. Report:
   ```
   📊 Phân tích nguồn:
   - {N} nguồn, ~{total_words} từ
   - Chủ đề chính: {topics}
   - Trùng lặp: {overlap_areas}
   - Mâu thuẫn: {contradictions or "Không có"}
   ```

---

## Step 2: Propose Outline

1. Create logical section structure from combined content
2. Group related information under headings, order for narrative flow
3. Mark which sources contribute to each section
4. Present to user:
   ```
   📝 Đề xuất cấu trúc tài liệu:
   1. **{Section 1}** — từ nguồn: {sources}
   2. **{Section 2}** — từ nguồn: {sources}
   ...
   Bạn muốn điều chỉnh gì không?
   ```
5. Interactive: wait for approval or modification
6. Pipeline mode: auto-approve, proceed immediately

---

## Step 3: Synthesize Content

1. For each section: gather relevant content from all sources
2. Merge content — eliminate redundancy, create coherent narrative
3. Resolve contradictions: present both perspectives with attribution
4. Ensure smooth transitions between subsections
5. Output format: Structured Markdown (H1/H2/H3, paragraphs, bullet lists, tables, bold/italic)

For comprehensive mode (3-5x depth), see `references/comprehensive-mode.md`.
For speaker notes (when output is presentation), see `references/extra-modes.md`.

---

## Step 4: Format & Deliver

1. Apply target length: short (~500-1000 words) | medium (~1000-3000) | long (~3000-10000) | user-specified
2. Quality checks: no duplicate paragraphs, consistent headings, tables have headers, consistent language
3. Deliver:
   ```
   ✅ Biên soạn hoàn tất:
   - Cấu trúc: {N} phần, {M} phần phụ
   - Độ dài: ~{word_count} từ
   - Ngôn ngữ: {language}
   [Preview first section]
   Bạn muốn chỉnh sửa gì trước khi xuất file?
   ```

---

## Conflict Resolution

When sources disagree, the worst outcome is silently choosing one version — the user loses
information and may not realize it. Instead:

- **Data conflicts** (e.g., different numbers for the same metric): present both values with
  clear source attribution: "Theo {source_A}: X. Trong khi đó, {source_B} ghi nhận: Y."
- **Opinion conflicts**: present both perspectives fairly, without taking sides
- **Date conflicts**: use the most recent source, but note the discrepancy
- **Critical conflicts**: in interactive mode, ask the user to decide. In pipeline mode, use
  the most recent or most authoritative source.

---

## Source Attribution

Readers need to know where information came from, especially in formal reports. Apply these
rules consistently:

1. When quoting or closely paraphrasing a source, add an inline citation: "(Nguồn: {source_name})"
2. For data tables, note the source below the table
3. At the end of the document, include a "Nguồn tham khảo" (References) section listing all
   sources with their paths/URLs
4. When multiple sources agree on a fact, attribution is optional (it clutters the text)

---

## Quality Checks

Before delivering, verify:
1. No duplicate paragraphs (common when merging overlapping sources)
2. Consistent heading hierarchy (H1 → H2 → H3, no skips)
3. All tables have headers
4. Consistent language throughout (don't mix Vietnamese and English mid-paragraph)
5. Source attribution present for key claims and data points

---

## Duplicate Detection Script

Before synthesizing, run the dedup script to identify overlapping paragraphs across sources:

```bash
python3 .github/skills/bien-soan/scripts/deduplicate.py --input collected.md --threshold 0.75
```

This helps identify which paragraphs need merging vs which are unique content. The script
reports paragraph pairs with Jaccard similarity above the threshold, so you can prioritize
merging those sections. For a JSON report: add `--output dedup_report.json`.

---

## Examples

**Example 1 — Standard synthesis:**
Input: 3 sources about marketing strategy (~8,000 words total, 40% overlap)
Output: Unified document (~3,000 words), 5 sections, conflicts noted with attribution

**Example 2 — Comprehensive mode:**
Input: Brief meeting notes (~500 words) about product roadmap
Output: Comprehensive document (~2,500 words) with expanded sections, context, and analysis

**Example 3 — Translation:**
Input: Vietnamese technical document (~2,000 words)
Output: English translation preserving structure, headings, and formatting

---

## What This Skill Does NOT Do

- Does NOT read files — that's thu-thap
- Does NOT generate output files — that's tao-* skills
- Does NOT install dependencies — redirects to /cai-dat
- Does NOT search the web — delegates to thu-thap
