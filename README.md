# InsightEngine

Pipeline tổng hợp nội dung đa nguồn → đa định dạng đầu ra.

Transform scattered information from documents, spreadsheets, web content, and other sources into structured reports, presentations, charts, and more — all orchestrated by AI skills.

## Skills

| Skill | Purpose | Command |
|-------|---------|---------|
| **tong-hop** | Pipeline orchestrator — analyzes intent, coordinates sub-skills | `/tong-hop` |
| **thu-thap** | Gather content from files, URLs, web search | `/thu-thap` |
| **bien-soan** | Synthesize, merge, translate (Vi↔En), chunk large docs | `/bien-soan` |
| **tao-word** | Create professional Word (.docx) with 3 style templates | `/tao-word` |
| **tao-excel** | Create Excel (.xlsx) with formulas, formatting, recalc | `/tao-excel` |
| **tao-slide** | Create PowerPoint (.pptx) with 5 style templates | `/tao-slide` |
| **tao-pdf** | Create PDF with reportlab, Vietnamese font support | `/tao-pdf` |
| **tao-html** | Create static HTML pages with 5 style templates | `/tao-html` |
| **tao-hinh** | Charts (matplotlib) + image generation (Apple Silicon) | `/tao-hinh` |
| **cai-dat** | Install/verify dependencies | `/cai-dat` |

## Pipeline Flow

```
User Request → tong-hop (orchestrator)
  ├─ thu-thap (gather from files/URLs/web)
  ├─ bien-soan (synthesize + translate)
  └─ tao-[format] (output)
       ├─ tao-word (.docx)
       ├─ tao-excel (.xlsx)
       ├─ tao-slide (.pptx)
       ├─ tao-pdf (.pdf)
       ├─ tao-html (.html)
       └─ tao-hinh (charts/images → PNG)
```

## Template Styles

5 styles available for slides and HTML:

| Style | Vibe | Best For |
|-------|------|----------|
| **corporate** | Blue accent, professional | Business reports, formal docs |
| **academic** | Serif, structured | Research papers, thesis |
| **minimal** | Whitespace, clean | Quick summaries, clean docs |
| **dark-modern** | Dark bg, neon accents | Tech talks, startup pitches |
| **creative** | Vibrant gradients, playful | Marketing, events, workshops |

## Key Features

- **Output Chaining**: Pipeline multiple outputs (e.g., Excel → Chart → PPT)
- **Large Document Chunking**: Process documents >50,000 words via chunking
- **Translation**: Vietnamese ↔ English with quality checks
- **Web Search**: Integrated Google search via Copilot tools
- **Chart Generation**: Bar, line, pie, radar, scatter with consistent palette
- **Image Generation**: Text-to-image with SD-Turbo on Apple Silicon (optional)
- **Progress UX**: Step-by-step Vietnamese progress messages, time estimates, style suggestions

## Tech Stack

| Component | Library |
|-----------|---------|
| File reading | markitdown[all] |
| Word output | python-docx |
| Excel output | openpyxl + pandas |
| PPT output | pptxgenjs (Node.js) |
| PDF output | reportlab + pypdf |
| HTML output | jinja2 + inline CSS |
| Charts | matplotlib + seaborn |
| Images | diffusers + torch/MPS (Apple Silicon) |
| Web search | vscode-websearchforcopilot_webSearch |

## Getting Started

1. Open this repo in VS Code with GitHub Copilot
2. Run `/cai-dat` to install dependencies
3. Run `/tong-hop` and describe what you need in Vietnamese or English

## License

MIT
