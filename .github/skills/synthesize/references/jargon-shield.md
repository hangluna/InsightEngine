# Jargon Shield — Reference

## Overview

This reference defines how InsightEngine communicates with users.
The golden rule: **users see business outcomes, not technical machinery.**

Jargon shield filters outgoing messages from Copilot to the user.
Applied by: `orchestrator.agent.md`, `synthesize/SKILL.md`, all gen-* skills.

---

## Blocklist — Technical Terms to Rewrite

When composing messages TO the user, replace these technical terms:

```yaml
BLOCKLIST:
  # Libraries / code
  "openpyxl":           "Excel generator"
  "python-docx":        "Word generator"
  "reportlab":          "PDF generator"
  "pptxgenjs":          "slide generator"
  "ppt-master":         "slide generator"
  "markitdown":         "file reader"
  "diffusers":          "image generator"
  "matplotlib":         "chart generator"
  "pandas":             "data processor"
  "BeautifulSoup":      "web parser"
  "Playwright":         "web fetcher"
  "httpx":              "web fetcher"
  "Jinja2":             "HTML template engine"
  "pip3 install":       "install dependencies"
  "import error":       "cài đặt chưa hoàn tất"
  
  # Technical commands
  "scripts/recalc.py":  "recalculate Excel formulas"
  "scripts/check_deps.py": "dependency check"
  "save_state.py":      "save progress"
  "tmp/":               "working folder"
  
  # Architecture jargon
  "chunking":           "phân đoạn dữ liệu"
  "embedding":          "vector encoding"
  "semantic search":    "tìm kiếm thông minh"
  "MPS backend":        "Apple Silicon acceleration"
  "Agg backend":        "chart rendering"
  "seed queries":       "search queries"
  "API endpoint":       "web service"
  "batch processing":   "xử lý theo lô"
  "retry logic":        "thử lại tự động"
  "fallback":           "phương án dự phòng"
  "schema":             "cấu trúc dữ liệu"
  
  # Git / pipeline internals
  "git commit":         "lưu thay đổi"
  "merge --no-ff":      "merge"
  "push origin":        "đẩy lên server"
  "branch":             "nhánh"
  
  # Skill system internals
  "SKILL.md":           "cấu hình pipeline"
  "agent.md":           "module AI"
  "orchestrator":       "pipeline manager"
  "strategist":         "workflow planner"
  "auditor":            "quality checker"
  
  # File/format abbreviations
  ".docx":              "file Word"
  ".xlsx":              "file Excel"
  ".pptx":              "file PowerPoint"
  ".pdf":               "file PDF"
  ".html":              "trang web"
  ".png":               "hình ảnh"
```

---

## Translation Patterns

Replace English technical phrases with natural Vietnamese:

```yaml
PATTERNS:
  output_delivery:
    BAD:  "Output generated at output/report.docx (45.2 KB)"
    GOOD: "✅ Đã tạo xong: output/report.docx (45 KB)"
    
  step_update:
    BAD:  "Running gen-word skill with corporate template..."
    GOOD: "📄 Đang tạo file Word..."
    
  error_message:
    BAD:  "ModuleNotFoundError: No module named 'openpyxl'"
    GOOD: "⚠️ Một số công cụ chưa được cài đặt. Gõ 'setup' để cài tự động."
    
  progress_update:
    BAD:  "Gathering from 3 URLs with httpx, fallback to Playwright..."
    GOOD: "🔍 Đang thu thập từ 3 nguồn..."
    
  retry_message:
    BAD:  "httpx failed, retrying with Playwright stealth mode..."
    GOOD: "⚠️ Thử lại nguồn 2 (1/2)..."
    
  completion:
    BAD:  "Pipeline completed. Files saved to output/. Auditor score: 87/100."
    GOOD: "✅ Hoàn thành! File đã lưu tại output/. Chất lượng: tốt."
```

---

## Message Composition Rules

```yaml
RULES:
  tone:
    - Friendly, natural Vietnamese
    - Outcome-focused (what user GETS, not HOW it was made)
    - Short (1-2 sentences per update)
    
  structure:
    - Emoji prefix for visual scanning
    - Action verb in present tense: "Đang tạo...", "Đã hoàn thành..."
    - Include result size/count when available: "(45 KB)", "(12 trang)"
    
  NEVER_SAY:
    - Library names (openpyxl, pptxgenjs, etc.)
    - Script paths (scripts/recalc.py, tmp/.session-state.json)
    - Architecture terms (orchestrator, auditor, strategist)
    - Error stack traces — translate to plain Vietnamese
    - Git commands or branch names
    
  ALWAYS_SAY:
    - What step is in progress
    - What result was produced
    - File path + size on completion
```

---

## Application

All outgoing messages must pass through this shield:

```
[Copilot generates technical message]
       ↓
[Apply BLOCKLIST substitutions]
       ↓
[Apply PATTERNS for common phrases]
       ↓
[Check RULES: tone, no jargon]
       ↓
[Deliver clean message to user]
```

This reference is consulted automatically by orchestrator and all skills when
composing ANY message visible to the user.
