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

### Content Depth — Why Default Output Is Often Too Thin

The most common user complaint is that output is too short and lacks substance. This happens
because standard synthesis mode focuses on *merging* sources efficiently — eliminating
redundancy and creating concise output. But users usually want *rich* output, not concise
output. They want to learn from the document, not just see their sources compressed.

**The fix: default to "enriched" synthesis, not bare-minimum synthesis.**

When synthesizing, the goal is not to produce the shortest possible document that covers all
points. The goal is to produce a document that a reader finds **genuinely useful and
informative**. This means:

1. **Don't just summarize — explain.** For each key point, include enough context that a
   reader who hasn't seen the sources can fully understand it. If a source mentions "RAG
   architecture improved by 40%", don't just write "RAG cải thiện 40%." Write what RAG is
   (briefly), what was improved, how it was measured, and why 40% matters.

2. **Add analysis, not just facts.** After presenting facts from sources, add a paragraph
   analyzing what they mean together. What's the pattern? What's the implication? What should
   the reader take away? This is what transforms a summary into an insight document.

3. **Include supporting details and examples.** Sources often contain examples, case studies,
   specific numbers, and quotes. Don't discard these to save space — they make the document
   credible and interesting. A report that says "nhiều công ty đang áp dụng AI" is weak;
   one that says "Microsoft, Google, và Meta đã đầu tư hơn $100B vào AI trong 2024-2025,
   với Microsoft dẫn đầu ở mảng enterprise AI" is substantive.

4. **Structure creates depth.** A well-structured document with H2/H3 hierarchy, tables for
   comparisons, and bullet lists for key points naturally becomes richer because each
   structural element forces you to provide specific content.

### Content Depth Levels

tong-hop passes a `content_depth` parameter based on request analysis:

```yaml
CONTENT_DEPTH:
  standard:
    # User asks for something quick, simple, or explicitly short
    trigger: "tóm tắt", "ngắn gọn", "quick", "brief", "overview"
    target_words_per_section: 200-400
    total_target: 1000-3000 words
    approach: Concise, key points only, minimal elaboration

  enriched:
    # DEFAULT for most requests — this is the new normal
    trigger: Most requests that don't specify length
    target_words_per_section: 400-800
    total_target: 3000-8000 words
    approach: |
      Each section gets:
      - Introduction paragraph (context + why this matters)
      - Core content with specific facts, numbers, examples
      - Analysis paragraph (implications, trends, connections)
      - Key data points in tables or formatted lists

  comprehensive:
    # User explicitly wants depth, or deep research was performed
    trigger: "chi tiết", "comprehensive", "đầy đủ", or research_depth=deep
    target_words_per_section: 800-2000
    total_target: 5000-15000 words
    approach: Full comprehensive-mode.md spec (3-5x standard)
```

**Important:** when `research_depth: deep` was used (multi-round search), automatically
upgrade to `comprehensive` depth — the user invested time in deep research, so they
expect a thorough document, not a brief summary of all that research.

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

For each section in the approved outline:

1. **Introduction** (2-3 sentences): set context and explain why this section matters
   to the reader. Don't jump straight into facts — orient the reader first.

2. **Core content**: gather all relevant information from all sources for this section.
   For each key point:
   - State the fact or finding clearly
   - Include specific data: numbers, percentages, dates, names (not vague generalities)
   - Add an example or case study when available in sources
   - Attribute the source when the claim is specific or surprising

3. **Comparison tables**: when the content naturally involves comparison (products, options,
   time periods, approaches), create a Markdown table instead of writing paragraphs. Tables
   are denser and easier to scan than "Option A does X. Option B does Y." prose.

4. **Analysis paragraph** (enriched/comprehensive mode): after presenting the facts, write
   1-2 paragraphs analyzing what they mean:
   - What patterns or trends emerge across sources?
   - What are the implications for the reader?
   - What connections exist between this section and others?
   - What's the "so what?" — why should the reader care?

5. **Section key takeaways** (enriched/comprehensive mode): end each major section with
   2-3 bullet-point takeaways. This helps readers who skim and reinforces the main points.

6. Merge overlapping content — eliminate redundancy but keep specifics from each source.
   Resolve contradictions: present both perspectives with attribution.

7. Ensure smooth transitions between subsections.

8. Output format: Structured Markdown (H1/H2/H3, paragraphs, bullet lists, tables, bold/italic)

### Content Richness Checklist

Before moving to the next section, verify:
- [ ] Contains at least 2-3 specific data points (numbers, names, dates) — not just generalities
- [ ] Has at least one comparison, example, or case study
- [ ] Provides analysis (what the facts mean), not just a list of facts
- [ ] A reader who hasn't seen the sources would find this section informative on its own

If a section fails this checklist and the content depth is enriched or comprehensive, go back
and add substance. The most common failure mode is writing generic sentences like "AI đang
phát triển nhanh chóng" without any supporting specifics.

For comprehensive mode (full 3-5x depth), see `references/comprehensive-mode.md`.
For speaker notes (when output is presentation), see `references/extra-modes.md`.

---

## Step 4: Format & Deliver

1. Apply target length based on content_depth:
   - **standard**: 1000-3000 words (quick summaries, overviews)
   - **enriched**: 3000-8000 words (default — most requests)
   - **comprehensive**: 5000-15000 words (deep research, detailed reports)
   - **user-specified**: honor explicit length requests
2. Quality checks: no duplicate paragraphs, consistent headings, tables have headers, consistent language
3. **Self-review before delivery**: read through the full output and ask:
   - Would I learn something new from this document?
   - Are the claims backed by specific evidence?
   - Could I remove any section and not lose important information?
   - Does each section add something the previous one didn't?
4. Deliver:
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

**Example 1 — Enriched synthesis (new default):**
Input: 3 sources about marketing strategy (~8,000 words total, 40% overlap)
Output: Enriched document (~5,000 words), 6 sections each with intro + analysis + takeaways,
2 comparison tables, conflicts noted with attribution, references section

**Example 2 — Comprehensive mode (deep research):**
Input: Deep research output (~50,000 chars) about AI trends, 8 research dimensions
Output: Comprehensive document (~12,000 words) with executive summary, 8 detailed sections
each with data tables + analysis + case studies, conclusion with forward-looking insights

**Example 3 — Standard (quick summary):**
Input: 2 meeting notes (~1,500 words total), user says "tóm tắt ngắn gọn"
Output: Concise summary (~800 words), key decisions, action items, no elaboration

**Example 4 — Translation:**
Input: Vietnamese technical document (~2,000 words)
Output: English translation preserving structure, headings, and formatting

---

## What This Skill Does NOT Do

- Does NOT read files — that's thu-thap
- Does NOT generate output files — that's tao-* skills
- Does NOT install dependencies — redirects to /cai-dat
- Does NOT search the web — delegates to thu-thap
