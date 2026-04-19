# Requirement Anchor — Structured Requirements Schema

> **Phase 13 addition** — prevents requirement drift by extracting typed requirements
> from the raw_prompt immediately on pipeline start. Used as ground-truth for all
> auditor calls throughout the pipeline.

---

## When to Use

Copilot MUST extract structured requirements immediately after `save_state.py init` —
**before any gather/compose/gen-* step runs**. This is the ground-truth document that
every audit checkpoint will reference.

---

## Extraction Protocol

```bash
# Step 1: Save raw prompt (already done at pipeline start)
python3 scripts/save_state.py init "<user's exact request>" "<intent>"

# Step 2: Copilot analyzes raw_prompt and extracts typed requirements
# Then saves them:
python3 scripts/save_state.py extract-requirements '<json>'

# Step 3: Verify
python3 scripts/save_state.py check-requirements
```

---

## Structured Requirements Schema

```json
{
  "output_files": [
    {
      "name": "jobs.xlsx",
      "type": "excel",
      "structure_hint": "one sheet per province/city"
    },
    {
      "name": "fresher-jobs-report.pptx",
      "type": "pptx",
      "structure_hint": "10-20 slides with charts and illustrations"
    },
    {
      "name": "fresher-jobs-slide.html",
      "type": "html",
      "structure_hint": "reveal.js slide format"
    }
  ],
  "fields_required": {
    "jobs.xlsx": [
      "company_name",
      "address",
      "province_city",
      "salary_range",
      "years_experience",
      "required_skills",
      "job_detail_url",
      "company_website",
      "company_reviews",
      "review_links",
      "work_environment_rating"
    ]
  },
  "filters": [
    "only fresher/junior dev roles",
    "max 2 years experience required (or no experience requirement)",
    "Vietnam only",
    "currently open positions"
  ],
  "grouping": [
    "by province/city (one sheet per province)"
  ],
  "format_constraints": [
    "Excel: one sheet per province/city",
    "PPT: 10-20 slides with charts and illustrations",
    "HTML: slide format (reveal.js)"
  ],
  "sources": [
    "ITViec",
    "TopCV",
    "VietnamWorks",
    "LinkedIn",
    "itviec.com",
    "topcv.vn",
    "vietnamworks.com"
  ],
  "content_requirements": [
    "company name",
    "address and province",
    "salary information",
    "years of experience required",
    "required skills list",
    "job detail URL (canonical, not listing page)",
    "company website URL",
    "all available company reviews",
    "review source links",
    "work environment ranking from reviews"
  ]
}
```

---

## Extraction Rules

```yaml
EXTRACTION_RULES:

  output_files:
    how: Look for explicit output format requests in the prompt
    examples: "xuất ra file excel", "làm báo cáo thuyết trình", "tạo website dạng slide"
    rule: If multiple formats mentioned, create one entry per format

  fields_required:
    how: Look for "đầy đủ", "bao gồm", field listings, "có X, Y, Z"
    examples: "có tên cty, địa chỉ, tỉnh thành, mức lương..."
    rule: Map to output_file.name. If all outputs need same fields, use "all" as key.

  filters:
    how: Look for selection criteria, constraints on what to include/exclude
    examples: "không yêu cầu năm kinh nghiệm hoặc dưới 2 năm", "chỉ ở Việt Nam"
    rule: Each filter is a single constraint string — be specific

  grouping:
    how: Look for "phân chia theo", "mỗi X là", "nhóm theo"
    examples: "mỗi sheet là 1 tỉnh thành" → "by province/city (one sheet per province)"
    rule: Grouping determines structure — always capture explicitly

  format_constraints:
    how: Look for "định dạng", quantity hints, visual requirements
    examples: "10-20 slide", "đầy đủ hình ảnh minh họa, biểu đồ"
    rule: Combine type + constraint: "PPT: 10-20 slides with illustrations and charts"

  sources:
    how: Look for platform names, "từ X, Y, Z"
    examples: "itviec", "topcv", "vietnamworks" — even if mentioned implicitly
    rule: Include both brand name and domain if known

  content_requirements:
    how: Enumerate all information items user asked to collect per record
    rule: Each item should be atomic (one piece of data per item)
```

---

## Auditor Integration

When auditor receives output to score, it MUST receive `structured_requirements` alongside:

```python
# Conceptual auditor call:
auditor_input = {
    "output": "<path or content of generated output>",
    "requirements": state["structured_requirements"],  # from save_state.py
    "step_name": "gen-excel"
}
```

The auditor scores EACH requirement item:

```json
{
  "requirement": "one sheet per province/city",
  "score": 0,
  "pass": false,
  "reason": "Output has 1 sheet named 'unknown' — no per-province grouping"
}
```

---

## Integration with orchestrator.agent.md

After FLOW Step 2 (`save_state.py init`), orchestrator MUST call:

```bash
# Step 2b: Extract structured requirements (mandatory — do not skip)
python3 scripts/save_state.py extract-requirements '<structured_json>'
python3 scripts/save_state.py check-requirements  # verify
```

The structured JSON is produced by Copilot analyzing the raw_prompt using the
extraction rules above. This must happen BEFORE any skill is called.
