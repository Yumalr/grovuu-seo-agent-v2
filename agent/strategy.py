"""Strategy generation pipeline.

Extracted from the original app.py. Uses google.genai SDK.
Retains the multi-pass approach (research → assembly → validation → content).
"""

import json
import time
from google import genai
from google.genai import types


def generate_with_retry(client, model_name, prompt, config=None, retries=5):
    """Wrapper to handle 429 (Rate Limits) and 503 (Unavailable) gracefully.
    Adds a mandatory sleep to respect the 15 RPM free tier limit.
    """
    gen_config = config or types.GenerateContentConfig()

    for attempt in range(retries):
        try:
            # Enforce 15 RPM limit (1 request every 4 seconds)
            time.sleep(4.5)
            return client.models.generate_content(
                model=model_name,
                contents=prompt,
                config=gen_config,
            )
        except Exception as e:
            error_str = str(e)
            is_rate_limit_or_unavailable = any(
                code in error_str for code in ["429", "503", "ResourceExhausted", "UNAVAILABLE"]
            )
            
            if attempt < retries - 1 and is_rate_limit_or_unavailable:
                # Wait longer on actual errors (backoff)
                sleep_time = 15 * (attempt + 1)
                print(f"Rate limit or 503 hit. Sleeping for {sleep_time}s...")
                time.sleep(sleep_time)
            else:
                raise


def assembly_pass(client, model_name, brief_text: str) -> dict:
    """Produces the complete strategy plan in a single request."""
    system = (
        "You are a senior SEO strategist at a boutique consultancy. You are designing a "
        "market-entry SEO strategy for a client. You convert the brief into a structured JSON object.\n\n"
        "STRATEGY REQUIREMENTS:\n"
        "- Think through the client's Ideal Customer Profiles (ICPs).\n"
        "- Detail why a 'flat' website structure fails and propose a 'Hub-and-Spoke' architecture.\n"
        "- Propose a Phasing strategy using 'Pilot, Scale, Park' methodology.\n\n"
        "Strictly output a JSON object with these EXACT keys:\n"
        "- business_name (string)\n"
        "- market (string)\n"
        "- what_we_are_doing (string, 2-3 paragraphs)\n"
        "- why_necessary (string, 2-3 paragraphs)\n"
        '- business_goals (array of objects: {"driver": string, "how_seo_achieves_this": string})\n'
        "- structure_value (string)\n"
        "- icps (array of strings)\n"
        "- pages (array of objects: type, proposed_url, main_keyword, title_patterned, h1_patterned, phase, policy)\n"
        "- next_steps (array of strings)\n"
        '- meta (array of objects: page_name, url, meta_title [<=60 chars], meta_description [<=155 chars], h1, primary_keywords, search_intent)\n'
        "Respond with ONLY the valid JSON object."
    )
    user = f"CLIENT BRIEF:\n{brief_text}"

    config = types.GenerateContentConfig(
        system_instruction=system,
        response_mime_type="application/json",
    )
    resp = generate_with_retry(client, model_name, user, config=config)

    text = resp.text.strip()
    if text.startswith("```json"):
        text = text[7:]
    if text.startswith("```"):
        text = text[3:]
    if text.endswith("```"):
        text = text[:-3]

    return json.loads(text.strip())


def validate_plan(plan: dict) -> list[str]:
    """Basic quality gate: catches thin or broken output."""
    issues = []
    required = [
        "business_name", "what_we_are_doing", "why_necessary",
        "business_goals", "pages", "meta",
    ]
    for key in required:
        if not plan.get(key):
            issues.append(f"Missing or empty field: {key}")
    if len(plan.get("pages", [])) < 3:
        issues.append("Fewer than 3 pages generated, likely too shallow")
    keywords = [
        p.get("primary_keyword", p.get("main_keyword"))
        for p in plan.get("pages", [])
    ]
    if len(keywords) != len(set(keywords)):
        issues.append("Duplicate primary keywords across pages, risk of cannibalization")
    for m in plan.get("meta", []):
        if len(m.get("meta_title", "")) > 60:
            issues.append(f"Meta title too long for {m.get('url')}")
        if len(m.get("meta_description", "")) > 155:
            issues.append(f"Meta description too long for {m.get('url')}")
    return issues


def content_pass(client, model_name, brief_text: str, plan: dict) -> dict:
    """Generate HTML for the top 3 core pages in a single request."""
    pages = plan.get("pages", [])

    def sort_key(p):
        return p.get("phase", "P9")

    sorted_pages = sorted(pages, key=sort_key)[:3]
    if not sorted_pages:
        return {}

    system = (
        "You are an expert SEO Content Writer and Web Developer. "
        "Write the complete, semantic HTML5 pages for the following page briefs. "
        "REQUIREMENTS:\n"
        "- Include <head> with proper meta title and description.\n"
        "- Use the provided H1.\n"
        "- Structure with H2s, H3s, paragraphs, and lists.\n"
        "- Write detailed, persuasive B2B copy.\n"
        "- Strictly output a JSON dictionary where the keys are filenames (e.g. 'page1.html') and values are the raw HTML strings.\n"
    )

    user = f"CLIENT BRIEF:\n{brief_text}\n\nPAGE BRIEFS:\n"
    for page in sorted_pages:
        url = page.get("proposed_url", "")
        if url.startswith("/"):
            url = url[1:]
        if url.endswith("/"):
            url = url[:-1]

        page_name = (
            url.replace("/", "_")
            if url
            else page.get("main_keyword", "index").replace(" ", "_")
        )
        safe_name = f"{page_name}.html"
        
        meta_desc = ""
        meta_title = page.get("title_patterned", "")
        for m in plan.get("meta", []):
            if m.get("url") == page.get("proposed_url"):
                meta_desc = m.get("meta_description", "")
                if not meta_title:
                    meta_title = m.get("meta_title", "")
                break
                
        user += (
            f"Filename: {safe_name}\n"
            f"Type: {page.get('type')}\n"
            f"Keyword: {page.get('main_keyword')}\n"
            f"Meta Title: {meta_title}\n"
            f"Meta Description: {meta_desc}\n"
            f"H1: {page.get('h1_patterned')}\n---\n"
        )

    config = types.GenerateContentConfig(
        system_instruction=system,
        response_mime_type="application/json"
    )
    resp = generate_with_retry(client, model_name, user, config=config)
    
    text = resp.text.strip()
    if text.startswith("```json"):
        text = text[7:]
    if text.startswith("```"):
        text = text[3:]
    if text.endswith("```"):
        text = text[:-3]

    try:
        return json.loads(text.strip())
    except json.JSONDecodeError:
        return {}
