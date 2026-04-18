# InsightEngine — Copilot Compatibility Matrix & Benchmark

> **Updated:** 2026-04-18  
> **Purpose:** Track which skills work with which Copilot models, and provide reproducible test cases.

---

## Compatibility Matrix

Test each skill with 3 standardized prompts per skill. Grade: ✅ Pass | ⚠️ Partial | ❌ Fail

### Model Tier Definitions

| Tier | Models | Context | Reasoning |
|------|--------|---------|-----------|
| **Tier 1 (Strong)** | Claude Opus 4, Claude Sonnet 4, GPT-4o | 128K+ | Strong multi-step |
| **Tier 2 (Standard)** | GPT-4o-mini, Claude Haiku, Gemini Flash | 32-128K | Good single-step |
| **Tier 3 (Basic)** | GPT-3.5 Turbo, older models | 4-16K | Limited chaining |

### Skill × Model Matrix

| Skill | Tier 1 | Tier 2 | Tier 3 | Critical Steps | Known Gaps |
|-------|--------|--------|--------|----------------|------------|
| tong-hop | ✅ | ⚠️ TBD | ❌ TBD | Step 1.5 analysis, Step 3.5 trace | Tier 2 may skip HARD GATE |
| thu-thap | ✅ | ⚠️ TBD | ⚠️ TBD | Platform-specific search, field extraction | Tier 2/3 may use generic Google |
| bien-soan | ✅ | ⚠️ TBD | ⚠️ TBD | Depth gate (≥300 words/section) | Tier 2/3 produce thin content |
| tao-word | ✅ | ✅ TBD | ⚠️ TBD | python-docx script generation | Generally script-based, reliable |
| tao-excel | ✅ | ✅ TBD | ⚠️ TBD | Formula generation, recalc.py | Formulas may be wrong on Tier 3 |
| tao-slide | ✅ | ⚠️ TBD | ❌ TBD | pptxgenjs/ppt-master pipeline | Pro mode too complex for Tier 3 |
| tao-pdf | ✅ | ✅ TBD | ⚠️ TBD | reportlab script | Generally reliable |
| tao-html | ✅ | ✅ TBD | ⚠️ TBD | reveal.js template | 8 styles may confuse Tier 3 |
| tao-hinh | ✅ | ⚠️ TBD | ❌ TBD | matplotlib + diffusers | AI image gen fails without MPS |
| thiet-ke | ✅ | ⚠️ TBD | ❌ TBD | Canvas + Pillow composition | Complex layout fails on Tier 3 |
| kiem-tra | ✅ | ⚠️ TBD | ⚠️ TBD | Requirement matching | May produce superficial audit |
| cai-tien | ✅ | ⚠️ TBD | ❌ TBD | Root cause analysis | Requires strong reasoning |

> **TBD** = Not yet benchmarked with actual test runs. Update after running benchmark test cases below.

### How to Update This Matrix

1. Switch Copilot model (VS Code → Copilot settings → Model)
2. Run each benchmark test case below
3. Grade: ✅ if output meets all ACs, ⚠️ if partial, ❌ if fails
4. Update the matrix cell and add notes to Known Gaps

---

## Benchmark Test Cases

### TC-01: Research Report (tests: tong-hop → thu-thap → bien-soan → tao-word)

```yaml
prompt: "Tổng hợp về xu hướng AI Agent trong phát triển phần mềm 2025-2026, tạo báo cáo Word corporate"
expected:
  step_1_5: Shows dimension expansion with ≥4 dimensions, waits for approval
  thu_thap: ≥5 sources, ≥10K chars gathered
  bien_soan: ≥5000 words, ≥5 sections, expert-level depth
  output: output/*.docx, ≥20KB, corporate style, TOC present
  step_trace: Visible numbered trace with ✅ markers
acceptance:
  - HARD GATE enforced (waits for user approval at Step 1.5)
  - Step trace printed and updated
  - Word doc has TOC, headings, ≥5 sections
  - Content is specific (names, numbers, dates) not generic
```

### TC-02: Data Collection (tests: tong-hop → thu-thap DC mode → validate_urls → tao-excel)

```yaml
prompt: "Tìm 15 job fresher JavaScript ở HCM trên ITViec, tạo Excel có tên công ty, vị trí, lương, URL job"
expected:
  step_1_5: Shows data_collection analysis with platforms, fields, quantity
  thu_thap: Platform-specific search (site:itviec.com), ≥10 items
  url_validation: validate_urls.py runs BEFORE tao-excel, reports direct/search classification
  output: output/*.xlsx with columns: company, position, salary, direct_url, source_platform
acceptance:
  - REQUEST_TYPE detected as data_collection
  - Search uses site:itviec.com (not generic Google)
  - URLs are to individual job pages (not search results)
  - validate_urls.py runs pre-output
  - Excel has ≥10 rows with all required fields
```

### TC-03: Mixed Collection + Analysis (tests: full pipeline with chaining)

```yaml
prompt: "Tìm jobs fresher JS HCM, tạo Excel tổng hợp, rồi tạo slide phân tích và xếp hạng top 5"
expected:
  step_1_5: Shows mixed type with both collection + analysis plan
  thu_thap: Platform-specific, structured extraction
  output_1: output/*.xlsx with job data
  output_2: output/*.pptx with analysis slides
  step_trace: Shows both Excel and Slide steps
acceptance:
  - REQUEST_TYPE detected as mixed
  - Both Excel AND Slide outputs generated
  - Slide contains analysis/ranking (not just data dump)
  - Pipeline traces both output steps
```

### TC-04: HTML Presentation (tests: tong-hop → thu-thap → bien-soan → tao-html)

```yaml
prompt: "Tạo HTML presentation về Python vs JavaScript cho beginners, style dark-modern"
expected:
  step_1_5: Shows research dimensions, presentation mode detected
  output: output/*.html with reveal.js, dark-modern theme
acceptance:
  - HTML uses reveal.js
  - Dark-modern style applied
  - ≥8 slides with transitions
  - Content is educational (not just bullet points)
```

### TC-05: Resume Test (tests: session resilience)

```yaml
setup: "Run TC-01 but interrupt after thu-thap step (close chat mid-pipeline)"
prompt: "tiếp tục" (in new chat session)
expected:
  resume_check: Detects .session-state.json, shows summary
  skips: thu-thap (already completed)
  continues: From bien-soan onward
acceptance:
  - save_state.py check returns IN_PROGRESS
  - User shown summary of completed steps
  - Pipeline resumes from correct step (not restart)
```

---

## Running Benchmarks

```bash
# Quick infrastructure check first:
python3 scripts/smoke_test.py

# Then manually run each TC prompt in Copilot chat.
# After each run, record results in the matrix above.

# Automated check after pipeline completes:
python3 scripts/smoke_test.py  # Verify output files exist
ls -la output/                  # Check file sizes
```

---

## Changelog

| Date | Model | TC | Result | Notes |
|------|-------|-----|--------|-------|
| 2026-04-18 | — | — | CREATED | Initial matrix and test cases |
