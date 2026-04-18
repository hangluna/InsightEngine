# InsightEngine

Multi-source content synthesis pipeline → multi-format output, running entirely in VS Code with GitHub Copilot.

> **🔄 Forked this repo?** Click **Sync fork → Update branch** in your GitHub repo, then tell Copilot: `setup InsightEngine`

---

## What is InsightEngine?

**InsightEngine is an action workflow — not an AI chat.** Every request triggers an automated pipeline: gather data → synthesize content → generate files → quality check → deliver results. You just describe what you want.

Unlike a chatbot, InsightEngine executes multi-step workflows automatically:
- Researches topics online or reads your files
- Synthesizes and structures the content
- Generates professional documents (Word, Excel, PowerPoint, PDF, HTML, charts)
- Self-reviews quality (100-point audit) and fixes weak sections before delivery

---

## Getting Started

### Option A — GitHub Codespaces (no installation, runs in browser)

> **Best for trying it out.** GitHub provides [60 free Codespace hours](https://docs.github.com/en/billing/concepts/product-billing/github-codespaces) per month. **Stop the codespace when you're done** to avoid exceeding quota.

**Step 1 — Fork the repo**

Go to https://github.com/markxLee/InsightEngine and click **Fork**.

**Step 2 — Create a Codespace**

In your forked repo, click **Code → Codespaces → Create codespace on main**. Wait a few minutes for it to start.

**Step 3 — Install the GitHub Copilot extension**

Click the **Extensions** icon in the sidebar, search for **"copilot"**, select **GitHub Copilot**, and click **Install**. Sign in to GitHub if prompted.

**Step 4 — Use InsightEngine**

> ⏱️ **First time:** Setup installs Python/Node.js libraries, taking about **2–3 minutes**. One-time only.
>
> ⚡ **After that:** Restart the codespace and you're ready — no reinstall needed.

Open Copilot Chat (Ctrl+Alt+I or the chat icon in the sidebar) and type:

```
setup InsightEngine
```

Once dependencies are installed, try:

```
research AI trends in 2025 and create a Word report in corporate style
```

**Step 5 — Stop the Codespace when done** ⚠️

In your GitHub repo, click **Code → Codespaces**, click `...` next to your codespace, and select **Stop codespace**.

---

### Option B — VS Code Local (recommended for regular use)

```bash
git clone https://github.com/<your-username>/InsightEngine
cd InsightEngine
code .
```

Open Copilot Chat and type `setup InsightEngine` to install dependencies.

> **Note:** Image generation with Stable Diffusion works best on Apple Silicon (M1/M2/M3). All other features work on any machine.

---

### Optional: Upgrade Copilot

GitHub Copilot Free has monthly request limits. For premium models (Claude Sonnet, GPT-4o) and unlimited usage:

👉 https://github.com/settings/copilot/features

---

## Usage Guide

> **InsightEngine is an action workflow.** Each request triggers a full pipeline automatically — no commands to memorize, no setup per request.

### 1. Just describe what you want

The pipeline classifies your intent and chooses the right workflow. You don't need to know how it works.

**Sample prompts — Research & reports:**
```
research AI trends in 2025 and create a Word report in corporate style
```
```
analyze the Southeast Asia fintech market, compare the top 5 companies, 
and create a dark-modern PowerPoint deck with 15 slides
```
```
gather all major LLMs from 2023 to now — benchmarks, developers, costs — 
and make a comprehensive comparison report
```

**Sample prompts — Reading files:**
```
read input/meeting-notes.docx and summarize as an email
```
```
read all files in the input/ folder and merge into a single report
```
```
read the Q4 financial report in input/ and create an Excel dashboard with charts
```

**Sample prompts — Quick creation:**
```
create a beginner-friendly blockchain presentation, 10 slides, minimal style
```
```
create an Excel table of Q1–Q4 revenue figures with a line chart
```
```
design a certificate for the AI Workshop on April 20 — leave the name field blank
```

**Sample prompts — Advanced chaining:**
```
research AI in education, compile data into an Excel file, 
then use those numbers to build a 15-slide academic presentation
```
```
read input/product-roadmap.pdf, analyze it, and create both a Word report 
and an executive summary slide deck
```

The pipeline shows an **execution plan** before running — you can review, adjust, or add details.

---

### 2. Want longer, more detailed output? Say so in the prompt

Default output is moderate length (~3,000–5,000 words). For deeper documents:

| You want | Add these keywords | Result |
|----------|-------------------|--------|
| Quick summary | `"brief"`, `"overview"`, `"concise"` | ~1,000–2,000 words |
| Standard report | *(default)* | ~3,000–5,000 words |
| Deep analysis | `"detailed"`, `"comprehensive"`, `"in-depth"` | ~8,000–15,000 words |

---

### 3. Want thorough research? Describe multiple dimensions

The pipeline auto-activates **deep research** when it detects complex requests:
- **Comparisons** ("compare A and B", "categorize all types of...")
- **Time spans** ("from 2023 to present")
- **Completeness** ("all models", "entire market")

**Example:**
```
comprehensive overview of all major AI models from 2023 to present — 
compare benchmarks, developers, and real-world applications — 
create a dark-modern slide deck
```

---

### 4. Choose a visual style

Append a style name to control the look of slides and HTML:

| Style | Best for |
|-------|---------|
| `corporate` | Business reports, formal documents |
| `academic` | Research, thesis, conference talks |
| `minimal` | Quick summaries, clean presentations |
| `dark-modern` | Tech talks, startups, engineering |
| `creative` | Marketing, events, workshops |

If no style is specified, the pipeline picks the most appropriate one.

---

### 5. Chain multiple outputs

InsightEngine supports **output chaining** — generate linked files in one request:

```
read input/sales_data.xlsx, create bar and line charts, 
then embed them in a corporate Word report
```
```
research AI trends 2025, build an Excel summary with key figures, 
then use those figures to create a 15-slide presentation
```

---

### 6. Provide input files

Place files to process in the `input/` folder. Supported: Word, PDF, Excel, PowerPoint, Text, Markdown, URLs, web search.

```
read all files in input/ and synthesize into a single comprehensive report
```

---

### 7. Quality is checked automatically

The pipeline scores output (100-point scale) before delivery. If it falls short, it automatically rewrites weak sections.

To request a manual audit:
```
verify the output against my original requirements
```

---

### 8. Auto-improving pipeline

InsightEngine improves over time. After a work session, trigger a **retrospective** to analyze what could be better:

```
improve the pipeline based on this session
```

The pipeline will:
1. Analyze the entire session (input → process → output → gaps)
2. Identify root causes of any issues
3. Propose targeted improvements to specific skills/agents
4. Create or update skills automatically if needed
5. Verify that improvements are effective

New skills and improvements are saved to `.github/skills/` and applied immediately in the next session — no deployment or restart required.

---

### 9. Resume from where you left off

If a pipeline is interrupted (context limit, session change), state is saved automatically. Just say:
```
continue
```

The pipeline resumes from the interrupted step — no need to start over.

---

## Architecture

```
User Request → orchestrator (central agent)
  ├─ Classify intent (synthesis / research / creation / design / data)
  ├─ Generate workflow plan
  ├─ Gather data (files, URLs, web search)
  ├─ Synthesize & structure content
  ├─ Generate files (Word / Excel / Slides / PDF / HTML / Chart / Image)
  ├─ Quality audit (100-point scoring)
  └─ Deliver results
```

---

## Tech Stack

| Component | Library |
|-----------|---------|
| File reading | `markitdown[all]` (Word, PDF, Excel, PPT, TXT, MD) |
| Word output | `python-docx` (3 style templates: corporate, academic, minimal) |
| Excel output | `openpyxl` + `pandas` (formulas, charts, formatting) |
| PPT output (Quick) | `pptxgenjs` (Node.js, 10 templates) |
| PPT output (Pro) | `ppt-master` SVG→PPTX (20+ layouts, 50+ charts, 6700+ icons) |
| PDF output | `reportlab` + `pypdf` (Vietnamese font support) |
| HTML output | `jinja2` + inline CSS (8 styles) |
| Charts | `matplotlib` + `seaborn` (bar, line, pie, radar, scatter) |
| Visual design | `reportlab` Canvas + `Pillow` (posters, certificates, covers, infographics) |
| Image generation | `diffusers` + `torch/MPS` (Apple Silicon, SD-Turbo) |
| Web search | `vscode-websearchforcopilot_webSearch` |
| URL fetch | Copilot `fetch_webpage` (with Playwright fallback for JS-heavy sites) |

---

## Self-Improvement Mechanism

InsightEngine uses a built-in continuous improvement loop:

1. **Runtime gap detection** — the orchestrator identifies when no existing skill handles a request well
2. **Automatic skill creation** — creates a new skill on-the-fly via `skill-creator`
3. **Session retrospective** — the `improve` skill analyzes session quality and proposes targeted fixes
4. **Iterative refinement** — `skill-forge` grades improvements on 6 criteria (A/B/C/D) and iterates until all reach grade A
5. **Persistent updates** — all improvements are committed to `.github/skills/` and take effect immediately

This means InsightEngine gets better the more you use it — without any manual configuration.

---

## License

MIT
