---
name: tao-hinh
description: |
  Generate professional charts from data using matplotlib (Agg backend).
  Supports bar, line, pie, radar, scatter charts with consistent color palettes.
  Output PNG at dpi=160 with Vietnamese label support.
  Use when user says "tạo biểu đồ", "vẽ chart", "create chart", or "/tao-hinh".
argument-hint: "[chart type] [data source: Excel/CSV/inline]"
---

# Tạo Hình — Chart & Data Visualization

Generate professional charts from data for reports and presentations.

```yaml
MODE: Script-based — generates Python script, runs via terminal
LANGUAGE: All Copilot responses in Vietnamese
OUTPUT: PNG files at dpi=160, bbox_inches='tight'
BACKEND: matplotlib with Agg (headless, no display needed)
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

## Step 3: Generate Chart Script

```yaml
SCRIPT_TEMPLATE:
  ALWAYS_START_WITH: |
    import matplotlib
    matplotlib.use('Agg')  # MUST be before any other matplotlib import
    import matplotlib.pyplot as plt
    import matplotlib.ticker as mticker
    import numpy as np

  FONT_HANDLING:
    vietnamese: |
      # Vietnamese font support
      plt.rcParams['font.family'] = 'sans-serif'
      plt.rcParams['font.sans-serif'] = ['Arial', 'Helvetica', 'DejaVu Sans']
      plt.rcParams['axes.unicode_minus'] = False

  SAVE_PATTERN: |
    plt.savefig(output_path, dpi=160, bbox_inches='tight',
                facecolor='white', edgecolor='none')
    plt.close()
    print(f"Chart saved: {output_path}")

SCRIPT_RULES:
  - ALWAYS call matplotlib.use('Agg') BEFORE importing pyplot
  - ALWAYS plt.close() after saving to free memory
  - ALWAYS use dpi=160, bbox_inches='tight'
  - NEVER call plt.show() (headless environment)
  - Use f-strings for dynamic values
  - Handle missing data gracefully (skip NaN)
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

## Output Conventions

```yaml
FILE_NAMING:
  pattern: "{name}_{chart_type}_{timestamp}.png"
  examples:
    - "sales_bar_20260416.png"
    - "revenue_line_20260416.png"
    - "market_share_pie_20260416.png"
  directory: Same as source data, or user-specified, or tmp/

QUALITY:
  dpi: 160 (always)
  format: PNG (default), SVG (if user requests vector)
  background: White (#FFFFFF)
  no_extra_whitespace: bbox_inches='tight'
```

---

## What This Skill Does NOT Do

- Does NOT display charts interactively (headless only, Agg backend)
- Does NOT generate images from text prompts (that is image generation mode, US-3.1.2)
- Does NOT modify source data files
- Does NOT install matplotlib — assumes already installed (see /cai-dat)
- Does NOT use plt.show() — always saves to file
