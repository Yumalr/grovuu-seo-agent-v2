"""Grovuu SEO Agent v2 — Evidence-based SEO Agent with chat interface.

Architecture:
  User -> Chat interface -> Gemini (with SEO Skill system prompt)
       -> MCP evidence tools (inspect_page, etc.)
       -> Structured findings with evidence status labels
       -> Downloadable HTML/DOCX/XLSX reports
"""

import io
import json
import os
import time
import zipfile
import pickle

import streamlit as st
from google import genai
from google.genai import types

from agent.prompts import build_system_prompt
from agent.core import TOOL_DECLARATIONS, execute_tool_call
from agent.strategy import (
    assembly_pass,
    validate_plan,
    content_pass,
)
from reports.html_report import generate_audit_report
from reports.strategy_docx import render_docx
from reports.meta_xlsx import render_excel_meta
from utils import extract_text


# ──────────────────────────────────────────────────────────────────
# Page config
# ──────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Grovuu SEO Agent",
    page_icon="🔍",
    layout="wide",
)

st.markdown(
    """
<style>
    [data-testid="stSidebar"] { min-width: 320px; }
    .stChatMessage { max-width: 900px; }
    div[data-testid="stStatusWidget"] { max-width: 900px; }
</style>
""",
    unsafe_allow_html=True,
)


# ──────────────────────────────────────────────────────────────────
# API key + client
# ──────────────────────────────────────────────────────────────────
api_key = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
if not api_key:
    try:
        api_key = st.secrets.get("GEMINI_API_KEY") or st.secrets.get("GOOGLE_API_KEY")
    except Exception:
        pass
if not api_key:
    st.error("Set GEMINI_API_KEY (or GOOGLE_API_KEY) in your environment or .streamlit/secrets.toml")
    st.stop()

MODEL_NAME = os.getenv("GEMINI_MODEL", "gemini-3.8-flash")


@st.cache_resource
def get_client():
    return genai.Client(api_key=api_key)


@st.cache_resource
def get_system_prompt():
    return build_system_prompt()


client = get_client()
system_prompt = get_system_prompt()


# ──────────────────────────────────────────────────────────────────
# Session state
# ──────────────────────────────────────────────────────────────────
STATE_FILE = "chat_history.pkl"

defaults = {
    "messages": [],           # Display history: [{"role": ..., "content": ...}]
    "genai_history": [],      # Gemini Content history for context continuity
    "last_inspection": None,  # Last inspect_page result for report download
    "uploaded_text": None,
    "uploaded_filename": None,
    "needs_response": False,
    "strategy_docx": None,
    "strategy_xlsx": None,
    "strategy_zip": None,
    "_run_strategy": False,
}

def save_state():
    state_to_save = {k: st.session_state[k] for k in defaults.keys()}
    try:
        with open(STATE_FILE, "wb") as f:
            pickle.dump(state_to_save, f)
    except Exception as e:
        print(f"Could not save state: {e}")

if "messages" not in st.session_state:
    if os.path.exists(STATE_FILE):
        try:
            with open(STATE_FILE, "rb") as f:
                loaded = pickle.load(f)
            for k, v in loaded.items():
                st.session_state[k] = v
        except Exception:
            for key, val in defaults.items():
                st.session_state[key] = val
    else:
        for key, val in defaults.items():
            st.session_state[key] = val
else:
    for key, val in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = val


# ──────────────────────────────────────────────────────────────────
# Sidebar
# ──────────────────────────────────────────────────────────────────
with st.sidebar:
    st.title("🔍 Grovuu SEO Agent")
    st.caption("Evidence-based SEO analysis, strategy, and implementation")

    st.divider()

    # --- Quick Inspect ---
    st.subheader("🌐 Inspect a Page")
    inspect_url = st.text_input(
        "URL", placeholder="https://example.com/page", label_visibility="collapsed",
    )
    if st.button("Inspect Page", use_container_width=True, type="primary"):
        if inspect_url:
            st.session_state.messages.append(
                {"role": "user", "content": f"Run a full on-page SEO audit on this URL: {inspect_url}"}
            )
            st.session_state.needs_response = True
            save_state()
            st.rerun()
        else:
            st.warning("Enter a URL first.")

    st.divider()

    # --- File Upload ---
    st.subheader("📄 Upload Document")
    uploaded = st.file_uploader(
        "Client brief, GSC export, or crawl data",
        type=["docx", "pdf", "txt", "md"],
        label_visibility="collapsed",
    )
    if uploaded:
        if st.session_state.uploaded_filename != uploaded.name:
            try:
                text = extract_text(uploaded)
                st.session_state.uploaded_text = text
                st.session_state.uploaded_filename = uploaded.name
                save_state()
                st.success(f"Loaded: {uploaded.name} ({len(text):,} chars)")
            except Exception as e:
                st.error(f"Could not read file: {e}")
        else:
            st.info(f"Loaded: {uploaded.name}")

    if st.session_state.uploaded_text:
        col_a, col_b = st.columns(2)
        with col_a:
            if st.button("📋 Strategy", use_container_width=True, help="Generate full SEO strategy"):
                brief_preview = st.session_state.uploaded_text[:2000]
                st.session_state.messages.append(
                    {"role": "user", "content": f"Generate a comprehensive SEO strategy from this client brief:\n\n{brief_preview}..."}
                )
                st.session_state.needs_response = True
                st.session_state._run_strategy = True
                save_state()
                st.rerun()
        with col_b:
            if st.button("💬 Discuss", use_container_width=True, help="Ask about the uploaded document"):
                brief_preview = st.session_state.uploaded_text[:2000]
                st.session_state.messages.append(
                    {"role": "user", "content": f"I have uploaded a client document. Here is the content for context:\n\n{brief_preview}\n\n...What questions should we address first?"}
                )
                st.session_state.needs_response = True
                save_state()
                st.rerun()

    st.divider()

    # --- Downloads ---
    st.subheader("📊 Downloads")
    has_downloads = False

    if st.session_state.last_inspection:
        has_downloads = True
        report_html = generate_audit_report(st.session_state.last_inspection)
        st.download_button(
            "🔍 HTML Audit Report",
            data=report_html, file_name="seo_audit_report.html",
            mime="text/html", use_container_width=True,
        )

    if st.session_state.strategy_docx:
        has_downloads = True
        st.download_button(
            "📄 Strategy (.docx)",
            data=st.session_state.strategy_docx, file_name="seo_strategy.docx",
            mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            use_container_width=True,
        )

    if st.session_state.strategy_xlsx:
        has_downloads = True
        st.download_button(
            "📊 Meta Data (.xlsx)",
            data=st.session_state.strategy_xlsx, file_name="seo_meta_data.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            use_container_width=True,
        )

    if st.session_state.strategy_zip:
        has_downloads = True
        st.download_button(
            "🖥️ HTML Pages (.zip)",
            data=st.session_state.strategy_zip, file_name="seo_html_content.zip",
            mime="application/zip", use_container_width=True,
        )

    if not has_downloads:
        st.caption("Reports will appear here after analysis.")

    st.divider()

    if st.button("🗑️ New Conversation", use_container_width=True):
        if os.path.exists(STATE_FILE):
            os.remove(STATE_FILE)
        for key, val in defaults.items():
            st.session_state[key] = val if not isinstance(val, list) else []
        st.rerun()


# ──────────────────────────────────────────────────────────────────
# Chat display
# ──────────────────────────────────────────────────────────────────
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# Welcome message
if not st.session_state.messages:
    with st.chat_message("assistant"):
        st.markdown("Ready. Paste a URL below to begin an audit, or upload a brief in the sidebar to generate a strategy.")


# ──────────────────────────────────────────────────────────────────
# Response generation
# ──────────────────────────────────────────────────────────────────

def _run_strategy_pipeline():
    """Run the full strategy generation pipeline."""
    brief = st.session_state.uploaded_text
    if not brief:
        return "No client brief uploaded. Please upload a document in the sidebar."

    with st.status("Generating SEO strategy...", expanded=True) as status:
        st.write("🧠 Strategy pass: analyzing brief and structuring plan...")
        plan = assembly_pass(client, MODEL_NAME, brief)

        st.write("✅ Validating output quality...")
        issues = validate_plan(plan)

        st.write("🌐 Content pass: generating HTML for top 3 pages...")
        html_pages = content_pass(client, MODEL_NAME, brief, plan)

        st.write("📦 Packaging deliverables...")
        st.session_state.strategy_docx = render_docx(plan)
        st.session_state.strategy_xlsx = render_excel_meta(plan.get("meta", []))

        buf = io.BytesIO()
        with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as zf:
            for filename, content in html_pages.items():
                zf.writestr(filename, content)
        st.session_state.strategy_zip = buf.getvalue()

        status.update(label="Strategy complete!", state="complete", expanded=False)

    result = f"**SEO strategy generated for {plan.get('business_name', 'the client')}.**\n\n"
    if issues:
        result += "⚠️ **Quality checks flagged:**\n"
        for issue in issues:
            result += f"- {issue}\n"
        result += "\n"
    result += (
        f"**Deliverables ready** (download from sidebar):\n"
        f"- 📄 Strategy document (.docx)\n"
        f"- 📊 Meta data sheet (.xlsx) with {len(plan.get('meta', []))} pages\n"
        f"- 🖥️ HTML content (.zip) with {len(html_pages)} pages\n\n"
        f"**Pages planned:** {len(plan.get('pages', []))}\n"
        f"**ICPs identified:** {len(plan.get('icps', []))}\n\n"
        f"You can now ask me questions about the strategy, request changes, or proceed with implementation."
    )
    return result


def generate_with_retry_chat(client, model_name, history, config, retries=5):
    """Wrapper to handle 503s and pace chat requests."""
    for attempt in range(retries):
        try:
            time.sleep(4.5) # Enforce 15 RPM limit
            return client.models.generate_content(
                model=model_name,
                contents=history,
                config=config,
            )
        except Exception as e:
            error_str = str(e)
            if attempt < retries - 1 and any(code in error_str for code in ["429", "503", "UNAVAILABLE"]):
                sleep_time = 15 * (attempt + 1)
                st.toast(f"Model busy (503/429). Retrying in {sleep_time}s...", icon="⏳")
                time.sleep(sleep_time)
            else:
                raise

def _generate_response(user_message: str) -> str:
    """Generate a response with tool calling and UI feedback."""

    # Strategy pipeline
    if st.session_state._run_strategy:
        st.session_state._run_strategy = False
        return _run_strategy_pipeline()

    # Build config
    config = types.GenerateContentConfig(
        system_instruction=system_prompt,
        tools=TOOL_DECLARATIONS,
    )

    # Add user message to genai history
    st.session_state.genai_history.append(
        types.Content(role="user", parts=[types.Part.from_text(text=user_message)])
    )

    # Call Gemini
    response = generate_with_retry_chat(client, MODEL_NAME, st.session_state.genai_history, config)

    # Handle function calls in a loop
    for _ in range(5):
        function_calls = []
        try:
            if response.candidates and response.candidates[0].content:
                for part in response.candidates[0].content.parts:
                    if part.function_call and part.function_call.name:
                        function_calls.append(part)
        except (IndexError, AttributeError):
            break

        if not function_calls:
            break

        # Record model response in history
        st.session_state.genai_history.append(response.candidates[0].content)

        # Execute tools with status display
        response_parts = []
        for fc_part in function_calls:
            fc = fc_part.function_call
            args = dict(fc.args) if fc.args else {}
            tool_url = args.get("url", "page")

            with st.status(f"🔍 Inspecting {tool_url}...", expanded=True) as status:
                st.write("Fetching server HTML and extracting SEO evidence...")
                try:
                    result = execute_tool_call(fc)
                    if fc.name == "inspect_page" and "error" not in result:
                        st.session_state.last_inspection = result
                        wc = result.get("content", {}).get("serverHtmlWordCount", "?")
                        lc = result.get("links", {}).get("internalCount", "?")
                        st.write(f"Found {wc} words, {lc} internal links")
                    status.update(label=f"✅ Inspected {tool_url}", state="complete", expanded=False)
                except Exception as e:
                    result = {"error": str(e)}
                    status.update(label=f"❌ Failed: {tool_url}", state="error", expanded=False)

            response_parts.append(
                types.Part.from_function_response(
                    name=fc.name,
                    response={"result": json.dumps(result, default=str)},
                )
            )

        # Send tool results back
        st.session_state.genai_history.append(
            types.Content(role="user", parts=response_parts)
        )
        response = generate_with_retry_chat(client, MODEL_NAME, st.session_state.genai_history, config)

    # Record final response
    if response.candidates and response.candidates[0].content:
        st.session_state.genai_history.append(response.candidates[0].content)

    try:
        return response.text
    except Exception:
        return "Analysis complete but I could not generate a text summary. Please try rephrasing your request."


# ──────────────────────────────────────────────────────────────────
# Process pending response
# ──────────────────────────────────────────────────────────────────
if st.session_state.needs_response and st.session_state.messages:
    st.session_state.needs_response = False
    last_msg = st.session_state.messages[-1]

    if last_msg["role"] == "user":
        with st.chat_message("assistant"):
            try:
                response_text = _generate_response(last_msg["content"])
                st.markdown(response_text)
                st.session_state.messages.append({"role": "assistant", "content": response_text})
            except Exception as e:
                error_text = f"❌ Error: {e}"
                st.error(error_text)
                st.session_state.messages.append({"role": "assistant", "content": error_text})
        save_state()
        st.rerun()

# Chat input
if prompt := st.chat_input("Ask anything about SEO, or paste a URL to audit..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    st.session_state.needs_response = True
    save_state()
    st.rerun()
