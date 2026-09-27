"""inspect_page MCP tool — single-page server-HTML SEO evidence.

Ported from the TypeScript reference implementation in inspect_page_mcp_v0.1.
Uses httpx for HTTP fetching and BeautifulSoup for HTML parsing.

Returns the same evidence schema as the reference: HTTP status, canonical,
robots directives, title/description + char counts, heading hierarchy,
internal/external links + anchors, images, OG tags, JSON-LD types,
language, viewport, and server-HTML word count.
"""

import json
import re
import time
from urllib.parse import urlparse, urljoin

import httpx
from bs4 import BeautifulSoup

from .security import validate_url

USER_AGENT = "Mozilla/5.0 (compatible; GrovuuSEOInspector/0.1)"
FETCH_TIMEOUT = 15  # seconds
MAX_RESPONSE_BYTES = 5 * 1024 * 1024  # 5 MB
MAX_IMAGES = 250
MAX_INTERNAL_LINKS = 200
MAX_EXTERNAL_LINKS = 100


def _clean(text: str) -> str:
    """Collapse whitespace and strip."""
    return re.sub(r"\s+", " ", text).strip()


def _abs_url(base: str, href: str | None) -> str | None:
    """Resolve a relative URL against a base. Returns None on failure."""
    if not href:
        return None
    try:
        return urljoin(base, href)
    except Exception:
        return None


def _walk_jsonld(node, types: set):
    """Recursively extract @type values from JSON-LD."""
    if node is None:
        return
    if isinstance(node, list):
        for item in node:
            _walk_jsonld(item, types)
        return
    if not isinstance(node, dict):
        return
    t = node.get("@type")
    if isinstance(t, str):
        types.add(t)
    elif isinstance(t, list):
        for x in t:
            if isinstance(x, str):
                types.add(x)
    if "@graph" in node:
        _walk_jsonld(node["@graph"], types)


def _get_schema_types(soup: BeautifulSoup) -> dict:
    """Extract JSON-LD @type values and flag invalid blocks."""
    types: set[str] = set()
    invalid: list[str] = []

    for i, script in enumerate(soup.find_all("script", type="application/ld+json")):
        raw = script.string
        if not raw or not raw.strip():
            continue
        try:
            parsed = json.loads(raw)
            _walk_jsonld(parsed, types)
        except json.JSONDecodeError:
            invalid.append(f"JSON-LD block {i + 1} is invalid JSON")

    return {"types": sorted(types), "invalid": invalid}


def inspect_page(url: str) -> dict:
    """Fetch one public webpage and return observed server-HTML SEO evidence.

    This is the Phase 1 MCP tool. It inspects server-rendered HTML only
    and explicitly states its limitations.

    Args:
        url: Public URL to inspect (http or https).

    Returns:
        dict with evidence status, HTTP info, indexability, metadata,
        headings, content metrics, links, images, structured data,
        and a limitations list.
    """
    # SSRF validation
    validate_url(url)

    started = time.time()

    with httpx.Client(
        follow_redirects=True,
        timeout=FETCH_TIMEOUT,
        max_redirects=5,
        headers={
            "user-agent": USER_AGENT,
            "accept": "text/html,application/xhtml+xml",
        },
    ) as client:
        response = client.get(url)

    fetch_ms = int((time.time() - started) * 1000)
    html = response.text
    html_bytes = len(html.encode("utf-8"))
    final_url = str(response.url)

    soup = BeautifulSoup(html, "html.parser")

    # --- Title ---
    title_tag = soup.find("title")
    title = _clean(title_tag.get_text()) if title_tag else ""

    # --- Meta description ---
    meta_desc_tag = soup.find("meta", attrs={"name": "description"})
    meta_description = (
        meta_desc_tag.get("content", "").strip() if meta_desc_tag else ""
    )

    # --- Canonical ---
    canonical_tag = soup.find("link", rel="canonical")
    canonical = (
        _abs_url(final_url, canonical_tag.get("href")) if canonical_tag else None
    )

    # --- Robots ---
    robots_meta_tag = soup.find("meta", attrs={"name": "robots"})
    robots_meta = (
        robots_meta_tag.get("content", "").strip() if robots_meta_tag else None
    )
    x_robots_tag = response.headers.get("x-robots-tag")

    noindex_check = f"{robots_meta or ''},{x_robots_tag or ''}".lower()
    is_noindex = "noindex" in noindex_check

    # --- Headings ---
    headings = []
    for tag in soup.find_all(re.compile(r"^h[1-6]$")):
        text = _clean(tag.get_text())
        if text:
            headings.append({"level": int(tag.name[1]), "text": text})

    h1_list = [h["text"] for h in headings if h["level"] == 1]

    # --- Links ---
    origin_parsed = urlparse(final_url)
    origin = f"{origin_parsed.scheme}://{origin_parsed.netloc}"
    internal_links = []
    external_links = []

    for a_tag in soup.find_all("a", href=True):
        href = _abs_url(final_url, a_tag.get("href"))
        if not href:
            continue
        anchor = _clean(a_tag.get_text())
        rel_attr = a_tag.get("rel")
        rel_str = " ".join(rel_attr) if isinstance(rel_attr, list) else rel_attr

        link_data = {"href": href, "anchor": anchor, "rel": rel_str}

        try:
            link_parsed = urlparse(href)
            link_origin = f"{link_parsed.scheme}://{link_parsed.netloc}"
            if link_origin == origin:
                internal_links.append(link_data)
            else:
                external_links.append(link_data)
        except Exception:
            external_links.append(link_data)

    # --- Images (capped) ---
    images = []
    for img in soup.find_all("img")[:MAX_IMAGES]:
        images.append(
            {
                "src": _abs_url(final_url, img.get("src")) or img.get("src", ""),
                "alt": img.get("alt"),
                "width": img.get("width"),
                "height": img.get("height"),
                "loading": img.get("loading"),
                "fetchpriority": img.get("fetchpriority"),
            }
        )

    # --- Word count (body text, excluding script/style/noscript/svg) ---
    body = soup.find("body")
    if body:
        body_copy = BeautifulSoup(str(body), "html.parser")
        for unwanted in body_copy.find_all(["script", "style", "noscript", "svg"]):
            unwanted.decompose()
        body_text = _clean(body_copy.get_text())
        word_count = len(body_text.split()) if body_text else 0
    else:
        word_count = 0

    # --- JSON-LD ---
    json_ld = _get_schema_types(soup)

    # --- Open Graph ---
    def _og(prop):
        tag = soup.find("meta", property=prop)
        return tag.get("content") if tag else None

    # --- Language and viewport ---
    html_tag = soup.find("html")
    lang = html_tag.get("lang") if html_tag else None
    viewport_tag = soup.find("meta", attrs={"name": "viewport"})
    viewport = viewport_tag.get("content", "").strip() if viewport_tag else None

    return {
        "evidenceStatus": "OBSERVED — inspect_page MCP",
        "requestedUrl": url,
        "finalUrl": final_url,
        "fetchMs": fetch_ms,
        "http": {
            "status": response.status_code,
            "ok": 200 <= response.status_code < 300,
            "contentType": response.headers.get("content-type"),
            "xRobotsTag": x_robots_tag,
        },
        "indexability": {
            "noindex": is_noindex,
            "robotsMeta": robots_meta,
            "canonical": canonical,
            "selfReferencingCanonical": canonical == final_url
            if canonical
            else False,
        },
        "metadata": {
            "title": title,
            "titleCharacters": len(title),
            "metaDescription": meta_description,
            "metaDescriptionCharacters": len(meta_description),
            "lang": lang,
            "viewport": viewport,
            "openGraph": {
                "title": _og("og:title"),
                "description": _og("og:description"),
                "image": _og("og:image"),
                "type": _og("og:type"),
            },
        },
        "headings": {"h1": h1_list, "all": headings},
        "content": {
            "serverHtmlWordCount": word_count,
            "htmlBytes": html_bytes,
        },
        "links": {
            "internalCount": len(internal_links),
            "externalCount": len(external_links),
            "internal": internal_links[:MAX_INTERNAL_LINKS],
            "external": external_links[:MAX_EXTERNAL_LINKS],
        },
        "images": {
            "count": len(images),
            "missingAltAttribute": sum(1 for i in images if i["alt"] is None),
            "missingDimensions": sum(
                1 for i in images if not i["width"] or not i["height"]
            ),
            "lazyLoaded": sum(1 for i in images if i["loading"] == "lazy"),
            "items": images,
        },
        "structuredData": {
            "jsonLdTypes": json_ld["types"],
            "invalidJsonLd": json_ld["invalid"],
        },
        "limitations": [
            "Server HTML only; JavaScript is not executed.",
            "No Core Web Vitals.",
            "No Search Console or GA4.",
            "No rank or SERP competitor data.",
            "No full-site crawl evidence.",
        ],
    }
