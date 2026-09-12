import io
import json
import os
import zipfile
import time
import streamlit as st
import google.generativeai as genai
from google.api_core import exceptions as google_exceptions
from docxtpl import DocxTemplate
from openpyxl import Workbook
from openpyxl.styles import Font, Alignment, PatternFill
import docx2txt
from pypdf import PdfReader

# Configure Streamlit page
st.set_page_config(page_title="SEO Strategy Agent", layout="centered")

# Configure Gemini
api_key = os.getenv("GEMINI_API_KEY")
if not api_key:
    try:
        api_key = st.secrets.get("GEMINI_API_KEY")
    except:
        pass
if not api_key:
    st.error("GEMINI_API_KEY is not set.")
    st.stop()

genai.configure(api_key=api_key)
model_name = os.getenv("GEMINI_MODEL", "gemini-3.5-flash")
model = genai.GenerativeModel(model_name)

META_COLUMNS = [
    "#", "Page Name", "URL", "Meta Title",
    "Meta Description", "H1 (On-Page)", "Primary Keywords", "Search Intent"
]

DOCX_TEMPLATE_PATH = "template.docx"

def generate_with_retry(prompt, config=None, retries=3):
    """Wrapper to handle 429 Too Many Requests (Rate Limits) gracefully."""
    for attempt in range(retries):
        try:
            if config:
                return model.generate_content(prompt, generation_config=config)
            else:
                return model.generate_content(prompt)
        except google_exceptions.ResourceExhausted as e:
            if attempt < retries - 1:
                print(f"Rate limit hit (429). Retrying in 60 seconds... (Attempt {attempt+1}/{retries})")
                time.sleep(60)
            else:
                raise e
        except Exception as e:
            if attempt < retries - 1 and "429" in str(e):
                print(f"Rate limit hit. Retrying in 60 seconds... (Attempt {attempt+1}/{retries})")
                time.sleep(60)
            else:
                raise e

def extract_text(uploaded_file) -> str:
    from io import BytesIO
    from docx import Document
    ext = os.path.splitext(uploaded_file.name)[1].lower()
    file_bytes = uploaded_file.getvalue()
    if ext == ".pdf":
        reader = PdfReader(BytesIO(file_bytes))
        pages = [page.extract_text() or "" for page in reader.pages]
        return "\n\n".join(pages)
    elif ext == ".docx":
        document = Document(BytesIO(file_bytes))
        parts = []
        for paragraph in document.paragraphs:
            if paragraph.text.strip():
                parts.append(paragraph.text.strip())
        for table in document.tables:
            for row in table.rows:
                parts.append(" | ".join(cell.text.strip() for cell in row.cells))
        return "\n".join(parts)
    elif ext in {".txt", ".md"}:
        return file_bytes.decode("utf-8", errors="replace")
    else:
        raise ValueError(f"Unsupported file type: {ext}")

def research_pass(brief_text: str, extra_requirements: str) -> str:
    """Long-form reasoning. No JSON constraint here — the goal is extreme depth and quality."""
    print("Starting research_pass...")
    system = (
        "You are a senior SEO strategist at a boutique consultancy, writing a "
        "market-entry SEO strategy for a client. You are not a generic copywriter.\n\n"
        "CONTENT & TONE STANDARD:\n"
        "- Write in a highly human-centric, professional B2B agency tone. Use clear, direct language.\n"
        "- Strictly avoid generic AI buzzwords (e.g., 'delve', 'testament', 'revolutionize', 'landscape', 'unlock').\n"
        "- Do not use robotic transitions. Write as if a senior marketing strategist is speaking directly to a client.\n\n"
        "STRATEGY REQUIREMENTS:\n"
        "- Think through the client's Ideal Customer Profiles (ICPs) and provide real example search terms they use.\n"
        "- Detail why a 'flat' website structure fails (e.g., general 'international' pages cannot rank against specialized competitors).\n"
        "- Propose a 'Hub-and-Spoke' architecture for this business (Country Hubs, Service Hubs, Area Pages, and Service×Location Spokes) to capture long-tail, high-intent keywords.\n"
        "- Propose a Phasing strategy using a 'Pilot, Scale, Park' risk-management methodology (Scale = confident demand, Pilot = test demand, Park = consolidate due to low demand).\n"
        "Write this as a thorough, deep internal strategy memo."
    )
    user = f"CLIENT BRIEF:\n{brief_text}\n\nEXTRA REQUIREMENTS:\n{extra_requirements or 'None'}"
    
    prompt = f"{system}\n\n{user}"
    print("Calling Gemini API for research_pass...")
    resp = generate_with_retry(prompt)
    print("research_pass complete.")
    return resp.text

def assembly_pass(brief_text: str, research_memo: str) -> dict:
    """Structures the research memo into the exact schema the templates need."""
    print("Starting assembly_pass...")
    system = (
        "You convert a strategist's research memo into a structured JSON object for document generation. "
        "Do not shorten or generalize the memo's content — carry its extreme specificity and reasoning into each field. "
        "Strictly output a JSON object with these EXACT keys:\n"
        "- business_name (string)\n"
        "- market (string)\n"
        "- what_we_are_doing (string, 2-3 paragraphs explaining the foundational SEO and hub-and-spoke blueprint)\n"
        "- why_necessary (string, 2-3 paragraphs explaining why this is needed, citing specific ICPs and search terms)\n"
        "- business_goals (array of objects: {\"driver\": string, \"how_seo_achieves_this\": string})\n"
        "- structure_value (string, explaining why flat structure fails and hub-and-spoke succeeds for this client)\n"
        "- icps (array of strings)\n"
        "- pages (array of objects representing the URL plan. Each object must have: "
        "\"type\" [e.g., Country Hub, Service Hub, Area Page, S×L], "
        "\"proposed_url\", \"main_keyword\", \"title_patterned\", \"h1_patterned\", "
        "\"phase\" [e.g., P0, P1, P2], \"policy\" [Scale, Pilot, Parked])\n"
        "- next_steps (array of strings)\n"
        "- meta (array of objects for the excel sheet: \"page_name\", \"url\", \"meta_title\" [<=60 chars, MUST include brand name], "
        "\"meta_description\" [<=155 chars, MUST end with a strong Call to Action], \"h1\", \"primary_keywords\" [string, comma separated], \"search_intent\" [e.g., Commercial, Informational, Navigational])\n"
        "Respond with ONLY the valid JSON object."
    )
    user = f"ORIGINAL BRIEF:\n{brief_text}\n\nSTRATEGIST'S RESEARCH MEMO:\n{research_memo}"
    prompt = f"{system}\n\n{user}"
    
    print("Calling Gemini API for assembly_pass...")
    config = genai.GenerationConfig(response_mime_type="application/json")
    resp = generate_with_retry(prompt, config=config)
    print("assembly_pass complete.")
    
    text = resp.text.strip()
    if text.startswith("```json"):
        text = text[7:]
    if text.startswith("```"):
        text = text[3:]
    if text.endswith("```"):
        text = text[:-3]
        
    return json.loads(text.strip())

def validate_plan(plan: dict) -> list[str]:
    """Basic quality gate — catches thin or broken output before it reaches her."""
    issues = []
    required = ["business_name", "what_we_are_doing", "why_necessary",
                "business_goals", "pages", "meta"]
    for key in required:
        if not plan.get(key):
            issues.append(f"Missing or empty field: {key}")
    if len(plan.get("pages", [])) < 3:
        issues.append("Fewer than 3 pages generated — likely too shallow")
    keywords = [p.get("primary_keyword", p.get("main_keyword")) for p in plan.get("pages", [])]
    if len(keywords) != len(set(keywords)):
        issues.append("Duplicate primary keywords across pages — risk of keyword cannibalization")
    for m in plan.get("meta", []):
        if len(m.get("meta_title", "")) > 60:
            issues.append(f"Meta title too long for {m.get('url')}")
        if len(m.get("meta_description", "")) > 155:
            issues.append(f"Meta description too long for {m.get('url')}")
    return issues

def content_pass(brief_text: str, plan: dict) -> dict:
    """Takes the top 5 core pages from the plan and generates HTML individually for extremely high quality."""
    print("Starting content_pass...")
    pages = plan.get("pages", [])
    
    # Sort pages to prioritize core pages (e.g., P0 or Country Hubs). Limit to 5.
    def sort_key(p):
        return p.get("phase", "P9")
        
    sorted_pages = sorted(pages, key=sort_key)[:5]
    if not sorted_pages:
        return {}
        
    html_pages = {}
    
    for i, page in enumerate(sorted_pages, start=1):
        # Construct a safe filename based on the URL or Name
        url = page.get("proposed_url", "")
        if url.startswith("/"): url = url[1:]
        if url.endswith("/"): url = url[:-1]
        
        page_name = url.replace("/", "_") if url else page.get("main_keyword", "index").replace(" ", "_")
        safe_name = f"{page_name}.html"
            
        system = (
            "You are an expert SEO Content Writer and Web Developer. "
            "Write the complete, semantic HTML5 page for the following page brief. "
            "REQUIREMENTS:\n"
            "- Output ONLY raw HTML code (no markdown formatting blocks like ```html around it, just the raw HTML).\n"
            "- Include <head> with proper meta title and description.\n"
            "- Use the provided H1.\n"
            "- Structure the body content professionally with H2s, H3s, paragraphs, and lists.\n"
            "- Write EXTREMELY detailed, persuasive, human-centric B2B copy satisfying the target keyword's search intent. Be thorough.\n"
            "- Do not use generic filler (lorem ipsum); write actual comprehensive B2B copy based on the client brief.\n"
        )
        
        meta_desc = ""
        meta_title = page.get("title_patterned", "")
        for m in plan.get("meta", []):
            if m.get("url") == page.get("proposed_url"):
                meta_desc = m.get("meta_description", "")
                if not meta_title:
                    meta_title = m.get("meta_title", "")
                break
                
        user = (
            f"CLIENT BRIEF:\n{brief_text}\n\n"
            f"PAGE REQUIREMENTS:\n"
            f"- Page Type: {page.get('type')}\n"
            f"- Proposed URL: {page.get('proposed_url')}\n"
            f"- Primary Keyword: {page.get('main_keyword')}\n"
            f"- Meta Title: {meta_title}\n"
            f"- Meta Description: {meta_desc}\n"
            f"- H1: {page.get('h1_patterned')}\n\n"
            f"Generate the full, extensive semantic HTML."
        )
        
        prompt = f"{system}\n\n{user}"
        print(f"Calling Gemini API for HTML generation ({i}/5) - {safe_name}...")
        resp = generate_with_retry(prompt)
        print(f"HTML generation complete for {safe_name}.")
        text = resp.text.strip()
        if text.startswith("```html"):
            text = text[7:]
        if text.startswith("```"):
            text = text[3:]
        if text.endswith("```"):
            text = text[:-3]
            
        html_pages[safe_name] = text.strip()
        
    return html_pages

def render_docx(plan: dict) -> bytes:
    if not os.path.exists(DOCX_TEMPLATE_PATH):
        raise FileNotFoundError(f"Template '{DOCX_TEMPLATE_PATH}' not found in directory.")
    doc = DocxTemplate(DOCX_TEMPLATE_PATH)
    doc.render(plan)
    buf = io.BytesIO()
    doc.save(buf)
    return buf.getvalue()

def render_excel_meta(meta_rows: list) -> bytes:
    wb = Workbook()
    ws = wb.active
    ws.title = "Meta Data - Final"
    ws.append(META_COLUMNS)
    
    # Format Headers
    header_fill = PatternFill(start_color="1F4E78", end_color="1F4E78", fill_type="solid")
    header_font = Font(color="FFFFFF", bold=True)
    for cell in ws[1]:
        cell.fill = header_fill
        cell.font = header_font
        cell.alignment = Alignment(horizontal="center", vertical="center")
        
    for i, row in enumerate(meta_rows, start=1):
        pk = row.get("primary_keywords", "")
        if isinstance(pk, list):
            pk = ", ".join(pk)
        ws.append([i, row.get("page_name", ""), row.get("url", ""),
                   row.get("meta_title", ""), row.get("meta_description", ""),
                   row.get("h1", ""), pk, row.get("search_intent", "")])
                   
    # Auto-adjust column widths and wrap text
    for col in ws.columns:
        max_length = 0
        column = col[0].column_letter
        for cell in col:
            try:
                if len(str(cell.value)) > max_length:
                    max_length = len(str(cell.value))
            except:
                pass
            cell.alignment = Alignment(wrap_text=True, vertical="top")
        
        adjusted_width = max_length + 2
        if adjusted_width > 50: 
            adjusted_width = 50  # Cap width so descriptions don't make the column infinite
        ws.column_dimensions[column].width = adjusted_width

    buf = io.BytesIO()
    wb.save(buf)
    return buf.getvalue()

def render_html_zip(html_pages: dict) -> bytes:
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as zf:
        for filename, content in html_pages.items():
            zf.writestr(filename, content)
    return buf.getvalue()

st.title("✨ Grovuu SEO Plan Generator")
st.markdown("Upload the client brief, add anything extra, get your Strategy, Meta Data, and HTML content.")

# Initialize session state for generated files
if "docx_buffer" not in st.session_state:
    st.session_state.docx_buffer = None
if "xlsx_buffer" not in st.session_state:
    st.session_state.xlsx_buffer = None
if "zip_buffer" not in st.session_state:
    st.session_state.zip_buffer = None
if "plan_data" not in st.session_state:
    st.session_state.plan_data = None
if "issues" not in st.session_state:
    st.session_state.issues = None

st.divider()

with st.container():
    with st.form("generation_form", border=True):
        st.subheader("1. Provide Input")
        uploaded = st.file_uploader("Client brief document", type=["docx", "pdf", "txt", "md"], help="Supported formats: DOCX, PDF, TXT, MD")
        extra_requirements = st.text_area("Extra requirements (optional)", height=100)
        
        submitted = st.form_submit_button("Generate Outputs", type="primary", use_container_width=True)

if submitted:
    # Clear previous results
    st.session_state.docx_buffer = None
    st.session_state.xlsx_buffer = None
    st.session_state.zip_buffer = None
    st.session_state.plan_data = None
    st.session_state.issues = None

    if not uploaded:
        st.error("⚠️ Please upload a client brief before generating.")
    else:
        try:
            with st.status("Processing your request...", expanded=True) as status:
                st.write("📄 Extracting text from document...")
                brief_text = extract_text(uploaded)
                
                st.write("🧠 Research Pass: Analyzing market & strategy (this takes a few minutes)...")
                research_memo = research_pass(brief_text, extra_requirements)
                
                st.write("🧩 Assembly Pass: Structuring the strategy into templates...")
                plan = assembly_pass(brief_text, research_memo)
                
                st.write("✅ Validating output quality...")
                issues = validate_plan(plan)
                
                st.write("🌐 Content Pass: Generating Developer HTML for Top 5 Pages...")
                html_pages = content_pass(brief_text, plan)
                
                st.write("🛠️ Creating Word, Excel, and ZIP output files...")
                st.session_state.docx_buffer = render_docx(plan)
                st.session_state.xlsx_buffer = render_excel_meta(plan.get("meta", []))
                st.session_state.zip_buffer = render_html_zip(html_pages)
                st.session_state.plan_data = plan
                st.session_state.issues = issues
                
                status.update(label="Generation Complete!", state="complete", expanded=False)
        except Exception as e:
            st.error(f"❌ An error occurred: {e}")

if st.session_state.docx_buffer and st.session_state.xlsx_buffer and st.session_state.zip_buffer:
    st.divider()
    
    if st.session_state.issues:
        st.warning("⚠️ Quality check flagged some issues — review before sending:")
        for issue in st.session_state.issues:
            st.write(f"- {issue}")
    else:
        st.success("✅ Done! No quality issues flagged. Download both files below.")

    st.subheader("🎉 2. Download Your Files")
    
    plan = st.session_state.plan_data
    safe_name = plan.get('business_name', 'SEO_Strategy').replace(" ", "_")
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.download_button(
            label="📄 SEO Strategy (.docx)",
            data=st.session_state.docx_buffer,
            file_name=f"{safe_name}_strategy.docx",
            mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            use_container_width=True,
            type="primary"
        )
    with col2:
        st.download_button(
            label="📊 Meta Data (.xlsx)",
            data=st.session_state.xlsx_buffer,
            file_name=f"{safe_name}_meta_data.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            use_container_width=True,
            type="primary"
        )
    with col3:
        st.download_button(
            label="🖥️ Developer HTML (.zip)",
            data=st.session_state.zip_buffer,
            file_name=f"{safe_name}_html_content.zip",
            mime="application/zip",
            use_container_width=True,
            type="primary"
        )
