"""Verify the full new-SDK import chain works."""
import sys
sys.stdout.reconfigure(encoding="utf-8")
sys.path.insert(0, ".")

print("Testing google.genai imports...")
from google import genai
from google.genai import types
print(f"  genai version: {genai.__version__}")

print("\nTesting agent.core imports...")
from agent.core import TOOL_DECLARATIONS, execute_tool_call
print(f"  Tool declarations: {len(TOOL_DECLARATIONS)} tools")
print(f"  Tool name: {TOOL_DECLARATIONS[0].function_declarations[0].name}")

print("\nTesting agent.prompts...")
from agent.prompts import build_system_prompt
prompt = build_system_prompt()
print(f"  System prompt: {len(prompt):,} chars")

print("\nTesting agent.strategy...")
from agent.strategy import research_pass, assembly_pass, validate_plan, content_pass
print("  All strategy functions imported")

print("\nTesting mcp_tools.inspect_page...")
from mcp_tools.inspect_page import inspect_page
result = inspect_page("https://example.com")
print(f"  inspect_page returned: {result['http']['status']} status")
print(f"  Title: {result['metadata']['title']}")
print(f"  Evidence: {result['evidenceStatus']}")

print("\nTesting reports...")
from reports.html_report import generate_audit_report
report = generate_audit_report(result)
print(f"  HTML report: {len(report):,} chars")

from reports.strategy_docx import render_docx
from reports.meta_xlsx import render_excel_meta
print("  DOCX and XLSX modules imported")

print("\nTesting utils...")
from utils import extract_text
print("  extract_text imported")

print("\n" + "=" * 50)
print("ALL IMPORTS AND BASIC TESTS PASSED!")
print("=" * 50)
