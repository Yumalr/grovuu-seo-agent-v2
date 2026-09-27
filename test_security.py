"""Test SSRF protection."""
import sys
sys.stdout.reconfigure(encoding="utf-8")
sys.path.insert(0, ".")

from mcp_tools.security import validate_url, SSRFError

tests = [
    ("http://localhost", True),
    ("http://127.0.0.1/admin", True),
    ("http://192.168.1.1", True),
    ("ftp://evil.com", True),
    ("https://example.com", False),
]

errors = 0
for url, should_block in tests:
    try:
        validate_url(url)
        if should_block:
            print(f"FAIL: {url} should have been blocked")
            errors += 1
        else:
            print(f"PASS: {url} allowed")
    except SSRFError as e:
        if not should_block:
            print(f"FAIL: {url} should NOT have been blocked: {e}")
            errors += 1
        else:
            print(f"PASS: {url} blocked - {e}")

print()
if errors == 0:
    print("All SSRF tests passed!")
else:
    print(f"{errors} tests FAILED")

# Test the full import chain
print()
print("Testing import chain...")
from agent.prompts import build_system_prompt
prompt = build_system_prompt()
print(f"System prompt loaded: {len(prompt):,} chars")

from agent.core import TOOL_DECLARATIONS
print(f"Tool declarations: {len(TOOL_DECLARATIONS)} tools")

from reports.html_report import generate_audit_report
print("HTML report module: OK")

from reports.strategy_docx import render_docx
print("DOCX report module: OK")

from reports.meta_xlsx import render_excel_meta
print("XLSX report module: OK")

print()
print("All imports OK!")
