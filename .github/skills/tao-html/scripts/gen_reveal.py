#!/usr/bin/env python3
"""Generate a reveal.js HTML presentation from JSON slide data.

Usage:
    python3 gen_reveal.py --input slides.json --output presentation.html --style corporate
"""

import argparse
import base64
import json
import sys
from html import escape
from pathlib import Path

REVEALJS_VERSION = "5.1.0"
REVEALJS_CDN = f"https://cdn.jsdelivr.net/npm/reveal.js@{REVEALJS_VERSION}"

STYLES = {
    "corporate": {
        "reveal_theme": "white",
        "background": "#ffffff",
        "heading_color": "#1a365d",
        "text_color": "#2d3748",
        "accent_color": "#3182ce",
        "font_heading": "'Segoe UI', 'Helvetica Neue', Arial, sans-serif",
        "font_body": "'Segoe UI', 'Helvetica Neue', Arial, sans-serif",
    },
    "academic": {
        "reveal_theme": "simple",
        "background": "#fafafa",
        "heading_color": "#1a202c",
        "text_color": "#1a202c",
        "accent_color": "#744210",
        "font_heading": "Georgia, 'Times New Roman', serif",
        "font_body": "Georgia, 'Times New Roman', serif",
    },
    "minimal": {
        "reveal_theme": "white",
        "background": "#ffffff",
        "heading_color": "#111827",
        "text_color": "#374151",
        "accent_color": "#059669",
        "font_heading": "'Inter', 'Helvetica Neue', Arial, sans-serif",
        "font_body": "'Inter', 'Helvetica Neue', Arial, sans-serif",
    },
    "dark-modern": {
        "reveal_theme": "night",
        "background": "#0f172a",
        "heading_color": "#6366f1",
        "text_color": "#f1f5f9",
        "accent_color": "#22d3ee",
        "font_heading": "'Inter', 'SF Pro Display', sans-serif",
        "font_body": "'Inter', 'SF Pro Text', sans-serif",
    },
    "creative": {
        "reveal_theme": "moon",
        "background": "#fffbeb",
        "heading_color": "#8b5cf6",
        "text_color": "#1e1b4b",
        "accent_color": "#f59e0b",
        "font_heading": "'Poppins', 'Nunito', sans-serif",
        "font_body": "'Open Sans', 'Nunito', sans-serif",
    },
}


def embed_image_base64(image_path: str) -> str:
    """Convert an image file to a base64 data URI."""
    path = Path(image_path)
    if not path.exists():
        return ""
    suffix = path.suffix.lower()
    mime_map = {".png": "image/png", ".jpg": "image/jpeg", ".jpeg": "image/jpeg",
                ".gif": "image/gif", ".svg": "image/svg+xml", ".webp": "image/webp"}
    mime = mime_map.get(suffix, "image/png")
    data = base64.b64encode(path.read_bytes()).decode("ascii")
    return f"data:{mime};base64,{data}"


def render_slide(slide: dict) -> str:
    """Render a single slide dict to a <section> HTML block."""
    slide_type = slide.get("type", "content")
    notes = slide.get("notes", "")
    notes_html = f'<aside class="notes">{escape(notes)}</aside>' if notes else ""

    if slide_type == "title":
        title = escape(slide.get("title", ""))
        subtitle = escape(slide.get("subtitle", ""))
        sub_html = f"<h3>{subtitle}</h3>" if subtitle else ""
        return f'<section data-state="title-slide"><h1>{title}</h1>{sub_html}{notes_html}</section>'

    if slide_type == "section":
        title = escape(slide.get("title", ""))
        return f'<section><h2>{title}</h2>{notes_html}</section>'

    if slide_type == "content":
        title = escape(slide.get("title", ""))
        bullets = slide.get("bullets", [])
        text = slide.get("text", "")
        body = ""
        if bullets:
            items = "".join(f"<li>{escape(b)}</li>" for b in bullets)
            body = f"<ul>{items}</ul>"
        elif text:
            body = f"<p>{escape(text)}</p>"
        return f"<section><h3>{title}</h3>{body}{notes_html}</section>"

    if slide_type == "image":
        title = escape(slide.get("title", ""))
        image_path = slide.get("image_path", "")
        caption = escape(slide.get("caption", ""))
        src = embed_image_base64(image_path) if image_path else ""
        img_tag = f'<img src="{src}" alt="{caption}" style="max-height:60vh;">' if src else f"<p><em>{caption}</em></p>"
        cap_html = f"<p><small>{caption}</small></p>" if caption else ""
        return f"<section><h3>{title}</h3>{img_tag}{cap_html}{notes_html}</section>"

    if slide_type == "quote":
        text = escape(slide.get("text", ""))
        author = escape(slide.get("author", ""))
        cite = f"<cite>— {author}</cite>" if author else ""
        return f"<section><blockquote><p>{text}</p>{cite}</blockquote>{notes_html}</section>"

    if slide_type == "code":
        title = escape(slide.get("title", ""))
        lang = slide.get("language", "")
        code = escape(slide.get("code", ""))
        return f'<section><h3>{title}</h3><pre><code data-trim data-noescape class="language-{lang}">{code}</code></pre>{notes_html}</section>'

    if slide_type == "table":
        title = escape(slide.get("title", ""))
        headers = slide.get("headers", [])
        rows = slide.get("rows", [])
        th = "".join(f"<th>{escape(h)}</th>" for h in headers)
        tr_list = []
        for row in rows:
            tds = "".join(f"<td>{escape(str(c))}</td>" for c in row)
            tr_list.append(f"<tr>{tds}</tr>")
        tbody = "".join(tr_list)
        return f"<section><h3>{title}</h3><table><thead><tr>{th}</tr></thead><tbody>{tbody}</tbody></table>{notes_html}</section>"

    if slide_type == "closing":
        title = escape(slide.get("title", "Cảm ơn!"))
        subtitle = escape(slide.get("subtitle", ""))
        sub_html = f"<p>{subtitle}</p>" if subtitle else ""
        return f'<section data-state="closing-slide"><h2>{title}</h2>{sub_html}{notes_html}</section>'

    # Fallback: treat as content
    return render_slide({**slide, "type": "content"})


def generate_html(data: dict, style_name: str) -> str:
    """Generate complete reveal.js HTML from slide data and style."""
    style = STYLES.get(style_name, STYLES["corporate"])
    title = escape(data.get("title", "Presentation"))
    author = escape(data.get("author", ""))
    slides = data.get("slides", [])

    slides_html = "\n        ".join(render_slide(s) for s in slides)

    custom_css = f"""
      .reveal {{
        font-family: {style['font_body']};
        color: {style['text_color']};
      }}
      .reveal h1, .reveal h2, .reveal h3 {{
        font-family: {style['font_heading']};
        color: {style['heading_color']};
        text-transform: none;
      }}
      .reveal a {{ color: {style['accent_color']}; }}
      .reveal blockquote {{
        border-left: 4px solid {style['accent_color']};
        padding: 0.5em 1em;
        font-style: italic;
        background: rgba(0,0,0,0.03);
      }}
      .reveal table {{
        border-collapse: collapse;
        margin: 0 auto;
      }}
      .reveal table th {{
        background: {style['accent_color']};
        color: #fff;
        padding: 0.5em 1em;
      }}
      .reveal table td {{
        border: 1px solid #ddd;
        padding: 0.5em 1em;
      }}
      .reveal table tr:nth-child(even) td {{
        background: rgba(0,0,0,0.03);
      }}
      .reveal ul, .reveal ol {{
        text-align: left;
        display: block;
        margin-left: 1em;
      }}
      .reveal li {{
        margin-bottom: 0.4em;
        line-height: 1.5;
      }}
      .reveal pre {{
        width: 90%;
        font-size: 0.65em;
      }}
      .reveal .slide-number {{
        color: {style['text_color']};
        font-size: 0.6em;
      }}
    """

    html = f"""<!DOCTYPE html>
<html lang="vi">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <meta name="author" content="{author}">
  <title>{title}</title>
  <link rel="stylesheet" href="{REVEALJS_CDN}/dist/reveal.css">
  <link rel="stylesheet" href="{REVEALJS_CDN}/dist/theme/{style['reveal_theme']}.css">
  <link rel="stylesheet" href="{REVEALJS_CDN}/plugin/highlight/monokai.css">
  <style>{custom_css}
  </style>
</head>
<body>
  <div class="reveal">
    <div class="slides">
      {slides_html}
    </div>
  </div>
  <script src="{REVEALJS_CDN}/dist/reveal.js"></script>
  <script src="{REVEALJS_CDN}/plugin/notes/notes.js"></script>
  <script src="{REVEALJS_CDN}/plugin/highlight/highlight.js"></script>
  <script>
    Reveal.initialize({{
      hash: true,
      slideNumber: true,
      transition: 'slide',
      plugins: [RevealNotes, RevealHighlight]
    }});
  </script>
</body>
</html>"""
    return html


def main():
    parser = argparse.ArgumentParser(description="Generate reveal.js HTML presentation from JSON data")
    parser.add_argument("--input", required=True, help="Path to JSON file with slide data")
    parser.add_argument("--output", required=True, help="Output HTML file path")
    parser.add_argument("--style", choices=list(STYLES.keys()), default="corporate",
                        help="Presentation style (default: corporate)")
    args = parser.parse_args()

    input_path = Path(args.input)
    if not input_path.exists():
        print(f"Error: Input file not found: {input_path}", file=sys.stderr)
        sys.exit(1)

    with open(input_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    html = generate_html(data, args.style)

    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(html)

    size_kb = output_path.stat().st_size / 1024
    slide_count = len(data.get("slides", []))
    print(f"✅ Saved: {output_path} ({size_kb:.1f} KB, {slide_count} slides, style: {args.style})")


if __name__ == "__main__":
    main()
