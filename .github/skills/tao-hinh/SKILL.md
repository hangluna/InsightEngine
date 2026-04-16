---
name: tao-hinh
description: |
  Generate professional charts from data using matplotlib + seaborn (Agg backend).
  Supports bar, line, pie, radar, scatter charts with consistent color palettes.
  Output PNG at dpi=160 with Vietnamese label support.
  Uses bundled scripts/gen_chart.py for all chart types.
  Use when user says "tạo biểu đồ", "vẽ chart", "create chart", or "/tao-hinh".
argument-hint: "[chart type: bar|line|pie|radar|scatter] [data source: Excel/CSV/inline]"
---

# Tạo Hình — Chart & Data Visualization

Generate professional charts from data for reports and presentations.

```yaml
MODE: Script-based — uses bundled scripts/gen_chart.py via terminal
LANGUAGE: All Copilot responses in Vietnamese
OUTPUT: PNG files at dpi=160, bbox_inches='tight'
BACKEND: matplotlib with Agg (headless, no display needed)
LIBRARIES: matplotlib (charts), seaborn (enhanced styling, optional)
```

---

## Trigger Conditions

Use this skill when user:
- Says "tạo biểu đồ", "vẽ chart", "tạo chart"
- Says "create chart", "visualize data", "generate chart"
- Uses command `/tao-hinh`
- Requests data visualization for reports or presentations
- Asks to embed charts into Word/PPT (chained from tao-word/tao-slide)

---

## Supported Chart Types

```yaml
CHART_TYPES:
  bar:
    aliases: ["bar chart", "biểu đồ cột", "column chart"]
    use_for: Comparing categories, ranking, before/after
    variants: vertical, horizontal, grouped, stacked
    
  line:
    aliases: ["line chart", "biểu đồ đường", "trend chart"]
    use_for: Trends over time, continuous data, projections
    variants: single, multi-series, with markers, area fill
    
  pie:
    aliases: ["pie chart", "biểu đồ tròn", "donut chart"]
    use_for: Proportions, market share, composition
    variants: standard, donut (wedgeprops=dict(width=0.4))
    max_slices: 8 (group remaining as "Khác")
    
  radar:
    aliases: ["radar chart", "biểu đồ radar", "spider chart"]
    use_for: Multi-dimensional comparison, skill profiles, scoring
    library: matplotlib.projections polar
    close_polygon: true (append first value to end)
    
  scatter:
    aliases: ["scatter plot", "biểu đồ phân tán", "dot chart"]
    use_for: Correlation, distribution, clustering
    variants: basic, with trend line, bubble (size parameter)
```

---

## Step 1: Identify Data Source

```yaml
DATA_SOURCES:
  excel_file:
    detect: User provides .xlsx or .xlsm path
    read_with: openpyxl or pandas
    example: "vẽ chart từ file sales.xlsx"
    
  csv_file:
    detect: User provides .csv or .tsv path
    read_with: pandas.read_csv()
    example: "tạo biểu đồ từ data.csv"
    
  inline_data:
    detect: User provides data directly in message
    parse: Extract into Python dict/list
    example: "vẽ bar chart: Q1=100, Q2=150, Q3=200"
    
  previous_output:
    detect: Chained from tao-excel or other skill
    read_from: Path provided by pipeline
    example: "vẽ chart từ Excel vừa tạo"

PARSE_RULES:
  - Auto-detect header row vs data rows
  - Handle Vietnamese column names (UTF-8)
  - Convert numeric strings to float
  - Skip empty rows/columns
  - If ambiguous, ASK user which columns to use for X/Y axis
```

---

## Step 2: Configure Chart

```yaml
CONFIGURATION:
  ask_user:
    - Chart type (if not obvious from data/request)
    - Title (suggest based on data)
    - Which columns for X axis / Y axis / series
    
  auto_infer:
    - Chart type from data shape (time series → line, categories → bar)
    - Colors from palette
    - Axis labels from column headers
    - Legend position (best fit)

CHART_DEFAULTS:
  figsize: [10, 6]          # inches
  dpi: 160                   # output resolution
  bbox_inches: 'tight'       # no whitespace
  title_fontsize: 16
  label_fontsize: 12
  tick_fontsize: 10
  legend_fontsize: 10
  grid: true (alpha=0.3)
```

---

## Step 3: Generate Chart

### Primary Method — Use bundled gen_chart.py (recommended)

```yaml
SCRIPT_ARCHITECTURE:
  script: .github/skills/tao-hinh/scripts/gen_chart.py
  usage: |
    python3 .github/skills/tao-hinh/scripts/gen_chart.py \
      --input data.json --output chart.png --type bar
    # Override title:
    python3 gen_chart.py --input data.json --output out.png --type line --title "Xu hướng"
    # Scatter with trend line:
    python3 gen_chart.py --input data.json --output out.png --type scatter --trend

  json_format: |
    {
      "title": "Chart Title",
      "x_label": "X Axis Label",
      "y_label": "Y Axis Label",
      "type": "bar",           // optional — overrides --type flag
      "data": {
        "labels": ["Q1", "Q2", "Q3"],
        "series": {
          "Doanh thu": [100, 150, 200],
          "Chi phí":   [80, 90, 110]
        }
      }
    }

    // For pie: data = { "labels": [...], "values": [...] }
    // For radar: data = { "categories": [...], "series": { "Name": [...] } }
    // For scatter: data = { "x": [...], "y": [...], "label": "Series" }

  output: "✅ Saved: {path} ({size} KB, {type}, {W}×{H}px)"
  
  workflow:
    1. Copilot prepares data as JSON (from Excel/CSV/inline)
    2. Save JSON to tmp/ directory
    3. Run gen_chart.py with appropriate --type
    4. Verify output PNG exists
    5. Optionally embed into .docx/.pptx via tao-word/tao-slide chaining
```

### Alternative — Inline script (for custom/complex charts)

Use when gen_chart.py doesn't cover the specific chart variant needed.

```yaml
SCRIPT_RULES:
  - ALWAYS call matplotlib.use('Agg') BEFORE importing pyplot
  - ALWAYS plt.close() after saving to free memory
  - ALWAYS use dpi=160, bbox_inches='tight'
  - NEVER call plt.show() (headless environment)
  - For enhanced styling: import seaborn as sns; sns.set_theme(style='whitegrid')
  - Use f-strings for dynamic values
  - Handle missing data gracefully (skip NaN)

SEABORN_USAGE:
  when_to_use:
    - Distribution plots (histplot, kdeplot, boxplot, violinplot)
    - Heatmaps (sns.heatmap)
    - Statistical regression (sns.lmplot, sns.regplot)
    - Pair plots for multi-variable analysis
  setup: |
    import seaborn as sns
    sns.set_theme(style='whitegrid', palette=PALETTE)
  note: seaborn is already installed per tech-stack requirements
```

---

## Color Palette

```yaml
PROFESSIONAL_PALETTE:
  primary:
    - '#2563EB'   # Blue
    - '#DC2626'   # Red
    - '#059669'   # Green
    - '#D97706'   # Amber
    - '#7C3AED'   # Purple
    - '#DB2777'   # Pink
    - '#0891B2'   # Cyan
    - '#65A30D'   # Lime

  background: '#FFFFFF'
  grid_color: '#E5E7EB'
  text_color: '#1F2937'
  
  usage_rules:
    - Use colors in order for consistency across charts in same document
    - Maintain same color→series mapping across related charts
    - For single-series charts, use primary[0] (blue)
    - For emphasis, use primary[1] (red) to highlight key data point
    
  COPILOT_MUST:
    - Pass palette as parameter, NOT hardcode in each chart
    - When generating multiple charts for same document, track color assignments
    - Apply same palette to all charts in a chain
```

---

## Step 4: Execute & Verify

```yaml
EXECUTION:
  1. Write Python script to tmp/ or scripts/ directory
  2. Run via: python3 <script_path>
  3. Check output file exists and has reasonable size (>1KB for charts)
  4. Report: file path, dimensions, file size

VERIFICATION:
  checks:
    - File exists at expected path
    - File size > 1KB (not empty/corrupt)
    - No error output from script
  on_error:
    - Show full error traceback
    - Common fixes: missing font → fallback to DejaVu Sans
    - Data type mismatch → add type conversion
    - Memory error → reduce figure size or data points
```

---

## Step 5: Embed in Documents (Chain Support)

```yaml
EMBEDDING:
  word_docx:
    method: python-docx add_picture()
    code: |
      from docx.shared import Inches
      doc.add_picture(chart_path, width=Inches(6.0))
    called_by: tao-word skill via chaining
    
  powerpoint_pptx:
    method: pptxgenjs addImage()
    code: |
      slide.addImage({
        path: chartPath,
        x: 0.5, y: 1.5, w: 9.0, h: 5.0
      });
    called_by: tao-slide skill via chaining
    
  html:
    method: Base64 inline embed
    code: |
      import base64
      with open(chart_path, 'rb') as f:
          b64 = base64.b64encode(f.read()).decode()
      img_tag = f'<img src="data:image/png;base64,{b64}" />'
    called_by: tao-html skill via chaining

CHAIN_OUTPUT:
  - Return dict: { path: str, width_px: int, height_px: int, chart_type: str }
  - Caller skill uses path to embed
  - Multiple charts returned as list of dicts
```

---

## Chart-Specific Templates

### Bar Chart

```python
fig, ax = plt.subplots(figsize=(10, 6))
colors = PALETTE[:len(categories)]
bars = ax.bar(categories, values, color=colors, width=0.6, edgecolor='white')

# Value labels on bars
for bar, val in zip(bars, values):
    ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + margin,
            f'{val:,.0f}', ha='center', va='bottom', fontsize=10)

ax.set_title(title, fontsize=16, fontweight='bold', pad=15)
ax.set_ylabel(y_label, fontsize=12)
ax.grid(axis='y', alpha=0.3)
ax.spines[['top', 'right']].set_visible(False)
```

### Line Chart

```python
fig, ax = plt.subplots(figsize=(10, 6))
for i, (series_name, series_data) in enumerate(series.items()):
    ax.plot(x_values, series_data, color=PALETTE[i],
            linewidth=2, marker='o', markersize=5, label=series_name)

ax.set_title(title, fontsize=16, fontweight='bold', pad=15)
ax.legend(loc='best', fontsize=10)
ax.grid(alpha=0.3)
ax.spines[['top', 'right']].set_visible(False)
```

### Pie Chart

```python
fig, ax = plt.subplots(figsize=(8, 8))
colors = PALETTE[:len(labels)]
wedges, texts, autotexts = ax.pie(
    values, labels=labels, colors=colors,
    autopct='%1.1f%%', startangle=90, pctdistance=0.75,
    textprops={'fontsize': 11}
)
ax.set_title(title, fontsize=16, fontweight='bold', pad=20)
```

### Radar Chart

```python
angles = np.linspace(0, 2*np.pi, len(categories), endpoint=False).tolist()
values_closed = values + [values[0]]  # close polygon
angles_closed = angles + [angles[0]]

fig, ax = plt.subplots(figsize=(8, 8), subplot_kw=dict(polar=True))
ax.fill(angles_closed, values_closed, color=PALETTE[0], alpha=0.25)
ax.plot(angles_closed, values_closed, color=PALETTE[0], linewidth=2)
ax.set_xticks(angles)
ax.set_xticklabels(categories, fontsize=11)
ax.set_title(title, fontsize=16, fontweight='bold', pad=20)
```

### Scatter Plot

```python
fig, ax = plt.subplots(figsize=(10, 6))
ax.scatter(x_values, y_values, color=PALETTE[0], s=60, alpha=0.7, edgecolors='white')

# Optional trend line
if show_trend:
    z = np.polyfit(x_values, y_values, 1)
    p = np.poly1d(z)
    ax.plot(sorted(x_values), p(sorted(x_values)),
            color=PALETTE[1], linewidth=2, linestyle='--', label='Trend')

ax.set_title(title, fontsize=16, fontweight='bold', pad=15)
ax.set_xlabel(x_label, fontsize=12)
ax.set_ylabel(y_label, fontsize=12)
ax.grid(alpha=0.3)
```

---

## Image Generation Mode (Apple Silicon Only) — US-3.1.2

Basic text-to-image generation using SD-Turbo on Apple Silicon MPS.
This is an **optional, basic** capability for simple illustrations.

> **Need more?** For advanced image generation (image-to-image restyling, portrait with face
> preservation, IP-Adapter, FaceID), use the `gen-image` skill from a-z-copilot-flow instead.
> `tao-hinh` only covers basic t2i for inline illustrations.

```yaml
AVAILABILITY_CHECK:
  script: |
    import platform, sys
    if platform.machine() != 'arm64' or platform.system() != 'Darwin':
        print("⚠️ Tạo hình ảnh chỉ hỗ trợ trên Apple Silicon Mac.")
        print("Bạn vẫn có thể dùng chức năng tạo biểu đồ (chart).")
        sys.exit(1)
    import torch
    if not torch.backends.mps.is_available():
        print("⚠️ MPS backend không khả dụng. Cần macOS 12.3+.")
        sys.exit(1)
    print("✅ Apple Silicon + MPS sẵn sàng.")

REQUIREMENTS:
  - torch (with MPS support, macOS 12.3+)
  - diffusers
  - transformers
  - accelerate
  install: pip3 install --user torch diffusers transformers accelerate
```

### Style Presets

```yaml
STYLE_PRESETS:
  flat-icon:
    prompt_suffix: "flat design icon, simple shapes, solid colors, no text, white background"
    size: [512, 512]
    use_for: App icons, UI icons, logos

  dark-tech:
    prompt_suffix: "dark technology background, neon glow, cyberpunk aesthetic, no text"
    size: [768, 768]
    use_for: Tech presentations, dark-themed slides

  cartoon:
    prompt_suffix: "cartoon illustration style, vibrant colors, clean lines, no text"
    size: [768, 768]
    use_for: Training materials, fun presentations

  minimal:
    prompt_suffix: "minimalist illustration, clean lines, muted colors, lots of whitespace, no text"
    size: [512, 512]
    use_for: Clean docs, subtle illustrations

  watercolor:
    prompt_suffix: "watercolor painting style, soft colors, artistic, no text"
    size: [768, 768]
    use_for: Creative presentations, artistic reports

  realistic:
    prompt_suffix: "photorealistic, high quality, detailed, professional photography, no text"
    size: [768, 768]
    use_for: Business presentations, professional docs
```

### SD-Turbo Configuration

```yaml
SD_TURBO:
  model: "stabilityai/sd-turbo"
  settings:
    guidance_scale: 0.0
    num_inference_steps: 4
    device: "mps"
    dtype: torch.float16

  script_template: |
    import torch
    from diffusers import AutoPipelineForText2Image

    pipe = AutoPipelineForText2Image.from_pretrained(
        "stabilityai/sd-turbo",
        torch_dtype=torch.float16,
        variant="fp16"
    )
    pipe = pipe.to("mps")

    prompt = "{user_prompt}, {style_suffix}"
    image = pipe(
        prompt=prompt,
        guidance_scale=0.0,
        num_inference_steps=4,
        width={width},
        height={height}
    ).images[0]

    image.save("{output_path}")
    print(f"Image saved: {output_path} ({width}x{height})")

  RULES:
    - NEVER include text rendering in prompts (SD cannot render text reliably)
    - Always append "no text, no letters, no words" to prompts
    - Model auto-downloads on first use (~2GB) to ~/.cache/huggingface/
    - Use torch.float16 for memory efficiency on MPS
    - Output minimum 512x512; 768x768 for presentation images
```

### Image Generation Workflow

```yaml
WORKFLOW:
  1_CHECK: Verify Apple Silicon + MPS available (exit gracefully if not)
  2_PROMPT: Build prompt from user description + style preset suffix
  3_GENERATE: Run SD-Turbo pipeline (4 steps, ~5 seconds on M1/M2)
  4_SAVE: Save to output path as PNG
  5_REPORT: Print path, dimensions, file size
  
  on_non_apple:
    message: |
      ⚠️ Chức năng tạo hình ảnh từ prompt chỉ hỗ trợ trên Apple Silicon Mac.
      Bạn vẫn có thể sử dụng chức năng tạo biểu đồ (bar, line, pie, radar, scatter).
    action: Skip image generation, suggest alternatives (stock photos, manual design)
```

---

## Output Conventions

```yaml
FILE_NAMING:
  charts:
    pattern: "{name}_{chart_type}_{timestamp}.png"
    examples:
      - "sales_bar_20260416.png"
      - "revenue_line_20260416.png"
  images:
    pattern: "{name}_{style}_{timestamp}.png"
    examples:
      - "hero_dark-tech_20260416.png"
      - "icon_flat-icon_20260416.png"
  directory: Same as source data, or user-specified, or tmp/

QUALITY:
  charts:
    dpi: 160
    format: PNG (default), SVG (if user requests vector)
    background: White (#FFFFFF)
    no_extra_whitespace: bbox_inches='tight'
  images:
    min_size: 512x512
    presentation_size: 768x768
    format: PNG
```

---

## What This Skill Does NOT Do

- Does NOT display charts interactively (headless only, Agg backend)
- Does NOT render text inside generated images (SD limitation)
- Does NOT modify source data files
- Does NOT install dependencies — assumes already installed (see /cai-dat)
- Does NOT use plt.show() — always saves to file
- Does NOT attempt image generation on non-Apple Silicon (graceful skip)
