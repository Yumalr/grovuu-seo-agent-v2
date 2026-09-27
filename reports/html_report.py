"""HTML audit report generator.

Produces a self-contained HTML report from inspect_page evidence,
following the HTML Report Spec from SEO Skill.md:
- Plus Jakarta Sans via Google Fonts CDN
- Card layout with severity pills
- Responsive, dark-mode aware
- No external JavaScript
"""

import html as html_mod
from datetime import datetime


def _esc(text) -> str:
    """HTML-escape a value, handling None."""
    if text is None:
        return '<span style="color:var(--muted)">None</span>'
    return html_mod.escape(str(text))


def _pill(severity: str) -> str:
    """Render a severity pill."""
    classes = {
        "Critical": "p-crit",
        "Warning": "p-warn",
        "Pass": "p-pass",
        "Info": "p-info",
    }
    cls = classes.get(severity, "p-info")
    return f'<span class="pill {cls}">{_esc(severity)}</span>'


def _tile(label: str, value, color: str = "") -> str:
    """Render a summary tile."""
    style = f' style="color:{color}"' if color else ""
    return f"""<div class="tile">
  <div class="v"{style}>{_esc(str(value))}</div>
  <div class="k">{_esc(label)}</div>
</div>"""


def generate_audit_report(inspection: dict, findings_md: str = "") -> str:
    """Generate a self-contained HTML audit report from inspection evidence.

    Args:
        inspection: The dict returned by inspect_page().
        findings_md: Optional markdown-formatted findings from the agent.

    Returns:
        Complete HTML string ready to save as a file.
    """
    meta = inspection.get("metadata", {})
    http = inspection.get("http", {})
    idx = inspection.get("indexability", {})
    content = inspection.get("content", {})
    links = inspection.get("links", {})
    images = inspection.get("images", {})
    sd = inspection.get("structuredData", {})
    headings = inspection.get("headings", {})
    og = meta.get("openGraph", {})

    page_url = inspection.get("finalUrl", inspection.get("requestedUrl", "Unknown"))
    title = meta.get("title", "Untitled")
    now = datetime.now().strftime("%d %b %Y, %H:%M")

    # Count issues for summary tiles
    issues_critical = 0
    issues_warning = 0
    issues_pass = 0

    # Auto-detect issues from evidence
    quick_checks = []

    # Title
    title_len = meta.get("titleCharacters", 0)
    if not title:
        quick_checks.append(("Critical", "Missing title tag"))
        issues_critical += 1
    elif title_len > 60:
        quick_checks.append(("Warning", f"Title too long ({title_len} chars, max 60)"))
        issues_warning += 1
    else:
        quick_checks.append(("Pass", f"Title present ({title_len} chars)"))
        issues_pass += 1

    # Meta description
    desc_len = meta.get("metaDescriptionCharacters", 0)
    if desc_len == 0:
        quick_checks.append(("Critical", "Missing meta description"))
        issues_critical += 1
    elif desc_len > 155:
        quick_checks.append(("Warning", f"Meta description too long ({desc_len} chars, max 155)"))
        issues_warning += 1
    else:
        quick_checks.append(("Pass", f"Meta description present ({desc_len} chars)"))
        issues_pass += 1

    # Canonical
    if idx.get("canonical"):
        quick_checks.append(("Pass", "Canonical tag present"))
        issues_pass += 1
    else:
        quick_checks.append(("Warning", "No canonical tag"))
        issues_warning += 1

    # H1
    h1_list = headings.get("h1", [])
    if len(h1_list) == 0:
        quick_checks.append(("Critical", "No H1 tag"))
        issues_critical += 1
    elif len(h1_list) > 1:
        quick_checks.append(("Warning", f"Multiple H1 tags ({len(h1_list)})"))
        issues_warning += 1
    else:
        quick_checks.append(("Pass", "Single H1 present"))
        issues_pass += 1

    # JSON-LD
    if sd.get("jsonLdTypes"):
        quick_checks.append(("Pass", f"JSON-LD: {', '.join(sd['jsonLdTypes'])}"))
        issues_pass += 1
    else:
        quick_checks.append(("Warning", "No JSON-LD structured data"))
        issues_warning += 1

    # Images missing alt
    missing_alt = images.get("missingAltAttribute", 0)
    if missing_alt > 0:
        quick_checks.append(("Warning", f"{missing_alt} images missing alt attribute"))
        issues_warning += 1
    else:
        quick_checks.append(("Pass", "All images have alt attributes"))
        issues_pass += 1

    # Images missing dimensions
    missing_dims = images.get("missingDimensions", 0)
    if missing_dims > 0:
        quick_checks.append(("Warning", f"{missing_dims} images missing width/height"))
        issues_warning += 1
    else:
        quick_checks.append(("Pass", "All images have dimensions"))
        issues_pass += 1

    # Open Graph
    og_present = any(v for v in og.values() if v)
    if og_present:
        quick_checks.append(("Pass", "Open Graph tags present"))
        issues_pass += 1
    else:
        quick_checks.append(("Warning", "No Open Graph tags"))
        issues_warning += 1

    # Build findings HTML
    findings_html = ""
    for severity, message in quick_checks:
        findings_html += f"""<div class="finding">
  <div class="t">{_pill(severity)} <h3>{_esc(message)}</h3></div>
</div>\n"""

    # Build headings table
    headings_rows = ""
    for h in headings.get("all", [])[:50]:
        indent = "&nbsp;" * ((h["level"] - 1) * 4)
        headings_rows += f"<tr><td>H{h['level']}</td><td>{indent}{_esc(h['text'])}</td></tr>\n"

    # Build images table (first 20)
    images_rows = ""
    for img in images.get("items", [])[:20]:
        alt_cell = _esc(img["alt"]) if img["alt"] is not None else '<span style="color:var(--crit)">Missing</span>'
        dims = f"{img['width']}×{img['height']}" if img["width"] and img["height"] else '<span style="color:var(--warn)">Missing</span>'
        src_short = (img["src"][:80] + "...") if len(img["src"]) > 80 else img["src"]
        images_rows += f"<tr><td class='mono'>{_esc(src_short)}</td><td>{alt_cell}</td><td>{dims}</td><td>{_esc(img.get('loading', ''))}</td></tr>\n"

    return f"""<!DOCTYPE html>
<html lang="en" data-theme="light">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>SEO Audit: {_esc(title)}</title>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700&display=swap">
<style>
:root {{
  --bg:#f9fafb; --card:#ffffff; --line:#e5e7eb; --thead:#f3f4f6; --zebra:#f9fafb;
  --text:#374151; --head:#111827; --muted:#6b7280; --accent:#0f766e;
  --crit:#dc2626; --crit-bg:#fef2f2; --warn:#b45309; --warn-bg:#fffbeb;
  --pass:#059669; --pass-bg:#ecfdf5; --info:#2563eb; --info-bg:#eff6ff;
}}
@media (prefers-color-scheme: dark) {{
  :root:not([data-theme="light"]) {{
    color-scheme:dark;
    --bg:#0f1417; --card:#161d21; --line:#2a3338; --thead:#1c2429; --zebra:#12191c;
    --text:#cbd5da; --head:#f1f5f7; --muted:#8b989f; --accent:#2dd4bf;
    --crit:#f87171; --crit-bg:#2a1414; --warn:#fbbf24; --warn-bg:#2a2210;
    --pass:#34d399; --pass-bg:#0f2620; --info:#60a5fa; --info-bg:#111f33;
  }}
}}
* {{ box-sizing:border-box }}
body {{ background:var(--bg); color:var(--text); font-family:"Plus Jakarta Sans",system-ui,sans-serif; font-size:.95rem; line-height:1.7; padding:32px 16px 64px; margin:0 }}
.wrap {{ max-width:980px; margin:0 auto; display:flex; flex-direction:column; gap:36px }}
h1,h2,h3 {{ color:var(--head); margin:0 }}
h1 {{ font-size:1.75rem; font-weight:700 }}
h2 {{ font-size:1.25rem; font-weight:700 }}
h3 {{ font-size:1rem; font-weight:700 }}
p {{ margin:0 }}
.intro {{ color:var(--muted); font-size:.95rem }}
section {{ display:flex; flex-direction:column; gap:14px }}
.mono {{ font-family:ui-monospace,Consolas,monospace; font-size:.85em; word-break:break-word }}
a {{ color:var(--accent) }}

.tiles {{ display:grid; grid-template-columns:repeat(4,1fr); gap:12px }}
.tile {{ background:var(--card); border:1px solid var(--line); border-radius:8px; padding:14px 16px }}
.tile .v {{ font-size:1.5rem; font-weight:700; color:var(--head) }}
.tile .k {{ font-size:.8rem; color:var(--muted) }}
@media (max-width:640px) {{ .tiles {{ grid-template-columns:repeat(2,1fr) }} }}

.tbl {{ overflow-x:auto; background:var(--card); border:1px solid var(--line); border-radius:8px }}
table {{ border-collapse:collapse; width:100%; font-size:.9rem }}
th,td {{ padding:10px 14px; text-align:left; vertical-align:top; border-bottom:1px solid var(--line) }}
th {{ background:var(--thead); font-weight:600; color:var(--head); white-space:nowrap }}
tbody tr:nth-child(even) td {{ background:var(--zebra) }}
tbody tr:last-child td {{ border-bottom:0 }}

.pill {{ display:inline-block; font-size:.72rem; font-weight:600; padding:2px 8px; border-radius:999px; white-space:nowrap }}
.p-crit {{ color:var(--crit); background:var(--crit-bg) }}
.p-warn {{ color:var(--warn); background:var(--warn-bg) }}
.p-pass {{ color:var(--pass); background:var(--pass-bg) }}
.p-info {{ color:var(--info); background:var(--info-bg) }}

.finding {{ background:var(--card); border:1px solid var(--line); border-radius:8px; padding:14px 18px; display:flex; flex-direction:column; gap:6px }}
.finding .t {{ display:flex; gap:10px; align-items:center; flex-wrap:wrap }}

.meta-grid {{ display:grid; grid-template-columns: 160px 1fr; gap:6px 16px; font-size:.9rem }}
.meta-grid dt {{ color:var(--muted); font-weight:600 }}
.meta-grid dd {{ margin:0; word-break:break-word }}
</style>
</head>
<body>
<div class="wrap">

<header>
  <div>
    <h1>SEO Page Audit</h1>
    <p class="intro">{_esc(page_url)}</p>
    <p class="intro" style="margin-top:4px">Generated {now} &middot; Evidence: OBSERVED via inspect_page MCP &middot; Fetch: {inspection.get('fetchMs', '?')}ms</p>
  </div>
</header>

<section>
  <h2>Summary</h2>
  <div class="tiles">
    {_tile("Critical", issues_critical, "var(--crit)")}
    {_tile("Warnings", issues_warning, "var(--warn)")}
    {_tile("Passed", issues_pass, "var(--pass)")}
    {_tile("Word Count", content.get("serverHtmlWordCount", 0))}
  </div>
</section>

<section>
  <h2>Metadata</h2>
  <div class="finding">
    <dl class="meta-grid">
      <dt>HTTP Status</dt><dd>{http.get("status", "?")}</dd>
      <dt>Title</dt><dd>{_esc(meta.get("title", ""))} ({meta.get("titleCharacters", 0)} chars)</dd>
      <dt>Meta Description</dt><dd>{_esc(meta.get("metaDescription", "")) or '<span style="color:var(--crit)">Missing</span>'} ({meta.get("metaDescriptionCharacters", 0)} chars)</dd>
      <dt>Canonical</dt><dd class="mono">{_esc(idx.get("canonical", "None"))}</dd>
      <dt>Self-referencing</dt><dd>{"Yes" if idx.get("selfReferencingCanonical") else "No"}</dd>
      <dt>Robots Meta</dt><dd>{_esc(idx.get("robotsMeta")) or "None"}</dd>
      <dt>X-Robots-Tag</dt><dd>{_esc(http.get("xRobotsTag")) or "None"}</dd>
      <dt>Noindex</dt><dd>{"Yes ⚠️" if idx.get("noindex") else "No"}</dd>
      <dt>Language</dt><dd>{_esc(meta.get("lang")) or "Not set"}</dd>
      <dt>Viewport</dt><dd>{_esc(meta.get("viewport")) or "Not set"}</dd>
    </dl>
  </div>
</section>

<section>
  <h2>Open Graph</h2>
  <div class="finding">
    <dl class="meta-grid">
      <dt>og:title</dt><dd>{_esc(og.get("title")) or "Not set"}</dd>
      <dt>og:description</dt><dd>{_esc(og.get("description")) or "Not set"}</dd>
      <dt>og:image</dt><dd class="mono">{_esc(og.get("image")) or "Not set"}</dd>
      <dt>og:type</dt><dd>{_esc(og.get("type")) or "Not set"}</dd>
    </dl>
  </div>
</section>

<section>
  <h2>Findings</h2>
  <div style="display:flex; flex-direction:column; gap:10px">
    {findings_html}
  </div>
</section>

<section>
  <h2>Heading Structure</h2>
  <div class="tbl">
    <table>
      <thead><tr><th>Level</th><th>Text</th></tr></thead>
      <tbody>{headings_rows or '<tr><td colspan="2" style="color:var(--muted)">No headings found</td></tr>'}</tbody>
    </table>
  </div>
</section>

<section>
  <h2>Links</h2>
  <div class="tiles" style="grid-template-columns:repeat(2,1fr)">
    {_tile("Internal Links", links.get("internalCount", 0))}
    {_tile("External Links", links.get("externalCount", 0))}
  </div>
</section>

<section>
  <h2>Images ({images.get("count", 0)} found)</h2>
  <div class="tiles" style="grid-template-columns:repeat(3,1fr)">
    {_tile("Missing Alt", images.get("missingAltAttribute", 0), "var(--crit)" if images.get("missingAltAttribute", 0) > 0 else "")}
    {_tile("Missing Dimensions", images.get("missingDimensions", 0), "var(--warn)" if images.get("missingDimensions", 0) > 0 else "")}
    {_tile("Lazy Loaded", images.get("lazyLoaded", 0))}
  </div>
  {f'''<div class="tbl">
    <table>
      <thead><tr><th>Source</th><th>Alt</th><th>Dimensions</th><th>Loading</th></tr></thead>
      <tbody>{images_rows}</tbody>
    </table>
  </div>''' if images_rows else ""}
</section>

<section>
  <h2>Structured Data</h2>
  <div class="finding">
    <dl class="meta-grid">
      <dt>JSON-LD Types</dt><dd>{", ".join(sd.get("jsonLdTypes", [])) or "None found"}</dd>
      <dt>Invalid Blocks</dt><dd>{", ".join(sd.get("invalidJsonLd", [])) or "None"}</dd>
    </dl>
  </div>
</section>

<section>
  <h2>Limitations</h2>
  <div class="finding">
    <p style="color:var(--muted); font-size:.9rem">This report is based on server-rendered HTML only. The following were NOT inspected:</p>
    <ul style="color:var(--muted); font-size:.9rem; margin:8px 0 0; padding-left:20px">
      {"".join(f"<li>{_esc(l)}</li>" for l in inspection.get("limitations", []))}
    </ul>
  </div>
</section>

</div>
</body>
</html>"""
